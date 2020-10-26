# -*- coding: utf-8 -*-

import asyncio
import json
from pathlib import Path
from typing import Callable, TYPE_CHECKING, Optional, Union

import vdf
from multidict import MultiDict
from typing_extensions import Final

from steam import Client, Game, TF2
from steam.ext import commands
from .enums import Language
from .protobufs import GCMsgProto
from .state import GCState

if TYPE_CHECKING:
    from .protobufs.base_gcmessages import BluePrintResponse
    from steam.ext import tf2

__all__ = (
    "Client",
    "Bot",
)


class Client(Client):
    VDF_DECODER: Callable[[str], MultiDict] = vdf.loads  #: The default VDF decoder to use
    VDF_ENCODER: Callable[[str], MultiDict] = vdf.dumps  #: The default VDF encoder to use
    GAME: Final[Game] = TF2

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
    def schema(self) -> MultiDict:
        return self._connection.schema

    def is_premium(self) -> bool:
        return self._connection._is_premium

    def set_language(self, file: Union[Path, str]) -> None:
        """Set the localization files for your bot."""
        file = Path(file).resolve()
        self._connection.language = json.loads(file.read_text())

    if TYPE_CHECKING:

        async def on_gc_connect(self, version: int) -> None:
            """|coro|
            Called after the client receives the welcome message from the  GC.

            Parameters
            ----------
            version: :class:`int`
                The version loaded.
            """

        async def on_gc_disconnect(self, reason: str) -> None:
            """|coro|
            Called after the client receives the goodbye message from the  GC.

            Parameters
            ----------
            reason: :class:`str`
                The reason for the disconnect
            """

        async def on_gc_ready(self) -> None:
            """|coro|
            Called after the Client connects to the GC and has the :attr:`schema`.
            """

        async def on_crafting_complete(self, craft: tf2.BluePrintResponse) -> None:
            """|coro|
            Called after a crafting recipe is completed.

            Parameters
            ----------
            craft: :class:`tf2.BluePrintResponse`
                The completed crafting recipe.
            """

        # above should be safe from changes

        # async def on_account_load(self) -> None: ... # might be removed depending on how long this takes to dispatch

        '''
        async def on_backpack_update(self, backpack: tf2.BackPack):
            """|coro|
            Called when the bot's backpack is updated. 
            
            Note
            ----
            This can be accessed at any time by calling :meth:`steam.ClientUser.inventory` with :attr:`steam.TF2` as 
            the game.

            Parameters
            ----------
            backpack: :class:`tf2.BackPack`
                The bot's backpack.
            """
        '''


class Bot(commands.Bot, Client):
    pass
