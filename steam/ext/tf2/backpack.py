# -*- coding: utf-8 -*-

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Iterator

import steam

from ...protobufs import GCMsg, GCMsgProto
from .enums import BackpackSortType, Class, ItemQuality, ItemSlot, Language

if TYPE_CHECKING:
    from .protobufs.base_gcmessages import CsoEconItem, CsoEconItemAttribute, CsoEconItemEquipped
    from .state import GCState

__all__ = (
    "BackPackItem",
    "BackPack",
)


class BackPackItem(steam.Item):
    """A class to represent an item from the client's backpack.

    Attributes
    ----------
    id: :class:`int`
        An alias for :attr:`asset_id`.
    position: :class:`int`
        The item's position in the inventory.
    quality: :class:`ItemQuality`
        The item's quality.
    """

    # others not a clue please feel to PR them

    __slots__ = (
        "id",
        "position",
        "account_id",
        "inventory",
        "def_index",
        "quantity",
        "level",
        "quality",
        "flags",
        "origin",
        "custom_name",
        "custom_desc",
        "attribute",
        "interior_item",
        "in_use",
        "style",
        "original_id",
        "contains_equipped_state",
        "equipped_state",
        "contains_equipped_state_v2",
        "_state",
    )

    id: int
    position: int
    account_id: int
    inventory: int
    def_index: int
    quantity: int
    level: int
    quality: int
    flags: int
    origin: int
    custom_name: str
    custom_desc: str
    attribute: list[CsoEconItemAttribute]
    interior_item: CsoEconItem
    in_use: bool
    style: int
    original_id: int
    contains_equipped_state: bool
    equipped_state: list[CsoEconItemEquipped]
    contains_equipped_state_v2: bool

    def __init__(self, item: steam.Item, state: GCState):
        for name, attr in inspect.getmembers(item):
            try:
                setattr(self, name, attr)
            except (AttributeError, TypeError):
                pass
        try:
            self.quality = ItemQuality.try_value(self.quality)
        except AttributeError:
            pass
        self._state = state

    def __repr__(self) -> str:
        item_repr = super().__repr__()[6:-1]
        resolved = [item_repr]
        attrs = ("position",)
        resolved.extend(f"{attr}={getattr(self, attr)!r}" for attr in attrs)
        return f"<BackPackItem {' '.join(resolved)}>"

    async def use(self) -> None:
        """|coro|
        Use this item.
        """
        msg = GCMsgProto(Language.UseItemRequest, item_id=self.id)
        await self._state.ws.send_gc_message(msg)

    async def open(self, key: BackPackItem) -> None:
        """|coro|
        Open a crate with a ``key``.

        Parameters
        ----------
        key: :class:`BackPackItem`
            The key to open the crate with.
        """
        msg = GCMsg(Language.UnlockCrate, key_id=key.id, crate_id=self.id)
        await self._state.ws.send_gc_message(msg)

    async def delete(self) -> None:
        """|coro|
        Delete this item.
        """
        msg = GCMsg(Language.Delete, item_id=self.id)
        await self._state.ws.send_gc_message(msg)

    async def wrap(self, wrapper: BackPackItem) -> None:
        """|coro|
        Wrap this item with the ``wrapper``.

        Parameters
        ----------
        wrapper: :class:`BackPackItem`
            The wrapping paper to use.
        """
        msg = GCMsg(Language.GiftWrapItem, item_id=self.id, wrapping_paper_id=wrapper.id)
        await self._state.ws.send_gc_message(msg)

    async def unwrap(self) -> None:
        """|coro|
        Unwrap this item.
        """
        msg = GCMsg(Language.GiftWrapItem, gift_id=self.id)
        await self._state.ws.send_gc_message(msg)

    async def equip(self, mercenary: Class, slot: ItemSlot) -> None:
        """|coro|
        Equip this item to a mercenary.

        Parameters
        ----------
        mercenary: :class:`Class`
            The mercenary to equip the item to.
        slot: :class:`ItemSlot`
            The item slot to equip the item to.
        """
        msg = GCMsgProto(Language.AdjustItemEquippedState, item_id=self.id, new_class=mercenary, new_slot=slot)
        await self._state.ws.send_gc_message(msg)

    async def set_position(self, position: int) -> None:
        """|coro|
        Set the position for this item.

        Parameters
        ----------
        position: :class:`int`
            The position to set the item to.
        """
        await self._state.backpack.set_positions([(self, position)])

    async def set_style(self, style: int) -> None:
        """|coro|
        Set the style for this item.
        """
        msg = GCMsg(Language.SetItemStyle, item_id=self.id, style=style)
        await self._state.ws.send_gc_message(msg)

    async def send_to(self, user: steam.User) -> None:
        """|coro|
        Send this gift-wrapped item to another user.

        Parameters
        ----------
        user: :class:`steam.User`
            The user to send this gift wrapped item to.
        """
        msg = GCMsg(Language.DeliverGift, user_id64=user.id64, gift_id=self.id)
        await self._state.ws.send_gc_message(msg)


class BackPack(steam.Inventory):
    """A class to represent the client's backpack."""

    def __init__(self, inventory: steam.Inventory):
        for name, attr in inspect.getmembers(inventory):
            try:
                setattr(self, name, attr)
            except (AttributeError, TypeError):
                pass
        self.items: list[BackPackItem] = [BackPackItem(item, self._state) for item in inventory.items]

    def __iter__(self) -> Iterator[BackPackItem]:
        return iter(self.items)

    async def set_positions(self, items_and_positions: list[tuple[BackPackItem, int]]) -> None:
        """|coro|
        Set the positions of items in the inventory.

        Parameters
        ----------
        items_and_positions: list[tuple[:class:`BackPackItem`, int]]
            A list of (item, position) pairs to set the positions for.
        """  # TODO is this 0 indexed?
        item_positions = [(item.id, position) for item, position in items_and_positions]
        msg = GCMsgProto(Language.SetItemPositions, item_positions=item_positions)
        await self._state.ws.send_gc_message(msg)

    async def sort(self, type: BackpackSortType) -> None:
        """|coro|
        Sort this inventory.

        Parameters
        ----------
        type: :class:`BackpackSortType`
            The sort type to sort by, only types visible in game are usable.
        """
        msg = GCMsgProto(Language.SortItems, sort_type=type)
        await self._state.ws.send_gc_message(msg)
