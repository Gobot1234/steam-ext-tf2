# -*- coding: utf-8 -*-

import asyncio
from typing import Optional

import steam
from steam.ext import commands

from .state import GCState


class GameCoordinatorClient(steam.Client):
    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None, **options):
        popped = options.pop("game", None)
        if popped:  # don't let them overwrite the main game
            options["games"] = [popped]
        super().__init__(loop, game=steam.TF2, **options)
        self._connection = GCState(loop=self.loop, client=self, http=self.http)


class GameCoordinatorBot(GameCoordinatorClient, commands.Bot):
    pass
