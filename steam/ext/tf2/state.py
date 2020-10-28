# -*- coding: utf-8 -*-

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Callable, Coroutine, Optional

from multidict import MultiDict

import steam
from steam import ClientUser, Game, Inventory
from steam.protobufs import EMsg, GCMsg, GCMsgProto, MsgProto
from steam.state import ConnectionState, register as register_emsg

from .backpack import BackPack
from .enums import Language
from .protobufs import base_gcmessages as cso_messages, base_gcmessages as messages, gcsdk_gcmessages as so_messages

if TYPE_CHECKING:
    from steam.http import HTTPClient
    from steam.protobufs.steammessages_clientserver_2 import CMsgGcClient

    from .client import Client

log = logging.getLogger(__name__)
EventParser = Callable[["GCState", GCMsgProto], Optional[Coroutine[None, None, None]]]


class Registerer:
    __slots__ = ("func", "language")

    def __init__(self, func: EventParser, language: Language):
        self.func = func
        self.language = language

    def __set_name__(self, state: "GCState", _) -> None:
        state.gc_parsers[self.language] = self.func


def register(language: Language) -> Callable[[EventParser], Registerer]:
    def decorator(func: EventParser) -> Registerer:
        return Registerer(func, language)

    return decorator


class GCState(ConnectionState):
    client: Client
    gc_parsers: dict[Language, EventParser] = {}

    __slots__ = (
        "schema",
        "language",
        "backpack",
        "backpack_slots",
        "_unpatched_inventory",
        "_is_premium",
    )

    def __init__(self, client: Client, http: HTTPClient, **kwargs):
        super().__init__(client, http, **kwargs)
        self.schema: Optional[MultiDict] = None
        self.language: Optional[MultiDict] = None
        self._unpatched_inventory: Optional[Callable[[ClientUser, Game], Coroutine[None, None, Inventory]]] = None
        self._is_premium = None

        language = kwargs.get("language")
        if language is not None:
            client.set_language(language)

    @register_emsg(EMsg.ClientFromGC)
    async def parse_gc_message(self, msg: MsgProto[CMsgGcClient]) -> None:
        if msg.body.appid != steam.TF2:
            return

        self.client._connect_event.set()

        try:
            language = Language(steam.utils.clear_proto_bit(msg.body.msgtype))
        except ValueError:
            return log.info(
                f"Ignoring unknown msg type: {msg.body.msgtype} ({steam.utils.clear_proto_bit(msg.body.msgtype)})"
            )

        try:
            msg = (
                GCMsgProto(language, msg.body.payload)
                if steam.utils.is_proto(msg.body.msgtype)
                else GCMsg(language, msg.body.payload)
            )
        except Exception as exc:
            if language == Language.SOCacheSubscriptionCheck:
                # I'm pretty confident the message is broken but we don't need its contents so this is fine
                return await self.parse_cache_check.func(self, None)
            return log.error(f"Failed to deserialize message: {language!r}, {msg.body.payload!r}", exc_info=exc)
        else:
            try:
                log.debug(
                    f"Socket has received GC message {msg!r} from the websocket."
                )  # see https://github.com/danielgtaylor/python-betterproto/issues/133
            except Exception:
                pass

        try:
            func = self.gc_parsers[language]
        except KeyError:
            log.debug(f"Ignoring event {msg!r}")
        else:
            await steam.utils.maybe_coroutine(func, self, msg)

    @register(Language.ClientWelcome)
    def parse_gc_client_connect(self, msg: GCMsgProto[messages.CMsgClientWelcome]) -> None:
        self.dispatch("gc_connect", msg.body.version)

    @register(Language.ServerWelcome)
    def parse_gc_server_connect(self, msg: GCMsgProto[messages.CMsgServerWelcome]) -> None:
        self.dispatch("gc_connect", msg.body.active_version)

    @register(Language.ClientGoodbye)
    def parse_client_goodbye(self, msg: GCMsgProto[messages.CMsgClientGoodbye]) -> None:
        self.dispatch("gc_disconnect", msg.body.reason)

    @register(Language.ServerGoodbye)
    def parse_server_goodbye(self, msg: GCMsgProto[messages.CMsgServerGoodbye]) -> None:
        self.dispatch("gc_disconnect", msg.body.reason)

    @register(Language.UpdateItemSchema)
    async def parse_schema(self, msg: GCMsgProto[messages.CMsgUpdateItemSchema]) -> None:
        log.info(f"Getting TF2 item schema at {msg.body.items_game_url}")
        try:
            resp = await self.http._session.get(msg.body.items_game_url)
        except Exception as exc:
            return log.error("Failed to get item schema", exc_info=exc)

        self.schema = self.client.VDF_DECODER(await resp.text())["items_game"]
        log.info("Loaded schema")

    @register(Language.SystemMessage)
    def parse_system_message(self, msg: GCMsgProto[messages.CMsgSystemBroadcast]) -> None:
        self.dispatch("system_message", msg.body.message)

    @register(Language.ClientDisplayNotification)
    def parse_client_notification(self, msg: GCMsgProto[messages.CMsgGcClientDisplayNotification]) -> None:
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
    def parse_crafting_response(self, msg: GCMsgProto[so_messages.CMsgSOMultipleObjects]) -> None:
        self.dispatch("crafting_complete", msg.body)  # TODO parse into item

    @register(Language.SOCacheSubscriptionCheck)
    async def parse_cache_check(self, _) -> None:
        log.debug("Requesting SO cache subscription refresh")
        msg = GCMsgProto(Language.SOCacheSubscriptionRefresh, owner=self.client.user.id64)
        await self.ws.send_gc_message(msg)

    def patch_user_inventory(self, new_inventory: steam.Inventory) -> None:
        async def inventory(self_: ClientUser, game: Game) -> steam.Inventory:
            if game != steam.TF2:
                return await self._unpatched_inventory(game)

            return new_inventory

        self.client.user.inventory = inventory

    async def update_inventory(self, items: list[cso_messages.CsoEconItem]) -> BackPack:
        backpack = BackPack(await self._unpatched_inventory(self.client.user, steam.TF2))
        for item in backpack:
            for backpack_item in items:
                if item.id == backpack_item.id:
                    for attribute_name in backpack_item.__dataclass_fields__:
                        setattr(item, attribute_name, getattr(backpack_item, attribute_name))
                    is_new = (backpack_item.inventory >> 30) & 1
                    item.position = 0 if is_new else backpack_item.inventory & 0xFFFF
                    break

        self.patch_user_inventory(backpack)
        self.backpack = backpack
        return backpack

    @register(Language.SOCacheSubscribed)
    async def parse_cache_subscribe(self, msg: GCMsgProto[so_messages.CMsgSOCacheSubscribed]) -> None:
        for cache in msg.body.objects:
            if cache.type_id == 1:  # backpack
                items = [cso_messages.CsoEconItem().parse(item_data) for item_data in cache.object_data]
                backpack = await self.update_inventory(items)
                self.dispatch("backpack_load", backpack)
            elif cache.type_id == 7:  # account metadata
                proto = cso_messages.CsoEconGameAccountClient().parse(cache.object_data[0])
                self._is_premium = not proto.trial_account
                self.backpack_slots = (50 if proto.trial_account else 300) + proto.additional_backpack_slots
                self.dispatch("account_load")  # TODO name doesnt sound too great also check dispatch order
                # is probably gonna be on_ready

    @register(Language.SOCreate)
    async def parse_item_add(self, msg: GCMsgProto[so_messages.CMsgSOSingleObject]) -> None:
        if msg.body.type_id != 1:
            return  # not an item

        if not self.backpack:
            return  # we don't have our backpack yet

        received_item = cso_messages.CsoEconItem().parse(msg.body.object_data)
        inventory = await self.update_inventory([received_item])
        item = steam.utils.find(lambda i: i.id == received_item.id, inventory)
        self.dispatch("item_receive", item)

    @register(Language.SOUpdate)
    async def handle_so_update(self, msg: GCMsgProto[so_messages.CMsgSOSingleObject]) -> None:
        await self._handle_so_update(msg.body)

    @register(Language.SOUpdateMultiple)
    async def handle_multiple_so_update(self, msg: GCMsgProto[so_messages.CMsgSOMultipleObjects]) -> None:
        for item in msg.body.objects:
            await self._handle_so_update(item)

    async def _handle_so_update(self, item: so_messages.CMsgSOSingleObject) -> None:
        if item.type_id == 1:
            if not self.backpack:
                return

            received_item = cso_messages.CsoEconItem().parse(item.object_data)
            old_item = steam.utils.find(lambda i: i.id == received_item.id, self.backpack)
            await self.update_inventory([received_item])
            new_item = steam.utils.find(lambda i: i.id == received_item.id, self.backpack)
            self.dispatch("item_update", old_item, new_item)
        elif item.type_id == 7:
            proto = cso_messages.CsoEconGameAccountClient().parse(item.object_data)
            backpack_slots = (50 if proto.trial_account else 300) + proto.additional_backpack_slots
            if proto.trial_account == self._is_premium or self.backpack_slots != backpack_slots:
                self._is_premium = not proto.trial_account
                self.backpack_slots = backpack_slots
                self.dispatch("account_update")
        else:
            log.debug(f"Unknown SO type {item.type_id} updated")

    @register(Language.SODestroy)
    async def handle_item_remove(self, msg: GCMsgProto[so_messages.CMsgSOSingleObject]) -> None:
        if msg.body.type_id != 1 or not self.backpack:
            return

        received_item = cso_messages.CsoEconItem().parse(msg.body.object_data)
        for item in self.backpack:
            if item.id == received_item.id:
                for attribute_name in received_item.__dataclass_fields__:
                    setattr(item, attribute_name, getattr(received_item, attribute_name))
                is_new = (received_item.inventory >> 30) & 1
                item.position = 0 if is_new else received_item.inventory & 0xFFFF
                self.backpack.items.remove(item)
                self.dispatch("item_remove", item)
                break
