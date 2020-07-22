# -*- coding: utf-8 -*-

import asyncio
from typing import Awaitable, Callable, Dict, Optional, TYPE_CHECKING

from steam.state import ConnectionState, register as register_emsg
from steam.protobufs import MsgProto, EMsg

from .enums import Language

if TYPE_CHECKING:
    from steam import Client
    from steam.http import HTTPClient

EventParser = Callable[["ConnectionState", "MsgProto"], Optional[Awaitable[None]]]


class Registerer:
    __slots__ = ("func", "language")

    def __init__(self, func: EventParser, language: Language):
        self.func = func
        self.language = language

    def __set_name__(self, state: "GCState", _):
        state.gc_parsers[self.language] = self.func


def register(language: Language) -> Callable[[EventParser], Registerer]:
    def decorator(func: EventParser):
        return Registerer(func, language)

    return decorator


class GCState(ConnectionState):
    gc_parsers: Dict[Language, EventParser] = dict()

    def __init__(self, loop: asyncio.AbstractEventLoop, client: "Client", http: "HTTPClient", **kwargs):
        super().__init__(loop, client, http, **kwargs)

    @register_emsg(EMsg.ClientFromGC)
    async def parse_gc_message(self, msg: MsgProto):
        print(msg)

    @register(Language.ServerWelcome)
    async def parse_gc_logon(self, msg: MsgProto):
        self.dispatch('gc_connect')

    @register(Language.ServerGoodbye)
    async def parse_gc_logoff(self, msg: MsgProto):
        self.dispatch('gc_disconnect')
