from __future__ import annotations

import logging
import re
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Optional

from ... import utils
from ..._const import VDF_LOADS
from ...errors import HTTPException
from ...game import TF2, Game
from ...models import register
from ...protobufs import GCMsgProto
from .._gc.state import GCState as GCState_
from .backpack import Backpack
from .enums import ItemFlags, ItemOrigin, Language
from .protobufs import base, sdk, struct_messages

if TYPE_CHECKING:
    from multidict import MultiDict

    from .client import Client
    from .types.schema import Schema


log = logging.getLogger(__name__)
SCHEMA: Schema


class GCState(GCState_):
    gc_parsers: dict[Language, Callable[..., Any]]
    Language = Language
    client: Client
    backpack: Backpack
    crafted_items: set[tuple[int, ...]]

    def __init__(self, client: Client, **kwargs: Any):
        super().__init__(client, **kwargs)
        self.schema: Schema
        self.language: Optional[MultiDict] = None
        self.backpack_slots: Optional[int] = None
        self._is_premium: Optional[bool] = None
        self.crafted_items: set[tuple[int, ...]] = set()

        language = kwargs.get("language")
        if language is not None:
            client.set_language(language)

    @register(Language.ClientWelcome)
    def parse_gc_client_connect(self, _) -> None:
        if not self._gc_connected.is_set():
            self.dispatch("gc_connect")
            self._gc_connected.set()

    @register(Language.ClientGoodbye)
    def parse_client_goodbye(self, _=None) -> None:
        self.dispatch("gc_disconnect")
        self._gc_connected.clear()

    # TODO maybe stuff for servers?

    @register(Language.UpdateItemSchema)
    async def parse_schema(self, msg: GCMsgProto[base.UpdateItemSchema]) -> None:
        log.info(f"Getting TF2 item schema at {msg.body.items_game_url}")
        try:
            resp = await self.http._session.get(msg.body.items_game_url)
        except Exception as exc:
            return log.error("Failed to get item schema", exc_info=exc)

        global SCHEMA
        self.schema = SCHEMA = (await utils.to_thread(VDF_LOADS, await resp.text()))["items_game"]  # type: ignore
        log.info("Loaded schema")

    @register(Language.SystemMessage)
    def parse_system_message(self, msg: GCMsgProto[base.SystemBroadcast]) -> None:
        self.dispatch("system_message", msg.body.message)

    @register(Language.ClientDisplayNotification)
    def parse_client_notification(self, msg: GCMsgProto[base.ClientDisplayNotification]) -> None:
        if self.language is None:
            return

        title = self.language[msg.body.notification_title_localization_key[1:]]
        text = re.sub(r"[\u0001|\u0002]", "", self.language[msg.body.notification_body_localization_key[1:]])
        for i, replacement in enumerate(msg.body.body_substring_values):
            if replacement[0] == "#":
                replacement = self.language[replacement[1:]]
            text = text.replace(f"%{msg.body.body_substring_keys[i]}%", replacement)
        self.dispatch("display_notification", title, text)

    @register(Language.CraftResponse)
    async def parse_crafting_response(self, msg: GCMsgProto[struct_messages.CraftResponse]) -> None:
        # this is called after item_receive so no fetching is necessary
        if msg.body.id_list:  # only empty if crafting failed
            self.crafted_items.add(msg.body.id_list)

    @register(Language.SOCacheSubscriptionCheck)
    async def parse_cache_check(self, _=None) -> None:
        log.debug("Requesting SO cache subscription refresh")
        msg = GCMsgProto(Language.SOCacheSubscriptionRefresh, owner=self.client.user.id64)
        await self.ws.send_gc_message(msg)

    async def update_backpack(self, *cso_items: base.Item, is_cache_subscribe: bool = False) -> None:
        await self.client.wait_until_ready()

        backpack = self.backpack or await self.fetch_backpack(Backpack)
        item_ids = [item.asset_id for item in backpack]

        if any(cso_item.id not in item_ids for cso_item in cso_items):
            try:
                await backpack.update()
            except HTTPException:
                pass

            item_ids = [item.asset_id for item in backpack]

            if any(cso_item.id not in item_ids for cso_item in cso_items):
                await self.restart_tf2()
                await backpack.update()  # if the item still isn't here something on valve's end has broken

        for cso_item in cso_items:  # merge the two items
            item = utils.get(backpack, asset_id=cso_item.id)
            if item is None:
                continue  # the item has been removed (gc sometimes sends you items that you have crafted/deleted)
            for attribute_name in cso_item.__annotations__:
                setattr(item, attribute_name, getattr(cso_item, attribute_name))

            is_new = is_cache_subscribe and (cso_item.inventory >> 30) & 1
            item.position = 0 if is_new else cso_item.inventory & 0xFFFF
            item.flags = ItemFlags.try_value(cso_item.flags)
            item.origin = ItemOrigin.try_value(cso_item.origin)

        self.backpack = backpack

    @register(Language.SOCacheSubscribed)
    async def parse_cache_subscribe(self, msg: GCMsgProto[sdk.CacheSubscribed]) -> None:
        for object in msg.body.objects:
            if object.type_id == 1:  # backpack
                await self.update_backpack(
                    *(base.Item().parse(item_data) for item_data in object.object_data),
                    is_cache_subscribe=True,
                )
            elif object.type_id == 7:  # account metadata
                proto = base.GameAccountClient().parse(object.object_data[0])
                self._is_premium = not proto.trial_account
                self.backpack_slots = (50 if proto.trial_account else 300) + proto.additional_backpack_slots
        if self._gc_connected.is_set():
            self._gc_ready.set()
            self.dispatch("gc_ready")

    @register(Language.SOCreate)
    async def parse_item_add(self, msg: GCMsgProto[sdk.SingleObject]) -> None:
        if msg.body.type_id != 1 or not self.backpack:
            return

        cso_item = base.Item().parse(msg.body.object_data)
        await self.update_backpack(cso_item)
        item = utils.get(self.backpack, id=cso_item.id)
        if item is None:  # protect from a broken item
            return
        self.dispatch("item_receive", item)

        for item_set in self.crafted_items.copy():
            items = [utils.get(self.backpack, asset_id=item_id) for item_id in item_set]
            if all(items):
                self.dispatch("crafting_complete", items)
                self.crafted_items.discard(item_set)

    @utils.call_once
    async def restart_tf2(self) -> None:
        await self.client.change_presence(game=Game(id=0))
        self.parse_client_goodbye()
        await self.client.change_presence(game=TF2, games=self.client._original_games)
        await self._gc_connected.wait()

    @register(Language.SOUpdate)
    async def handle_so_update(self, msg: GCMsgProto[sdk.SingleObject]) -> None:
        await self._handle_so_update(msg.body)

    @register(Language.SOUpdateMultiple)
    async def handle_multiple_so_update(self, msg: GCMsgProto[sdk.MultipleObjects]) -> None:
        for item in msg.body.objects:
            await self._handle_so_update(item)  # type: ignore  # TODO use a Protocol here

    async def _handle_so_update(self, object: sdk.SingleObject) -> None:
        if object.type_id == 1:
            if not self.backpack:
                return

            cso_item = base.Item().parse(object.object_data)

            old_item = utils.get(self.backpack, asset_id=cso_item.id)
            if old_item is None:  # broken item
                return
            await self.update_backpack(cso_item)
            new_item = utils.get(self.backpack, id=cso_item.id)
            if new_item is None:
                return

            self.dispatch("item_update", old_item, new_item)
        elif object.type_id == 7:
            proto = base.GameAccountClient().parse(object.object_data)
            backpack_slots = (50 if proto.trial_account else 300) + proto.additional_backpack_slots
            if proto.trial_account == self._is_premium or self.backpack_slots != backpack_slots:
                self._is_premium = not proto.trial_account
                self.backpack_slots = backpack_slots
                self.dispatch("account_update")
        else:
            log.debug(f"Unknown item {object!r} updated")

    @register(Language.SODestroy)
    async def handle_item_remove(self, msg: GCMsgProto[sdk.SingleObject]) -> None:
        if msg.body.type_id != 1 or not self.backpack:
            return

        deleted_item = base.Item().parse(msg.body.object_data)
        item = utils.get(self.backpack, asset_id=deleted_item.id)
        if item is None:  # broken item
            return
        for attribute_name in deleted_item.__annotations__:
            setattr(item, attribute_name, getattr(deleted_item, attribute_name))
        self.backpack.items.remove(item)  # type: ignore
        self.dispatch("item_remove", item)
