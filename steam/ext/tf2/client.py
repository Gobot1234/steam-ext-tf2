from __future__ import annotations

import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Iterable, Optional, overload

from typing_extensions import Literal

from ..._const import VDF_LOADS
from ...ext import commands
from ...game import TF2, Game
from ...gateway import Msgs
from ...protobufs import GCMsg
from ...user import User
from .._gc import Client as Client_
from .._gc.client import ClientUser as ClientUser_
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
    from .backpack import Backpack, BackpackItem, Schema

__all__ = (
    "Client",
    "Bot",
)


class TF2ClientUser(ClientUser_):
    if TYPE_CHECKING:

        @overload
        async def inventory(self, game: Literal[TF2]) -> Backpack:
            ...

        @overload
        async def inventory(self, game: Game) -> Inventory:
            ...


class Client(Client_):
    _GAME = TF2  # type: ignore
    _ClientUserCls = TF2ClientUser
    user: TF2ClientUser
    _connection: GCState

    def _get_state(self, **options: Any) -> GCState:
        return GCState(client=self, **options)

    def _get_gc_message(self) -> Any:
        return False  # for now this isn't required

    @property
    def schema(self) -> Schema:
        """TF2's item schema. ``None`` if the user isn't ready."""
        return self._connection.schema

    @property
    def backpack_slots(self) -> int:
        """The client's number of backpack slots."""
        return self._connection.backpack_slots

    def is_premium(self) -> bool:
        """Whether or not the client's account has TF2 premium. ``None`` if the user isn't ready."""
        return self._connection._is_premium  # type: ignore

    def set_language(self, file: os.PathLike[str]) -> None:
        """Set the localization files for your bot.

        This isn't necessary in most situations.
        """
        file = Path(file).resolve()
        self._connection.language = VDF_LOADS(file.read_text())

    async def craft(self, items: Iterable[BackpackItem], recipe: int = -2) -> Optional[list[BackpackItem]]:
        """|coro|
        Craft a set of items together with an optional recipe.

        Parameters
        ----------
        items
            The items to craft.
        recipe
            The recipe to craft them with default is -2 (wildcard). Setting for metal crafts isn't required. See
            https://github.com/DontAskM8/TF2-Crafting-Recipe/blob/master/craftRecipe.json for other recipe details.

        Returns
        -------
        The crafted items, ``None`` if crafting failed.
        """

        def check_gc_msg(msg: GCMsg[Any]) -> bool:
            if (
                isinstance(msg.body, CraftResponse) and not msg.body.being_used
            ):  # craft queue is FIFO, so this works fine
                nonlocal ids
                msg.body.being_used = True
                ids = list(msg.body.id_list)
                return True

            return False

        def check_crafting_complete(items: list[BackpackItem]) -> bool:
            return [item.id for item in items] == ids

        ids = []
        future = self.loop.create_future()
        listeners = self._listeners.setdefault("crafting_complete", [])
        listeners.append((future, check_crafting_complete))

        await self.ws.send_gc_message(GCMsg(Language.Craft, recipe=recipe, items=[item.id for item in items]))

        try:
            resp = await self.wait_for("gc_message_receive", check=check_gc_msg, timeout=60)
        except asyncio.TimeoutError:
            recipe_id = -1
        else:
            recipe_id = resp.body.recipe_id

        print("got recipe_id", recipe_id)
        if recipe_id == -1:
            future.cancel()  # cancel the future (it's cleaned from _listeners up by dispatch)
            return None

        return await future

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

        async def on_crafting_complete(self, items: list[tf2.BackpackItem]) -> None:
            """|coro|
            Called after a crafting recipe is completed.

            Parameters
            ----------
            items: list[:class:`tf2.BackpackItem`]
                The items the craft request created.
            """

        async def on_item_receive(self, item: tf2.BackpackItem) -> None:
            """|coro|
            Called when the client receives an item.

            Parameters
            ----------
            item: :class:`tf2.BackpackItem`
                The received item.
            """

        async def on_item_remove(self, item: tf2.BackpackItem) -> None:
            """|coro|
            Called when the client has an item removed from its backpack.

            Parameters
            ----------
            item: :class:`tf2.BackpackItem`
                The removed item.
            """

        async def on_item_update(self, before: tf2.BackpackItem, after: tf2.BackpackItem) -> None:
            """|coro|
            Called when the client has an item in its backpack updated.

            Parameters
            ----------
            before: :class:`tf2.BackpackItem`
                The item before being updated.
            after: :class:`tf2.BackpackItem`
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
                "gc_connect",
                "gc_disconnect",
                "gc_ready",
                "account_update",
            ],
            *,
            check: Callable[[], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> None:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["error"],
            *,
            check: Callable[[str, Exception, tuple[Any, ...], dict[str, Any]], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> tuple[str, Exception, tuple, dict]:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["message"],
            *,
            check: Callable[[Message], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> Message:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["comment"],
            *,
            check: Callable[[Comment], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> Comment:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["user_update"],
            *,
            check: Callable[[User, User], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> tuple[User, User]:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["typing"],
            *,
            check: Callable[[User, datetime], bool] = ...,
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
            check: Callable[[TradeOffer], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> TradeOffer:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["user_invite"],
            *,
            check: Callable[[UserInvite], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> UserInvite:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["clan_invite"],
            *,
            check: Callable[[ClanInvite], bool] = ...,
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
            check: Callable[[Msgs], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> Msgs:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["crafting_complete"],
            *,
            check: Callable[[list[tf2.BackpackItem]], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> list[tf2.BackpackItem]:
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
            check: Callable[[BackpackItem], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> BackpackItem:
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
                "gc_connect",
                "gc_disconnect",
                "gc_ready",
                "account_update",
            ],
            *,
            check: Callable[[], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> None:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["error"],
            *,
            check: Callable[[str, Exception, tuple[Any, ...], dict[str, Any]], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> tuple[str, Exception, tuple, dict]:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["message"],
            *,
            check: Callable[[Message], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> Message:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["comment"],
            *,
            check: Callable[[Comment], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> Comment:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["user_update"],
            *,
            check: Callable[[User, User], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> tuple[User, User]:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["typing"],
            *,
            check: Callable[[User, datetime], bool] = ...,
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
            check: Callable[[TradeOffer], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> TradeOffer:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["user_invite"],
            *,
            check: Callable[[UserInvite], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> UserInvite:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["clan_invite"],
            *,
            check: Callable[[ClanInvite], bool] = ...,
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
            check: Callable[[Msgs], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> Msgs:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["command_error"],
            *,
            check: Callable[[Context, Exception], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> tuple[Context, Exception]:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["command"],
            *,
            check: Callable[[Context], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> Context:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["command_completion"],
            *,
            check: Callable[[Context], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> Context:
            ...

        @overload
        async def wait_for(
            self,
            event: Literal["crafting_complete"],
            *,
            check: Callable[[list[tf2.BackpackItem]], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> list[tf2.BackpackItem]:
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
            check: Callable[[BackpackItem], bool] = ...,
            timeout: Optional[float] = ...,
        ) -> BackpackItem:
            ...
