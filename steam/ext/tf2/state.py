# -*- coding: utf-8 -*-

import asyncio
from typing import TYPE_CHECKING

from steam.state import ConnectionState, register
from steam.protobufs import MsgProto, EMsg

if TYPE_CHECKING:
    from steam import Client
    from steam.http import HTTPClient


class GCState(ConnectionState):
    def __init__(self, loop: asyncio.AbstractEventLoop, client: "Client", http: "HTTPClient", **kwargs):
        super().__init__(loop, client, http, **kwargs)

    @register(EMsg.ClientFromGC)
    async def parse_gc_message(self, msg: MsgProto):
        print(msg)
