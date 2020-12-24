# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, TYPE_CHECKING, Callable, Optional, Union, overload

import vdf
from multidict import MultiDict
from typing_extensions import Final, Literal

from steam import TF2, ClanInvite, Client, ClientUser, Comment, Game, Message, TradeOffer, User, UserInvite, Inventory
from steam.ext import commands
from steam.protobufs import GCMsg, GCMsgProto

from ...gateway import Msgs
from ..commands import Context
from .enums import Language
from .protobufs.struct_messages import CraftResponse
from .state import GCState

if TYPE_CHECKING:
    from steam.ext import tf2

    from .backpack import BackPack, BackPackItem

__all__ = (
    "Client",
    "Bot",
)


class TF2ClientUser(ClientUser):
    @overload
    async def inventory(self, game: Literal[TF2]) -> BackPack:
        ...

    @overload
    async def inventory(self, game: Game) -> Inventory:
        ...

    async def inventory(self, game: Game) -> Union[Inventory, BackPack]:
        return await super().inventory(game)


class Client(Client):
    VDF_DECODER: Callable[[str], MultiDict] = vdf.loads  #: The default VDF decoder to use
    VDF_ENCODER: Callable[[str], MultiDict] = vdf.dumps  #: The default VDF encoder to use
    GAME: Final[Game] = TF2

    user: Optional[TF2ClientUser]

    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None, **options: Any):
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
        """Set the localization files for your bot.

        This isn't necessary in most situations.
        """
        file = Path(file).resolve()
        self._connection.language = self.VDF_DECODER(file.read_text())

    async def craft(self, items: list[BackPackItem], recipe: int = -2) -> None:
        """|coro|
        Craft a set of items together with an optional recipe.

        Parameters
        ----------
        items: list[:class:`BackPackItem`]
            The items to craft.
        recipe: :class:`int`
            The recipe to craft them with default is -2 (wildcard). See
            https://github.com/DontAskM8/TF2-Crafting-Recipe/blob/master/craftRecipe.json for recipe details.
        """
        msg = GCMsg(Language.Craft, recipe=recipe, items=[item.id for item in items])
        await self.ws.send_gc_message(msg)

    # boring subclass stuff

    async def start(self, *args: Any, **kwargs: Any) -> None:
        self._gc_connect_task = self.loop.create_task(self._on_gc_connect())
        self._gc_disconnect_task = self.loop.create_task(self._on_disconnect())
        await super().start(*args, **kwargs)

    async def _on_gc_connect(self) -> None:
        await self.wait_until_ready()
        self._connection._unpatched_inventory = self.user.inventory
        await self.wait_for("gc_connect")
        while True:  # this is ok-ish as gateway.KeepAliveHandler should catch any blocking and disconnects
            await self.ws.send_gc_message(GCMsgProto(Language.ClientHello))
            await asyncio.sleep(5)

    async def _on_disconnect(self) -> None:
        while True:
            await self.wait_for("disconnect")
            self._gc_connect_task.cancel()
            await self.wait_for("connect")
            self._gc_connect_task = self.loop.create_task(self._on_gc_connect())

    async def close(self) -> None:
        try:
            if self.ws:
                await self.ws.send_gc_message(GCMsgProto(Language.ClientGoodbye))
                await self.change_presence(game=Game(id=0))  # disconnect from games
            if self.is_ready():
                self._gc_disconnect_task.cancel()
                self._gc_connect_task.cancel()
        finally:
            await super().close()

    if TYPE_CHECKING:

        async def on_gc_connect(self, version: int) -> None:
            """|coro|
            Called after the client receives the welcome message from the GC.
            """

        async def on_gc_disconnect(self) -> None:
            """|coro|
            Called after the client receives the goodbye message from the GC.
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
        # these may be broken

        async def on_crafting_complete(self, *items: tf2.BackPackItem) -> None:
            """|coro|
            Called after a crafting recipe is completed.

            Parameters
            ----------
            *items: :class:`tf2.BackPackItem`
                The items the craft request created.
            """

        async def on_backpack_update(self, backpack: tf2.BackPack) -> None:
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

        async def on_item_receive(self, item: tf2.BackPackItem) -> None:
            """|coro|
            Called when the client receives an item.

            Parameters
            ----------
            item: :class:`tf2.BackPackItem`
                The received item.
            """

        async def on_item_remove(self, item: tf2.BackPackItem) -> None:
            """|coro|
            Called when the client has an item removed from its inventory.

            Parameters
            ----------
            item: :class:`tf2.BackPackItem`
                The removed item.
            """

        async def on_item_update(self, before: tf2.BackPackItem, after: tf2.BackPackItem) -> None:
            """|coro|
            Called when the client has an item in its inventory updated.

            Parameters
            ----------
            before: :class:`tf2.BackPackItem`
                The item before being updated.
            after: :class:`tf2.BackPackItem`
                The item now.
            """

        @overload
        async def wait_for(
            self,
            event: Literal[
                "connect",
                "disconnect",
                "ready",
                "login",
                "logout",
            ],
            *,
            check: Optional[Callable[[], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> None:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["error"],
            *,
            check: Optional[Callable[[str, Exception, tuple[Any, ...], dict[str, Any]], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> tuple[str, Exception, tuple, dict]:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["message"],
            *,
            check: Optional[Callable[[Message], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> Message:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["comment"],
            *,
            check: Optional[Callable[[Comment], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> Comment:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["user_update"],
            *,
            check: Optional[Callable[[User, User], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> tuple[User, User]:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["typing"],
            *,
            check: Optional[Callable[[User, datetime], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> tuple[User, datetime]:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal[
                "trade_receive",
                "trade_send",
                "trade_accept",
                "trade_decline",
                "trade_cancel",
                "trade_expire",
                "trade_counter",
            ],
            *,
            check: Optional[Callable[[TradeOffer], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> TradeOffer:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["user_invite"],
            *,
            check: Optional[Callable[[UserInvite], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> UserInvite:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["clan_invite"],
            *,
            check: Optional[Callable[[ClanInvite], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> ClanInvite:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal[
                "socket_receive",
                "socket_send",
            ],
            *,
            check: Optional[Callable[[Msgs], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> Msgs:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal[
                "socket_raw_receive",
                "socket_raw_send",
            ],
            *,
            check: Optional[Callable[[bytes], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> bytes:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal[
                "gc_connect",
                "gc_disconnect",
                "gc_ready",
                "account_update",
            ],
            *,
            check: Optional[Callable[[], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> None:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["crafting_complete"],
            *,
            check: Optional[Callable[[CraftResponse], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> CraftResponse:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["backpack_update"],
            *,
            check: Optional[Callable[[BackPack], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> BackPack:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal[
                "item_receive",
                "item_remove",
                "item_update",
            ],
            *,
            check: Optional[Callable[[BackPackItem], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> BackPackItem:
            ...


class Bot(commands.Bot, Client):
    if TYPE_CHECKING:

        @overload
        async def wait_for(
            self,
            event: Literal[
                "connect",
                "disconnect",
                "ready",
                "login",
                "logout",
            ],
            *,
            check: Optional[Callable[[], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> None:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["error"],
            *,
            check: Optional[Callable[[str, Exception, tuple[Any, ...], dict[str, Any]], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> tuple[str, Exception, tuple, dict]:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["message"],
            *,
            check: Optional[Callable[[Message], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> Message:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["comment"],
            *,
            check: Optional[Callable[[Comment], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> Comment:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["user_update"],
            *,
            check: Optional[Callable[[User, User], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> tuple[User, User]:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["typing"],
            *,
            check: Optional[Callable[[User, datetime], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> tuple[User, datetime]:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal[
                "trade_receive",
                "trade_send",
                "trade_accept",
                "trade_decline",
                "trade_cancel",
                "trade_expire",
                "trade_counter",
            ],
            *,
            check: Optional[Callable[[TradeOffer], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> TradeOffer:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["user_invite"],
            *,
            check: Optional[Callable[[UserInvite], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> UserInvite:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["clan_invite"],
            *,
            check: Optional[Callable[[ClanInvite], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> ClanInvite:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal[
                "socket_receive",
                "socket_send",
            ],
            *,
            check: Optional[Callable[[Msgs], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> Msgs:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal[
                "socket_raw_receive",
                "socket_raw_send",
            ],
            *,
            check: Optional[Callable[[bytes], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> bytes:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["command_error"],
            *,
            check: Optional[Callable[[Context, Exception], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> tuple[Context, Exception]:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["command"],
            *,
            check: Optional[Callable[[Context], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> Context:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["command_completion"],
            *,
            check: Optional[Callable[[Context], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> Context:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal[
                "gc_connect",
                "gc_disconnect",
                "gc_ready",
                "account_update",
            ],
            *,
            check: Optional[Callable[[], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> None:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["crafting_complete"],
            *,
            check: Optional[Callable[[CraftResponse], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> CraftResponse:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["backpack_update"],
            *,
            check: Optional[Callable[[BackPack], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> BackPack:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal[
                "item_receive",
                "item_remove",
                "item_update",
            ],
            *,
            check: Optional[Callable[[BackPackItem], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> BackPackItem:
            ...
