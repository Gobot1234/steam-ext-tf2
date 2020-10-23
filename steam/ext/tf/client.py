# -*- coding: utf-8 -*-

import asyncio
from typing import TYPE_CHECKING, Optional

from ...client import Client
from ...ext import commands
from ...game import TF2
from ...gateway import SteamWebSocket
from ...protobufs import EMsg, MsgProto
from ...protobufs.steammessages_clientserver_2 import CMsgGcClient
from ...utils import set_proto_bit
from .enums import Language
from .protobufs import GCMsgBase, GCMsgProto, base_gcmessages as messages
from .state import GCState

__all__ = (
    "Client",
    "Bot",
)


class Client(Client):
    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None, **options):
        game = options.pop("game", None)
        if game is not None:  # don't let them overwrite the main game
            try:
                options["games"].append(game)
            except (TypeError, KeyError):
                options["games"] = [game]
        options["game"] = TF2
        super().__init__(loop, **options)
        self._connection = GCState(client=self, http=self.http, **options)

    async def close(self) -> None:
        await self.ws.send_gc_message(GCMsgProto(Language.ClientGoodbye))
        await super().close()

    @property
    def schema(self):
        return self._connection.schema

    if TYPE_CHECKING:
        # TODO docs events
        pass


class Bot(commands.Bot, Client):
    pass
