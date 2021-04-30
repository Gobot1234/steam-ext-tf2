# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Iterable, Optional, overload

from multidict import MultiDict
from typing_extensions import Final, Literal

from ...client import Client
from ...ext import commands
from ...game import TF2, Game
from ...gateway import Msgs, return_true
from ...protobufs import GCMsg
from ...user import ClientUser, User
from .enums import Language
from .protobufs.struct_messages import CraftResponse
from .state import GCState

if TYPE_CHECKING:
    from steam.ext import tf2

    from ...comment import Comment
    from ...invite import ClanInvite, UserInvite
    from ...message import Message
    from ...trade import Inventory, TradeOffer
    from ..commands import Context
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


class Client(Client):
    GAME: Final[Game] = TF2

    user: Optional[TF2ClientUser]

    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None, **options: Any):
        game = options.pop("game", None)
        if game is not None:  # don't let them overwrite the main game
            try:
                options["games"].append(game)
            except (TypeError, KeyError):
                options["games"] = [game]
        options["game"] = self.GAME
        self._original_games: Optional[list[Game]] = options.get("games")
        self._crafting_lock = asyncio.Lock()

        super().__init__(loop, **options)
        self._connection = GCState(client=self, **options)

    @property
    def schema(self) -> Optional[MultiDict]:
        """Optional[:class:`multidict.MultiDict`]: TF2's item schema."""
        return self._connection.schema

    @property
    def backpack_slots(self) -> Optional[int]:
        """Optional[:class:`int`]: The client's number of backpack slots. ``None`` if the user isn't ready."""
        return self._connection.backpack_slots

    def is_premium(self) -> Optional[bool]:
        """
        Optional[:class:`bool`]: Whether or not the client's account has TF2 premium. ``None`` if the user isn't ready.
        """
        return self._connection._is_premium

    def set_language(self, file: os.PathLike[str]) -> None:
        """Set the localization files for your bot.

        This isn't necessary in most situations.
        """
        from . import VDF_DECODER

        file = Path(file).resolve()
        self._connection.language = VDF_DECODER(file.read_text())

    async def craft(self, items: Iterable[BackPackItem], recipe: int = -2) -> Optional[list[BackPackItem]]:
        """|coro|
        Craft a set of items together with an optional recipe.

        Note
        ----
        This internally acquires a lock and is only able to craft one set of items at a time as we have to wait for a
        response to get the items crafted.

        Parameters
        ----------
        items: list[:class:`BackPackItem`]
            The items to craft.
        recipe: :class:`int`
            The recipe to craft them with default is -2 (wildcard). Setting for metal crafts isn't required. See
            https://github.com/DontAskM8/TF2-Crafting-Recipe/blob/master/craftRecipe.json for other recipe details.

        Returns
        -------
        Optional[list[:class:`BackPackItem`]]
            The crafted items, ``None`` if crafting failed.
        """

        async with self._crafting_lock:
            future = self.loop.create_future()
            listeners = self._listeners.setdefault("crafting_complete", [])
            listeners.append((future, return_true))

            await self.ws.send_gc_message(
                GCMsg(Language.Craft, recipe=recipe, items=[item.id for item in items])
            )
            # would like to be able to just check job_source_id, but it doesn't appear to get set (would also allow
            # this to be used without the lock)
            resp = await self.wait_for("gc_message_receive", check=lambda c: isinstance(c.body, CraftResponse))  # noqa

            if resp.body.recipe_id == -1:  # failed to craft, we need to make sure to cleanup *everything*
                future.cancel()  # cancel the future
                listeners.remove((future, return_true))  # remove the listener
                return None

            return await future

    async def wait_for_gc_ready(self):
        await self._connection._gc_ready.wait()

    # boring subclass stuff

    def _handle_ready(self) -> None:
        self._connection._unpatched_inventory = self.user.inventory
        super()._handle_ready()

    async def _on_gc_connect(self) -> None:
        """
        await self._connection._connected.wait()
        while True:  # this is ok-ish as gateway.KeepAliveHandler should catch any blocking and disconnects
            await self.ws.send_gc_message(GCMsgProto(Language.ClientHello))
            await asyncio.sleep(5)
        """
        # this breaks things not sure why can't be bothered finding out stuff seems to work without pinging.

    if TYPE_CHECKING:

        async def on_gc_connect(self) -> None:
            """|coro|
            Called after the client receives the welcome message from the GC.

            Warning
            -------
            This is called every time we craft an item and disconnect so same warnings apply to
            :meth:`steam.Client.on_connect`
            """

        async def on_gc_disconnect(self) -> None:
            """|coro|
            Called after the client receives the goodbye message from the GC.

            Warning
            -------
            This is called every time we craft an item and disconnect so same warnings apply to
            :meth:`steam.Client.on_connect`
            """

        async def on_gc_ready(self) -> None:
            """|coro|
            Called after the client connects to the GC and has the :attr:`schema`, :meth:`Client.user.inventory` and set
            up and account info (:meth:`is_premium` and :attr:`backpack_slots`).

            Warning
            -------
            This is called every time we craft an item and disconnect so same warnings apply to
            :meth:`steam.Client.on_connect`
            """

        async def on_account_update(self) -> None:
            """|coro|
            Called when the client user's account is updated. This can happen from any one of the below changing:

                - :meth:`is_premium`
                - :attr:`backpack_slots`
            """

        async def on_crafting_complete(self, *items: tf2.BackPackItem) -> None:
            """|coro|
            Called after a crafting recipe is completed.

            Parameters
            ----------
            *items: :class:`tf2.BackPackItem`
                The items the craft request created.
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
            Called when the client has an item removed from its backpack.

            Parameters
            ----------
            item: :class:`tf2.BackPackItem`
                The removed item.
            """

        async def on_item_update(self, before: tf2.BackPackItem, after: tf2.BackPackItem) -> None:
            """|coro|
            Called when the client has an item in its backpack updated.

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
            check: Optional[Callable[[tuple[BackPackItem, ...]], bool]] = ...,
            timeout: Optional[float] = ...,
        ) -> tuple[BackPackItem, ...]:
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
