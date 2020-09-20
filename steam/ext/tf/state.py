# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
import logging
from typing import Callable, Coroutine, Optional, TYPE_CHECKING

import steam
from steam.state import ConnectionState, register as register_emsg
from steam.protobufs import MsgProto, EMsg

from .enums import Language
from .protobufs.base_gcmessages import CMsgClientGoodbye, CMsgClientWelcome, CMsgServerGoodbye, CMsgServerWelcome

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

    __slots__ = ('_has_gc_session',)

    def __init__(self, loop: asyncio.AbstractEventLoop, client: Client, http: HTTPClient, **kwargs):
        super().__init__(loop, client, http, **kwargs)

    @register_emsg(EMsg.ClientFromGC)
    async def parse_gc_message(self, msg: DefaultMsg):
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
    def parse_gc_connect(self, msg: DefaultMsg):
        proto = CMsgClientWelcome().parse(msg.body.payload)
        self._has_gc_session = True
        self.dispatch("gc_connect", proto.version)

    @register(Language.ServerWelcome)
    def parse_gc_connect(self, msg: DefaultMsg):
        proto = CMsgServerWelcome().parse(msg.body.payload)
        self._has_gc_session = True
        self.dispatch("gc_connect", proto.active_version)

    @register(Language.ServerGoodbye)
    def parse_goodbye(self, msg: DefaultMsg):
        proto = CMsgClientGoodbye().parse(msg.body.payload)
        self.dispatch("gc_disconnect", proto.reason)

    @register(Language.ServerGoodbye)
    def parse_goodbye(self, msg: DefaultMsg):
        proto = CMsgServerGoodbye().parse(msg.body.payload)
        self.dispatch("gc_disconnect", proto.reason)

    # TODO impl https://github.com/DoctorMcKay/node-tf2/blob/master/handlers.js
