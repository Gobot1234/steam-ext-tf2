from __future__ import annotations

import re
from collections.abc import Iterable
from contextvars import ContextVar
from typing import TYPE_CHECKING, Optional

from betterproto.casing import pascal_case

from ...trade import BaseInventory, Item
from ...user import User
from .enums import BackpackSortType, ItemFlags, ItemOrigin, ItemQuality, ItemSlot, Mercenary, WearLevel
from .protobufs import base, struct_messages

if TYPE_CHECKING:

    from .state import GCState
    from .types.schema import Schema

__all__ = (
    "BackpackItem",
    "Backpack",
)


WEAR_PARSER = re.compile("|".join(re.escape(wear.name) for wear in WearLevel))
SCHEMA = ContextVar[Schema]("schema")


class BackpackItem(Item):
    """A class to represent an item from the client's backpack.

    Note
    ----
    This is meant to be user instantiable but only to use the following methods:

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
        "custom_description",
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
    )
    REPR_ATTRS = (*Item.REPR_ATTRS, "position", "def_index")
    _state: GCState

    position: int  #: The item's position in the backpack.

    account_id: int  #: Same as the :attr:`steam.SteamID.id` of the :attr:`steam.Client.user`.
    inventory: int  #: The attribute the :attr:`position` is calculated from.
    quantity: int  #: I think this should be the same as :attr:`amount`.
    level: int  #: The item's level.
    flags: ItemFlags  #: The item's flags.
    origin: ItemOrigin  #: The item's origin.
    custom_name: str
    custom_description: str
    attribute: list[base.ItemAttribute]
    interior_item: base.Item
    in_use: bool
    style: int
    original_id: int
    contains_equipped_state: bool
    equipped_state: list[base.ItemEquipped]
    contains_equipped_state_v2: bool

    # the other attribute definitions others not a clue please feel free to PR them

    @property
    def quality(self) -> ItemQuality | None:
        """The item's quality."""
        return self._quality

    @quality.setter
    def quality(self, value: int | str) -> None:
        if isinstance(value, int):
            self._quality = ItemQuality.try_value(value)
        else:
            for tag in self.tags or ():
                if tag.get("category") == "Quality":
                    try:
                        self._quality = ItemQuality[tag["internal_name"].title()]
                    except KeyError:
                        self._quality = None

    async def use(self) -> None:
        """Use this item."""
        await self._state.ws.send_gc_message(base.UseItem(item_id=self.id))

    async def open(self, key: BackpackItem) -> None:
        """Open a crate with a ``key``.

        Parameters
        ----------
        key
            The key to open the crate with.
        """
        await self._state.ws.send_gc_message(struct_messages.OpenCrateRequest( key_id=key.id, crate_id=self.id))

    async def delete(self) -> None:
        """Delete this item."""
        await self._state.ws.send_gc_message(struct_messages.DeleteItemRequest( item_id=self.id))

    async def wrap(self, wrapper: BackpackItem) -> None:
        """Wrap this item with the ``wrapper``.

        Parameters
        ----------
        wrapper
            The wrapping paper to use.
        """
        await self._state.ws.send_gc_message(struct_messages.WrapItemRequest(item_id=self.id, wrapping_paper_id=wrapper.id))

    async def unwrap(self) -> None:
        """Unwrap this item."""
        await self._state.ws.send_gc_message(struct_messages.UnwrapItemRequest(gift_id=self.id))

    async def equip(self, mercenary: Mercenary, slot: ItemSlot) -> None:
        """Equip this item to a mercenary.

        Parameters
        ----------
        mercenary
            The mercenary to equip the item to.
        slot
            The item slot to equip the item to.
        """
        if slot >= ItemSlot.Misc:
            raise ValueError("cannot use enums that aren't real item slots")
        msg = GCMsgProto(Language.AdjustItemEquippedState, item_id=self.id, new_class=mercenary, new_slot=slot)
        await self._state.ws.send_gc_message(msg)

    async def set_position(self, position: int) -> None:
        """Set the position for this item.

        Parameters
        ----------
        position
            The position to set the item to. This is 0 indexed.
        """
        await self._state.backpack.set_positions([(self, position)])

    async def set_style(self, style: int) -> None:
        """Set the style for this item."""
        await self._state.ws.send_gc_message(base.AdjustItemEquippedState(item_id=self.id, style=style))

    async def send_to(self, user: User) -> None:
        """Send this gift-wrapped item to another user.

        Parameters
        ----------
        user
            The user to send this gift wrapped item to.
        """
        await self._state.ws.send_gc_message(struct_messages.DeliverGiftRequest(user_id64=user.id64, gift_id=self.id))

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
                    return ItemSlot.__new__(ItemSlot, name=tag["internal_name"], value=-1)  # type: ignore

    @property
    def def_index(self) -> int:
        """The item's def index. This is used to form the item's SKU."""
        try:
            return self._def_index
        except AttributeError:
            schema = SCHEMA.get()
            for def_index, item in schema["items"].items():
                if item.get("name") == self.name:
                    self._def_index = int(def_index)
                    return self._def_index
            raise RuntimeError(f"Could not find def index for {self.name}")

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
    def from_sku(cls) -> BackpackItem | None:
        """Construct a :class:`BackPackItem` from a sku"""
        self = cls.__new__(cls)
        self.def_index = ...
        return self

    # TODO:
    # - festiveized
    # - effect
    # - to_listing?
    # - from_listing?


class Backpack(BaseInventory[BackpackItem]):
    """A class to represent the client's backpack."""

    __slots__ = ()

    async def set_positions(self, items_and_positions: Iterable[tuple[BackpackItem, int]]) -> None:
        """Set the positions of items in the inventory.

        Parameters
        ----------
        items_and_positions
            A list of (item, position) pairs to set the positions for. This is 0 indexed.
        """
        await self._state.ws.send_gc_message(base.SetItemPositions(
            item_positions=[base.SetItemPositionsItemPosition(item_id=item.id, position=position) for item, position in items_and_positions],
        ))

    async def sort(self, type: BackpackSortType) -> None:
        """Sort this inventory.

        Parameters
        ----------
        type
            The sort type to sort by, only types visible in game are usable.
        """
        await self._state.ws.send_gc_message(base.SortItems(sort_type=type))
