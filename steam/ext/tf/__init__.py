# -*- coding: utf-8 -*-

import asyncio
from typing import TYPE_CHECKING, Optional

import steam
from steam.ext import commands

from .state import GCState

__title__ = "steam.ext.tf"
__author__ = "Gobot1234"
__license__ = "MIT"
__version__ = "1.0.0a"


class Client(steam.Client):
    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None, **options):
        popped = options.pop("game", None)
        if popped is not None:  # don't let them overwrite the main game
            options["games"] = [popped]
        super().__init__(loop, game=steam.TF2, **options)
        self._connection = GCState(loop=self.loop, client=self, http=self.http)

    @property
    def schema(self):
        return self._connection.schema

    if TYPE_CHECKING:
        # TODO docs events
        pass


class Bot(Client, commands.Bot):
    pass


del asyncio, TYPE_CHECKING, Optional
