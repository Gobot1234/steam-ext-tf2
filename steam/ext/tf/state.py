# -*- coding: utf-8 -*-

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Callable, Coroutine, Optional

try:
    import orvdf as vdf
except ImportError:
    import vdf
else:
    import multidict

    vdf.VDFDict = multidict.MultiDict

import steam
from steam.protobufs import EMsg, MsgProto
from steam.state import ConnectionState, register as register_emsg

from .enums import Language
from .protobufs import (
    GCMsg,
    GCMsgProto,
    base_gcmessages as cso_messages,
    base_gcmessages as messages,
    gcsdk_gcmessages as so_messages,
)

if TYPE_CHECKING:
    from steam import Client
    from steam.http import HTTPClient
    from steam.protobufs.steammessages_clientserver_2 import CMsgGcClient

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
    gc_parsers: dict[Language, EventParser] = {}

    __slots__ = (
        "schema",
        "language",
        "items",
        "backpack_slots",
        "_is_premium",
        "_has_gc_session",
    )

    def __init__(self, client: Client, http: HTTPClient, **kwargs):
        super().__init__(client, http, **kwargs)
        self.schema: Optional[vdf.VDFDict] = None
        self.language: Optional[str] = None

    @register_emsg(EMsg.ClientFromGC)
    async def parse_gc_message(self, msg: MsgProto[CMsgGcClient]) -> None:
        # print("got messsage", msg)

        if msg.body.appid != steam.TF2:
            return

        try:
            language = Language(steam.utils.clear_proto_bit(msg.body.msgtype))
        except ValueError:
            return log.info(
                f"Ignoring unknown msg type: {msg.body.msgtype} ({steam.utils.clear_proto_bit(msg.body.msgtype)})"
            )
        # print("lang is", language)
        try:
            msg = (
                GCMsgProto(language, msg.body.payload)
                if steam.utils.is_proto(language)
                else GCMsg(language, msg.body.payload)
            )
        except Exception as exc:
            return log.error(f"Failed to deserialize message: {language!r}, {msg.body.payload!r}", exc_info=exc)
        else:
            try:
                log.debug(
                    f"Socket has received GC message {msg!r} from the websocket."
                )  # see https://github.com/danielgtaylor/python-betterproto/issues/133
            except Exception:
                pass
        # print("got message", msg)
        try:
            func = self.gc_parsers[language]
        except KeyError:
            log.debug(f"Ignoring event {msg!r}")
        else:
            await steam.utils.maybe_coroutine(func, self, msg)

    @register(Language.ClientWelcome)
    def parse_gc_connect(self, msg: GCMsgProto[messages.CMsgClientWelcome]) -> None:
        self._has_gc_session = True
        self.dispatch("gc_connect", msg.body.version)

    @register(Language.ServerWelcome)
    def parse_gc_connect(self, msg: GCMsgProto[messages.CMsgServerWelcome]) -> None:
        self._has_gc_session = True
        self.dispatch("gc_connect", msg.body.active_version)

    @register(Language.ClientGoodbye)
    def parse_goodbye(self, msg: GCMsgProto[messages.CMsgClientGoodbye]) -> None:
        self.dispatch("gc_disconnect", msg.body.reason)

    @register(Language.ServerGoodbye)
    def parse_goodbye(self, msg: GCMsgProto[messages.CMsgServerGoodbye]) -> None:
        self.dispatch("gc_disconnect", msg.body.reason)

    @register(Language.UpdateItemSchema)
    async def parse_schema(self, msg: GCMsgProto[messages.CMsgUpdateItemSchema]) -> None:
        log.info("Getting TF2 item schema at", msg.body.items_game_url)
        try:
            resp = await self.http._session.get(msg.body.items_game_url)
        except Exception as exc:
            return log.error("Failed to get item schema", exc_info=exc)

        self.schema = vdf.loads(await resp.text())["items_game"]
        log.info("Loaded schema")
        self.dispatch("gc_ready")

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
    def parse_crafting_response(self, msg: GCMsgProto[messages.BluePrintResponse]) -> None:
        self.dispatch("crafting_complete", msg.body)

    @register(Language.SOCacheSubscriptionCheck)
    async def parse_cache_check(self, _) -> None:
        log.debug("Requesting SO cache subscription refresh")
        msg = GCMsg(Language.SOCacheSubscriptionRefresh, owner=self.client.user.id64)
        await self.ws.send_gc_message(msg)

    @register(Language.SOCacheSubscribed)
    async def parse_cache_subscribe(self, msg: GCMsgProto[so_messages.CMsgSOCacheSubscribed]):
        for cache in msg.body.objects:
            if cache.type_id == 1:  # backpack
                items = []
                for item_data in cache.object_data:
                    item = cso_messages.CsoEconItem().parse(item_data)
                    is_new = (item.inventory >> 30) & 1
                    item.position = 0 if is_new else item.inventory & 0xFFFF
                    items.append(item)
                self.items = items
                # TODO patch client.user.inventory (a) to return this but (b) also to merge the items together
                self.dispatch("backpack_load", items)
            elif cache.type_id == 7:  # account metadata
                proto = cso_messages.CsoEconGameAccountClient().parse(cache.object_data[0])
                self._is_premium = not proto.trial_account
                self.backpack_slots = (50 if proto.trial_account else 300) + proto.additional_backpack_slots
                self.dispatch("account_load")  # TODO name doesnt sound too great

    # TODO impl https://github.com/DoctorMcKay/node-tf2/blob/master/handlers.js#L166-L269
