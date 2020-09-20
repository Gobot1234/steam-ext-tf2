# -*- coding: utf-8 -*-

import asyncio
from typing import Optional

import steam
from steam.ext import commands

from .state import GCState

__title__ = "steam.ext.tf2"
__author__ = "Gobot1234"
__license__ = "MIT"
__version__ = "1.0.0a"


class Client(steam.Client):
    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None, **options):
        popped = options.pop("game", None)
        if popped:  # don't let them overwrite the main game
            options["games"] = [popped]
        super().__init__(loop, game=steam.TF2, **options)
        self._connection = GCState(loop=self.loop, client=self, http=self.http)

    # TODO docs events


class Bot(Client, commands.Bot):
    pass
