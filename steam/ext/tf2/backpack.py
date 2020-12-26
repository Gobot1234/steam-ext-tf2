# -*- coding: utf-8 -*-

from __future__ import annotations

import inspect
import re
from typing import Optional, TYPE_CHECKING, TypeVar

from betterproto.casing import pascal_case

from ...enums import _is_descriptor
from ...user import User
from ...trade import Inventory, Item
from ...protobufs import GCMsg, GCMsgProto
from .enums import BackpackSortType, Mercenary, ItemQuality, ItemSlot, Language, WearLevel
from .protobufs.base_gcmessages import CsoEconItem

if TYPE_CHECKING:
    from .state import GCState

__all__ = (
    "BackPackItem",
    "BackPack",
)


WEARS: dict[str, WearLevel] = {
    "(Battle Scarred)": WearLevel.BattleScarred,
    "(Well-Worn)": WearLevel.WellWorn,
    "(Field-Tested)": WearLevel.FieldTested,
    "(Minimal Wear)": WearLevel.MinimalWear,
    "(Factory New)": WearLevel.FactoryNew,
}
WEAR_PARSER = re.compile("|".join(wear.replace("(", "\(").replace(")", "\)") for wear in WEARS))
BPI = TypeVar("BPI", bound="BackPackItem")


class BackPackItem(Item):
    """A class to represent an item from the client's backpack.

    Attributes
    ----------
    id: :class:`int`
        An alias for :attr:`asset_id`.
    quality: :class:`ItemQuality`
        The item's quality.
    """

    # others not a clue please feel to PR them

    __slots__ = (
        "position",
        "_state",
    ) + tuple(CsoEconItem.__annotations__)

    position: int
    quality: Optional[ItemQuality]

    def __init__(self, item: Item, state: GCState):  # noqa
        for name, attr in inspect.getmembers(item, predicate=lambda attr: not _is_descriptor(attr)):
            if not (name.startswith("__") and name.endswith("__")):
                try:
                    setattr(self, name, attr)
                except (AttributeError, TypeError):
                    pass
        try:
            self.quality = ItemQuality.try_value(self.quality)
        except AttributeError:
            for tag in self.tags:
                if tag.get("category") == "Quality":
                    self.quality = getattr(ItemQuality, tag["internal_name"], None)

        self._state = state

    def __repr__(self) -> str:
        item_repr = super().__repr__()[6:-1]
        resolved = [item_repr]
        attrs = ("position",)
        resolved.extend(f"{attr}={getattr(self, attr, None)!r}" for attr in attrs)
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

    async def equip(self, mercenary: Mercenary, slot: ItemSlot) -> None:
        """|coro|
        Equip this item to a mercenary.

        Parameters
        ----------
        mercenary: :class:`Mercenary`
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

    async def send_to(self, user: User) -> None:
        """|coro|
        Send this gift-wrapped item to another user.

        Parameters
        ----------
        user: :class:`steam.User`
            The user to send this gift wrapped item to.
        """
        msg = GCMsg(Language.DeliverGift, user_id64=user.id64, gift_id=self.id)
        await self._state.ws.send_gc_message(msg)

    # methods similar to https://github.com/danocmx/node-tf2-item-format

    def is_australium(self) -> bool:
        return "Australium" in self.name and self.name != "Australium Gold"

    def is_craftable(self) -> bool:
        return all(description.get("value") != "( Not Usable in Crafting )" for description in self.descriptions)

    def is_unusual(self) -> bool:
        return self.quality == ItemQuality.Unusual

    @property
    def wear(self) -> Optional[WearLevel]:
        wear = WEAR_PARSER.findall(self.name)
        return WEARS[wear[0]] if wear else None

    @property
    def equipable_by(self) -> list[Mercenary]:
        tags = [dict for dict in self.tags if dict.get("category") == "Class"]
        return [Mercenary[mercenary["internal_name"]] for mercenary in tags]

    @property
    def slot(self) -> Optional[ItemSlot]:
        for tag in self.tags:  # Craft_Item and Tf_Gift fail this
            if tag.get("category") == "Type" and "internal_name" in tag:
                try:
                    return ItemSlot[
                        pascal_case(tag["internal_name"], strict=False).replace("Pda", "PDA").replace("Tf_Gift", "Gift")
                    ]
                except KeyError:
                    return tag["internal_name"]

    # TODO:
    # - festiveized
    # - effect
    # - to_sku
    # - from_sku?
    # - to_listing?
    # - from_listing?


if TYPE_CHECKING:

    class BackPackItem(BackPackItem, CsoEconItem):
        # We don't want the extra bloat of betterproto.Message at runtime but we do want its fields
        ...


class BackPack(Inventory[BPI]):
    """A class to represent the client's backpack."""

    items: list[BPI]

    def __init__(self, inventory: Inventory):  # noqa
        for name, attr in inspect.getmembers(inventory, lambda attr: not _is_descriptor(attr)):
            if not (name.startswith("__") and name.endswith("__")):
                try:
                    setattr(self, name, attr)
                except (AttributeError, TypeError):
                    pass
        self.items = [BackPackItem(item, self._state) for item in inventory.items]

    async def set_positions(self, items_and_positions: list[tuple[BackPackItem, int]]) -> None:
        """|coro|
        Set the positions of items in the inventory.

        Parameters
        ----------
        items_and_positions: list[tuple[:class:`BackPackItem`, int]]
            A list of (item, position) pairs to set the positions for.
        """
        # TODO is this 0 indexed?
        # Warning this crashes the bot atm
        msg = GCMsgProto(
            Language.SetItemPositions,
            item_positions=[{"item_id": item.id, "position": position} for item, position in items_and_positions],
        )
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
