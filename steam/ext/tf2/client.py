# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Optional, Union

import vdf
from multidict import MultiDict
from typing_extensions import Final

from steam import TF2, Client, Game
from steam.ext import commands
from steam.protobufs import GCMsg

from .enums import Language
from .state import GCState

if TYPE_CHECKING:
    from steam.ext import tf2

    from .backpack import BackPackItem
    from .protobufs.base_gcmessages import BluePrintResponse

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
        self._gc_connect_task: Optional[asyncio.Task] = None

    @property
    def schema(self) -> Optional[MultiDict]:
        """:class:`multidict.MultiDict`: TF2's item schema."""
        return self._connection.schema

    @property
    def backpack_slots(self) -> int:
        """:class:`int`: The client's number of backpack slots"""
        return self._connection.backpack_slots

    def is_premium(self) -> bool:
        """:class:`bool`: Whether or not the client's account has TF2 premium"""
        return self._connection._is_premium

    def set_language(self, file: Union[Path, str]) -> None:
        """Set the localization files for your bot."""
        file = Path(file).resolve()
        self._connection.language = self.VDF_DECODER(file.read_text())

    async def craft(self, items: list[BackPackItem], recipe: Optional[int] = None):
        pass

    # boring subclass stuff

    async def start(self, *args, **kwargs) -> None:
        self._gc_connect_task = self.loop.create_task(self._on_gc_connect())
        await super().start(*args, **kwargs)

    async def _on_gc_connect(self) -> None:
        await self.wait_until_ready()
        self._connection._unpatched_inventory = self.user.inventory
        await self.wait_for("gc_connect")
        while True:  # this is ok-ish as gateway.KeepAliveHandler should catch any blocking and disconnects
            await self.ws.send_gc_message(GCMsg(Language.ClientHello))
            await asyncio.sleep(5)

    async def close(self) -> None:
        await self.ws.send_gc_message(GCMsg(Language.ClientGoodbye))
        self._gc_connect_task.cancel()
        await super().close()

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
            Called after the client connects to the GC and has the :attr:`schema`, :meth:`Client.user.inventory` and set
            up and account info (:meth:`is_premium` and :attr:`backpack_slots`).
            """

        async def on_account_update(self) -> None:
            """|coro|
            Called when the client user's account is updated. This can happen from any one of the below changing:

                - :meth:`is_premium`
                - :attr:`backpack_slots`
            """

        # NOTE!!!!!!
        # above should be safe from changes
        # below are subject to changes and or may be broken

        async def on_crafting_complete(self, craft: tf2.BluePrintResponse) -> None:
            """|coro|
            Called after a crafting recipe is completed.

            Parameters
            ----------
            craft: :class:`tf2.BluePrintResponse`
                The completed crafting recipe.
            """

        async def on_backpack_update(self, backpack: tf2.BackPack):
            """|coro|
            Called when the client's backpack is updated.

            Note
            ----
            This can be accessed at any time by calling :meth:`steam.ClientUser.backpack` with :attr:`steam.TF2` as
            the game.

            Parameters
            ----------
            backpack: :class:`tf2.BackPack`
                The client's backpack.
            """

        async def on_item_receive(self, item: tf2.BackPackItem):
            """|coro|
            Called when the client receives an item.

            Parameters
            ----------
            item: :class:`tf2.BackPackItem`
                The received item.
            """

        async def on_item_remove(self, item: tf2.BackPackItem):
            """|coro|
            Called when the client has an item removed from its inventory.

            Parameters
            ----------
            item: :class:`tf2.BackPackItem`
                The removed item.
            """

        async def on_item_update(self, before: tf2.BackPackItem, after: tf2.BackPackItem):
            """|coro|
            Called when the client has an item in its inventory updated.

            Parameters
            ----------
            before: :class:`tf2.BackPackItem`
                The item before being updated.
            after: :class:`tf2.BackPackItem`
                The item now.
            """

    # TODO wait_fors


class Bot(commands.Bot, Client):
    pass
