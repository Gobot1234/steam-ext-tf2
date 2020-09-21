# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
import logging
import re
from typing import TYPE_CHECKING, Callable, Coroutine, Optional

import vdf

import steam
from steam.protobufs import EMsg, MsgProto
from steam.state import ConnectionState, register as register_emsg

from .enums import Language
from .protobufs import base_gcmessages as messages

if TYPE_CHECKING:
    from steam import Client
    from steam.http import HTTPClient
    from steam.protobufs.steammessages_clientserver_2 import CMsgGcClient

log = logging.getLogger(__name__)
DefaultMsg = MsgProto["CMsgGcClient"]
EventParser = Callable[["GCState", DefaultMsg], Optional[Coroutine[None, None, None]]]


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
    gc_parsers: dict[Language, EventParser] = dict()

    __slots__ = (
        "schema",
        "language",
        "_has_gc_session",
    )

    def __init__(self, loop: asyncio.AbstractEventLoop, client: Client, http: HTTPClient, **kwargs):
        super().__init__(loop, client, http, **kwargs)
        self.schema: Optional[vdf.VDFDict] = None
        self.language: Optional[str] = None

    @register_emsg(EMsg.ClientFromGC)
    async def parse_gc_message(self, msg: DefaultMsg) -> None:
        if msg.body.appid != steam.TF2:
            return
        try:
            language = Language(steam.utils.clear_proto_bit(msg.body.msgtype))
        except ValueError:
            return log.info(
                f"Ignoring unknown msg type: {msg.body.msgtype} ({steam.utils.clear_proto_bit(msg.body.msgtype)})"
            )

        try:
            func = self.gc_parsers[language]
        except KeyError:
            log.debug(f"Ignoring event {msg!r}")
        else:
            await steam.utils.maybe_coroutine(func, self, msg)

    @register(Language.ClientWelcome)
    def parse_gc_connect(self, msg: DefaultMsg) -> None:
        proto = messages.CMsgClientWelcome().parse(msg.body.payload)
        self._has_gc_session = True
        self.dispatch("gc_connect", proto.version)

    @register(Language.ServerWelcome)
    def parse_gc_connect(self, msg: DefaultMsg) -> None:
        proto = messages.CMsgServerWelcome().parse(msg.body.payload)
        self._has_gc_session = True
        self.dispatch("gc_connect", proto.active_version)

    @register(Language.ClientGoodbye)
    def parse_goodbye(self, msg: DefaultMsg) -> None:
        proto = messages.CMsgClientGoodbye().parse(msg.body.payload)
        self.dispatch("gc_disconnect", proto.reason)

    @register(Language.ServerGoodbye)
    def parse_goodbye(self, msg: DefaultMsg) -> None:
        proto = messages.CMsgServerGoodbye().parse(msg.body.payload)
        self.dispatch("gc_disconnect", proto.reason)

    @register(Language.UpdateItemSchema)
    async def parse_schema(self, msg: DefaultMsg) -> None:
        proto = messages.CMsgUpdateItemSchema().parse(msg.body.payload)

        try:
            resp = await self.http._session.get(proto.items_game_url)
        except Exception as exc:
            log.error("Failed to get item schema")
            return log.error(exc)

        self.schema = vdf.parse(await resp.text())["items_game"]
        self.dispatch("gc_ready")

    @register(Language.SystemMessage)
    def parse_system_message(self, msg: DefaultMsg) -> None:
        proto = messages.CMsgSystemBroadcast().parse(msg.payload.body)
        self.dispatch("system_message", proto.message)

    @register(Language.ClientDisplayNotification)
    def parse_client_notification(self, msg: DefaultMsg) -> None:
        if self.language is None:
            return

        proto = messages.CMsgGcClientDisplayNotification().parse(msg.body.payload)
        title = self.language[proto.notification_title_localization_key[1:]]
        text = re.sub(r"[\u0001|\u0002]", "", self.language[proto.notification_body_localization_key[1]])
        for i, replacement in enumerate(proto.body_substring_values):
            if replacement[0] == "#":
                replacement = self.language[replacement[1:]]
            text = text.replace(f"%{proto.body_substring_keys[i]}%", replacement)
        self.dispatch("display_notification", title, text)

    @register(Language.CraftResponse)
    def parse_crafting_response(self, msg: DefaultMsg) -> None:
        proto = messages.BluePrintResponse().parse(msg.body.payload)
        self.dispatch("crafting_complete", proto)

    @register_emsg(EMsg.ServiceMethodResponse)
    async def parse_service_method_response(self, msg: MsgProto) -> None:
        await self.ws.send
        super().parse_service_method_response(msg)

    # TODO impl https://github.com/DoctorMcKay/node-tf2/blob/master/handlers.js#L129-L269
