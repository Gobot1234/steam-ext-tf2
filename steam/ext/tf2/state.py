# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
import logging
import re
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Optional

from multidict import MultiDict

from ... import utils
from ...game import TF2, Game
from ...models import EventParser, register
from ...protobufs import EMsg, GCMsg, GCMsgProto, MsgProto
from ...state import ConnectionState
from ...trade import Inventory
from .backpack import BackPack, BackPackItem
from .enums import Language
from .protobufs import base_gcmessages as cso_messages, gcsdk_gcmessages as so_messages, struct_messages
from .protobufs.struct_messages import UpdateMultipleItems

if TYPE_CHECKING:
    from ...protobufs.steammessages_clientserver_2 import CMsgGcClient
    from .client import Client

log = logging.getLogger(__name__)


class GCState(ConnectionState):
    gc_parsers: dict[Language, EventParser[Language]] = {}
    client: Client

    __slots__ = (
        "schema",
        "language",
        "backpack",
        "backpack_slots",
        "_unpatched_inventory",
        "_is_premium",
        "_connected",
    )

    def __init__(self, client: Client, **kwargs: Any):
        super().__init__(client, **kwargs)
        self.schema: Optional[MultiDict] = None
        self.language: Optional[MultiDict] = None
        self.backpack_slots: Optional[int] = None
        self._unpatched_inventory: Optional[Callable[[Game], Coroutine[None, None, Inventory]]] = None
        self._is_premium: Optional[bool] = None
        self._connected = asyncio.Event()
        self._gc_ready = asyncio.Event()

        language = kwargs.get("language")
        if language is not None:
            client.set_language(language)

    @register(EMsg.ClientFromGC)
    async def parse_gc_message(self, msg: MsgProto[CMsgGcClient]) -> None:
        if msg.body.appid != self.client.GAME.id:
            return

        try:
            language = Language(utils.clear_proto_bit(msg.body.msgtype))
        except ValueError:
            return log.info(
                f"Ignoring unknown msg type: {msg.body.msgtype} ({utils.clear_proto_bit(msg.body.msgtype)})"
            )

        try:
            msg = (
                GCMsgProto(language, msg.body.payload)
                if utils.is_proto(msg.body.msgtype)
                else GCMsg(language, msg.body.payload)
            )
        except Exception as exc:
            if language == language.SOCacheSubscriptionCheck:
                # This payload is commonly malformed
                return await self.parse_cache_check()
            return log.error(f"Failed to deserialize message: {language!r}, {msg.body.payload!r}", exc_info=exc)
        else:
            if log.isEnabledFor(logging.DEBUG):
                log.debug(f"Socket has received GC message {msg!r} from the websocket.")

        self.dispatch("gc_message_receive", msg)

        try:
            func = self.gc_parsers[language]
        except KeyError:
            if log.isEnabledFor(logging.DEBUG):
                log.debug(f"Ignoring event {msg!r}")
        else:
            await utils.maybe_coroutine(func, msg)

    @register(Language.ClientWelcome)
    def parse_gc_client_connect(self, _) -> None:
        if not self._connected.is_set():
            self.dispatch("gc_connect")
            self._connected.set()

    @register(Language.ClientGoodbye)
    def parse_client_goodbye(self, _=None) -> None:
        self.dispatch("gc_disconnect")
        self._connected.clear()

    # TODO maybe stuff for servers?

    @register(Language.UpdateItemSchema)
    async def parse_schema(self, msg: GCMsgProto[cso_messages.CMsgUpdateItemSchema]) -> None:
        log.info(f"Getting TF2 item schema at {msg.body.items_game_url}")
        try:
            resp = await self.http._session.get(msg.body.items_game_url)
        except Exception as exc:
            return log.error("Failed to get item schema", exc_info=exc)

        from . import VDF_DECODER  # circular import

        self.schema = VDF_DECODER(await resp.text())["items_game"]
        log.info("Loaded schema")

    @register(Language.SystemMessage)
    def parse_system_message(self, msg: GCMsgProto[cso_messages.CMsgSystemBroadcast]) -> None:
        self.dispatch("system_message", msg.body.message)

    @register(Language.ClientDisplayNotification)
    def parse_client_notification(self, msg: GCMsgProto[cso_messages.CMsgGcClientDisplayNotification]) -> None:
        if self.language is None:
            return

        title = self.language[msg.body.notification_title_localization_key[1:]]
        text = re.sub(r"[\u0001|\u0002]", "", self.language[msg.body.notification_body_localization_key[1]])
        for i, replacement in enumerate(msg.body.body_substring_values):
            if replacement[0] == "#":
                replacement = self.language[replacement[1:]]
            text = text.replace(f"%{msg.body.body_substring_keys[i]}%", replacement)
        self.dispatch("display_notification", title, text)

    @register(Language.CraftResponse)
    def parse_crafting_response(self, msg: GCMsg[struct_messages.CraftResponse]) -> None:
        # this is called after item_receive so no fetching is necessary
        if msg.body.id_list:  # only empty if crafting failed
            self.dispatch(
                "crafting_complete",
                *(utils.find(lambda i: i.asset_id == item_id, self.backpack) for item_id in msg.body.id_list),
            )

    @register(Language.SOCacheSubscriptionCheck)
    async def parse_cache_check(self, _=None) -> None:
        log.debug("Requesting SO cache subscription refresh")
        msg = GCMsgProto(Language.SOCacheSubscriptionRefresh, owner=self.client.user.id64)
        await self.ws.send_gc_message(msg)

    def patch_user_inventory(self, new_inventory: Inventory) -> None:
        async def inventory(_, game: Game) -> Inventory:
            if game != TF2:
                return await self._unpatched_inventory(game)

            return new_inventory

        self.client.user.__class__.inventory = inventory

    async def update_backpack(self, *items: cso_messages.CsoEconItem) -> BackPack:
        await self.client.wait_until_ready()
        backpack = BackPack(await self._unpatched_inventory(TF2))
        for item in backpack:
            for backpack_item in items:
                if item.asset_id == backpack_item.id:
                    for attribute_name in backpack_item.__annotations__:
                        setattr(item, attribute_name, getattr(backpack_item, attribute_name))
                    break

        self.patch_user_inventory(backpack)
        self.backpack = backpack
        return backpack

    @register(Language.SOCacheSubscribed)
    async def parse_cache_subscribe(self, msg: GCMsg[so_messages.CMsgSOCacheSubscribed]) -> None:
        for cache in msg.body.objects:
            if cache.type_id == 1:  # backpack
                items = [cso_messages.CsoEconItem().parse(item_data) for item_data in cache.object_data]
                for item in await self.update_backpack(*items):
                    is_new = (item.inventory >> 30) & 1
                    item.position = 0 if is_new else item.inventory & 0xFFFF
            elif cache.type_id == 7:  # account metadata
                proto = cso_messages.CsoEconGameAccountClient().parse(cache.object_data[0])
                self._is_premium = not proto.trial_account
                self.backpack_slots = (50 if proto.trial_account else 300) + proto.additional_backpack_slots
        if self._connected.is_set():
            self._gc_ready.set()
            self.dispatch("gc_ready")

    @register(Language.SOCreate)
    async def parse_item_add(self, msg: GCMsg[so_messages.CMsgSOSingleObject]) -> None:
        if msg.body.type_id != 1 or not self.backpack:
            return

        received_item = cso_messages.CsoEconItem().parse(msg.body.object_data)
        item = utils.find(lambda i: i.asset_id == received_item.id, await self.update_backpack(received_item))

        if item is None:
            await self.restart_tf2()  # steam doesn't add the item to your api inventory until you restart tf2
            return await self.parse_item_add(msg)

        item.position = item.inventory & 0x0000FFFF
        self.dispatch("item_receive", item)

    async def restart_tf2(self) -> None:
        await self.client.change_presence(game=Game(id=0))
        self.parse_client_goodbye()
        await self.client.change_presence(game=TF2, games=self.client._original_games)

    @register(Language.SOUpdate)
    async def handle_so_update(self, msg: GCMsgProto[so_messages.CMsgSOSingleObject]) -> None:
        await self._handle_so_update(msg.body)

    @register(Language.SOUpdateMultiple)
    async def handle_multiple_so_update(self, msg: GCMsgProto[so_messages.CMsgSOMultipleObjects]) -> None:
        try:
            type_id = msg.body.objects[0].type_id
        except IndexError:
            pass  # would be weird
        else:
            if type_id == 1:
                msg.body = UpdateMultipleItems().parse(msg.payload)  # discard the message cause my word it's broke
        for item in msg.body.objects:
            await self._handle_so_update(item)

    async def _handle_so_update(self, item: so_messages.CMsgSOSingleObject) -> None:
        if item.type_id == 1:
            if not self.backpack:
                return
            received_item: cso_messages.CsoEconItem = item.inner

            def check(item: BackPackItem) -> bool:
                return item.asset_id == int(received_item.id)

            old_item = utils.find(check, self.backpack)
            new_item = utils.find(check, await self.update_backpack(received_item))
            new_item.position = item.inventory & 0x0000FFFF
            self.dispatch("item_update", old_item, new_item)
        elif item.type_id == 7:
            proto = cso_messages.CsoEconGameAccountClient().parse(item.object_data)
            backpack_slots = (50 if proto.trial_account else 300) + proto.additional_backpack_slots
            if proto.trial_account == self._is_premium or self.backpack_slots != backpack_slots:
                self._is_premium = not proto.trial_account
                self.backpack_slots = backpack_slots
                self.dispatch("account_update")
        else:
            log.debug(f"Unknown item {item!r} updated")

    @register(Language.SODestroy)
    async def handle_item_remove(self, msg: GCMsgProto[so_messages.CMsgSOSingleObject]) -> None:
        if msg.body.type_id != 1 or not self.backpack:
            return

        deleted_item = cso_messages.CsoEconItem().parse(msg.body.object_data)
        for item in self.backpack:
            if item.asset_id == deleted_item.id:
                for attribute_name in deleted_item.__annotations__:
                    setattr(item, attribute_name, getattr(deleted_item, attribute_name))
                self.backpack.items.remove(item)
                self.dispatch("item_remove", item)
                break
