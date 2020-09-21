# -*- coding: utf-8 -*-

import asyncio
from typing import Optional, TYPE_CHECKING

import steam
from steam.ext import commands

from .enums import Language
from .state import GCState
from .protobufs import GCMsg, base_gcmessages as messages


__all__ = (
    "Client",
    "Bot",
)


class Client(steam.Client):
    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None, **options):
        super().__init__(loop, **options)
        popped = options.pop("game", None)
        if popped is not None:  # don't let them overwrite the main game
            options["games"] = [popped]
        self._connection = GCState(loop=self.loop, client=self, http=self.http, game=steam.TF2, **options)

    async def close(self) -> None:
        await self.ws.send_as_proto(GCMsg(Language.ClientGoodbye))
        await super().close()

    @property
    def schema(self):
        return self._connection.schema

    if TYPE_CHECKING:
        # TODO docs events
        pass


class Bot(Client, commands.Bot):
    pass

