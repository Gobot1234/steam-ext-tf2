from __future__ import annotations

import re
from collections.abc import Iterable
from typing import TYPE_CHECKING, Optional

from betterproto.casing import pascal_case

from ... import utils
from ...protobufs import GCMsg, GCMsgProto
from ...trade import BaseInventory, Inventory, Item
from ...user import User
from .enums import BackpackSortType, ItemQuality, ItemSlot, Language, Mercenary, WearLevel

if TYPE_CHECKING:
    from .protobufs.base_gcmessages import CsoEconItem, CsoEconItemAttribute, CsoEconItemEquipped
    from .schema import Schema
    from .state import GCState

__all__ = (
    "BackPackItem",
    "BackPack",
)


WEAR_PARSER = re.compile("|".join(re.escape(wear.name) for wear in WearLevel))


def load_schema() -> Schema:
    try:
        from .state import SCHEMA
    except AttributeError:  # I don't really know how you can feasibly get this but ¯\_(ツ)_/¯
        raise RuntimeError("Cannot get schema when not logged into GC")
    return SCHEMA


class BackPackItem(Item):
    """A class to represent an item from the client's backpack.

    Note
    ----
    This is meant to be user instantiatable but only to use the following methods:

        - :meth:`is_australium`
        - :meth:`is_craftable`
        - :meth:`is_unusual`
        - :attr:`wear`
        - :attr:`equipable_by`
        - :attr:`slot`
    """

    __slots__ = (
        "position",
        "account_id",
        "inventory",
        "quantity",
        "level",
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
        "_quality",
        "_def_index",
        "_state",
    )
    REPR_ATTRS = (*Item.REPR_ATTRS, "position")

    position: int  #: The item's position in the backpack.

    account_id: int  #: Same as the :attr:`steam.SteamID.id` of the :attr:`steam.Client.user`.
    inventory: int  #: The attribute the :attr:`position` is calculated from.
    quantity: int  #: I think this should be the same as :attr:`amount`.
    level: int  #: The item's level.
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

    # the other attribute definitions others not a clue please feel free to PR them

    def __init__(self, item: Item, *, _state: Optional[GCState] = None):  # noqa
        utils.update_class(item, self)
        self._state = _state

    def __repr__(self) -> str:
        item_repr = super().__repr__()[6:-1]
        resolved = [item_repr]
        attrs = ("position",)
        resolved.extend(f"{attr}={getattr(self, attr, None)!r}" for attr in attrs)
        return f"<BackPackItem {' '.join(resolved)}>"

    @property
    def id(self) -> int:
        """An alias for :attr:`asset_id`, with extra checking that you own the item."""
        if self._state is None:
            raise ValueError("cannot access the id of items you don't own")
        return self.asset_id

    @id.setter
    def id(self, value: int) -> None:
        ...  # assignments should just do nothing.

    @property
    def quality(self) -> ItemQuality | None:
        """The item's quality."""
        return self._quality

    @quality.setter
    def quality(self, value: int | str) -> None:
        if isinstance(value, int):
            self._quality = ItemQuality.try_value(value)
        else:
            for tag in self.tags:
                if tag.get("category") == "Quality":
                    try:
                        self._quality = ItemQuality[tag["internal_name"].title()]
                    except KeyError:
                        self._quality = None

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
        key
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
        wrapper
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
        mercenary
            The mercenary to equip the item to.
        slot
            The item slot to equip the item to.
        """
        if slot >= 100:
            raise ValueError("cannot use enums that aren't real item slots")
        msg = GCMsgProto(Language.AdjustItemEquippedState, item_id=self.id, new_class=mercenary, new_slot=slot)
        await self._state.ws.send_gc_message(msg)

    async def set_position(self, position: int) -> None:
        """|coro|
        Set the position for this item.

        Parameters
        ----------
        position
            The position to set the item to. This is 0 indexed.
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
        user
            The user to send this gift wrapped item to.
        """
        msg = GCMsg(Language.DeliverGift, user_id64=user.id64, gift_id=self.id)
        await self._state.ws.send_gc_message(msg)

    # methods similar to https://github.com/danocmx/node-tf2-item-format

    def is_australium(self) -> bool:
        """Whether or not the item is australium."""
        return "Australium" in self.name and self.name != "Australium Gold"

    def is_craftable(self) -> bool:
        """Whether or not the item is craftable."""
        return all(description.get("value") != "( Not Usable in Crafting )" for description in self.descriptions)

    def is_unusual(self) -> bool:
        """Whether or not the item is unusual."""
        return self.quality == ItemQuality.Unusual

    @property
    def wear(self) -> Optional[WearLevel]:
        """The item's wear level."""
        wear = WEAR_PARSER.findall(self.name)
        return WearLevel[wear[0]] if wear else None

    @property
    def equipable_by(self) -> list[Mercenary]:
        """The mercenaries the item is equipable."""
        tags = [tag for tag in self.tags if tag.get("category") == "Class"]
        return [Mercenary[mercenary["internal_name"]] for mercenary in tags]

    @property
    def slot(self) -> Optional[ItemSlot]:
        """The item's equip slot."""
        for tag in self.tags:
            if tag.get("category") == "Type" and "internal_name" in tag:
                try:
                    return ItemSlot[
                        pascal_case(tag["internal_name"], strict=False)
                        .replace("Pda", "PDA")
                        .replace("Tf_Gift", "Gift")
                        .replace("Craft_Item", "CraftItem")
                    ]
                except KeyError:
                    return tag["internal_name"]

    @property
    def def_index(self) -> int:
        """The item's def index. This is used to form the item's SKU."""
        try:
            return self._def_index
        except AttributeError:
            schema = load_schema()
            for def_index, item in schema["items"].items():
                if item.get("name") == self.name:
                    self._def_index = def_index
                    return def_index

    @def_index.setter
    def def_index(self, value: int) -> None:
        self._def_index = value

    # @property
    # def unusual_effect(self):
    #     print()

    @property
    def sku(self) -> str:
        """The item's SKU."""
        parts = [self.def_index, ";", self.quality.value]

        # if self.unusual:
        #     parts.append(f";u{self.unusual.value}")

        if self.is_australium():
            parts.append(";australium")

        if not self.is_craftable():
            parts.append(";uncraftable")

        if self.wear:
            parts.append(f";w{self.wear.value}")  # TODO check

        # if self.texture:
        #     parts.append(f";pk{self.texture}")
        #
        # if self.elevated:
        #     parts.append(";strange")
        #
        # if self.killstreak:
        #     parts.append(f";kt-{self.killstreak}")
        #
        # if self.defindex:
        #     parts.append(f";td-{self.targetDefindex}")
        #
        # if self.festivized:
        #     parts.append(";festive")
        #
        # if self.craft_number:
        #     parts.append(f";n{self.selfNumber.value}")
        #
        # if self.crate_number:
        #     parts.append(f";c{self.selfNumber.value}")

        return "".join(parts)

    @classmethod
    def from_sku(cls) -> BackPackItem | None:
        """Construct a :class:`BackPackItem` from a sku"""
        self = cls.__new__(cls)
        self.def_index = ...
        return self

    # TODO:
    # - festiveized
    # - effect
    # - to_listing?
    # - from_listing?


class BackPack(BaseInventory[BackPackItem]):
    """A class to represent the client's backpack."""

    __slots__ = ()

    def __init__(self, inventory: Inventory):  # noqa
        utils.update_class(inventory, self)
        self.__class__ = BackPack
        self.items = [BackPackItem(item, _state=self._state) for item in inventory.items]  # type: ignore

    async def update(self) -> None:
        await super().update()
        self.items = [BackPackItem(item, _state=self._state) for item in self.items]  # type: ignore
        pass

    async def set_positions(self, items_and_positions: Iterable[tuple[BackPackItem, int]]) -> None:
        """|coro|
        Set the positions of items in the inventory.

        Parameters
        ----------
        items_and_positions
            A list of (item, position) pairs to set the positions for. This is 0 indexed.
        """
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
        type
            The sort type to sort by, only types visible in game are usable.
        """
        msg = GCMsgProto(Language.SortItems, sort_type=type)
        await self._state.ws.send_gc_message(msg)
