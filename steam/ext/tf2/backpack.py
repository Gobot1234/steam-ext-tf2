from __future__ import annotations

import re
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, Optional

from betterproto.casing import pascal_case
from typing_extensions import Literal, TypedDict

from ... import utils
from ...protobufs import GCMsg, GCMsgProto
from ...trade import Inventory, Item
from ...user import User
from .enums import BackpackSortType, ItemQuality, ItemSlot, Language, Mercenary, WearLevel
from .protobufs.base_gcmessages import CsoEconItem

if TYPE_CHECKING:
    from .state import GCState

__all__ = (
    "BackPackItem",
    "BackPack",
)


WEAR_PARSER = re.compile("|".join(re.escape(wear.name) for wear in WearLevel))
Bools = Literal["0", "1"]


class ValueDict(TypedDict):
    value: int


class ColorDict(TypedDict):  # I'm sorry my fellow tea drinkers
    color_name: str


class RaririesDict(TypedDict):
    value: int
    loc_key: str
    loc_key_weapon: str
    color: str
    next_rarity: NotRequired[str]


class EquipConflicts(TypedDict):
    glasses: dict[str, int]
    whole_head: dict[str, int]


class CollectionDict(TypedDict):
    name: str
    description: str
    is_reference_collection: Bools
    items: dict[str, int]


class OperationInfo(TypedDict):
    name: str
    gateway_item_name: str
    required_item_name: str
    operation_start_date: str  # format of "2017-10-15 00:00:00" and "2038-01-01 00:00:00"
    stop_adding_to_queue_date: str
    stop_giving_to_player_date: str
    contracts_end_date: str  # all datetimes with above format
    quest_log_res_file: NotRequired[str]
    quest_list_res_file: NotRequired[str]
    operation_lootlist: str
    is_campaign: Literal[0, 1]
    max_drop_count: NotRequired[int]


class ItemInfo(TypedDict):
    name: str
    prefab: str
    item_name: str
    item_description: str
    image_inventory: str


class AttributeInfo(TypedDict):
    name: str
    attribute_class: str
    description_string: NotRequired[str]
    description_format: str
    hidden: Bools
    effect_type: Literal["positive", "neutral", "negative"]
    stored_as_integer: Bools
    armory_desc: NotRequired[str]


class ItemSet(TypedDict):
    name: str
    items: dict[str, Literal["1"]]
    attributes: dict[str, dict[str, str]]
    store_bundle: NotRequired[str]


class CraftInfo(TypedDict):
    name: str
    n_A: str
    desc_inputs: str
    desc_outputs: str
    di_A: str
    di_B: str
    do_A: str
    do_B: str
    all_same_class: NotRequired[Bools]
    always_known: Bools
    premium_only: Bools
    disabled: Bools
    input_items: dict[
        str,
    ]


class Schema(TypedDict):
    game_info: dict[str, int]
    qualities: dict[str, ValueDict]
    colors: dict[str, ColorDict]
    rarities: dict[str, RaririesDict]
    equip_regions_list: dict[str, Literal[0, 1] | dict[Literal["shared"], Bools]]
    equip_conflicts: dict[str, dict[str, Bools]]
    quest_objective_conditions: list  # this is not really possible to type
    item_series_types: dict[str, dict[str, Any]]
    item_collections: dict[str, CollectionDict]
    operations: dict[int, OperationInfo]
    prefabs: dict[str, dict[str, Any]]  # there are too many options for this for me to type them for now TODO
    items: dict[int, ItemInfo]
    attributes: dict[str, AttributeInfo]
    item_criteria_templates: dict[str, dict[str, str]]
    random_attribute_templates: dict[str, dict[str, str]]
    lootlist_job_template_definitions: dict[str, dict[str, str]]
    item_sets: dict[str, ItemSet]
    client_loot_lists: dict[str, str | dict[str, Literal["1"]]]
    revolving_loot_lists: dict[str, str]
    recipes: dict[str, CraftInfo]
    achievement_rewards: dict[str, str | dict[str, str | dict[str, str]]]


def load_schema() -> Schema:
    try:
        from .state import SCHEMA
    except AttributeError:  # I don't really know how you can feasibly get this but ¯\_(ツ)_/¯
        raise RuntimeError("Cannot get schema when not logged into GC")
    return SCHEMA


cso_slots = CsoEconItem.__annotations__.copy()
del cso_slots["id"]
del cso_slots["quality"]
del cso_slots["def_index"]


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

    Attributes
    ----------
    id: :class:`int`
        An alias for :attr:`asset_id`.
    position: :class:`int`
        The item's position in the backpack.
    account_id: :class:`int`
        Same as the :attr:`steam.SteamID.id` of the :attr:`steam.Client.user`.
    inventory: :class:`int`
        The attribute the :attr:`position` is calculated from.
    level: :class:`int`
        The item's level.
    """

    # others not a clue please feel free to PR them

    __slots__ = ("position", "_quality", "_def_index", "_state", *cso_slots)

    position: int
    quality: Optional[ItemQuality]

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
        if self._state is None:
            raise ValueError("cannot access the id of items you don't own")
        return self.asset_id

    @id.setter
    def id(self, value: int) -> None:
        ...  # assignments should just do nothing.

    @property
    def quality(self) -> ItemQuality | None:
        """Optional[:class:`ItemQuality`]: The item's quality."""
        return self._quality

    @quality.setter
    def quality(self, value: int | str) -> None:
        try:
            self._quality = ItemQuality.try_value(value)
        except AttributeError:
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
        if slot >= 100:
            raise ValueError("cannot use enums that aren't real item slots")
        msg = GCMsgProto(Language.AdjustItemEquippedState, item_id=self.id, new_class=mercenary, new_slot=slot)
        await self._state.ws.send_gc_message(msg)

    async def set_position(self, position: int) -> None:
        """|coro|
        Set the position for this item.

        Parameters
        ----------
        position: :class:`int`
            The position to set the item to. This is 0 indexed
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
        return WearLevel[wear[0]] if wear else None

    @property
    def equipable_by(self) -> list[Mercenary]:
        tags = [tag for tag in self.tags if tag.get("category") == "Class"]
        return [Mercenary[mercenary["internal_name"]] for mercenary in tags]

    @property
    def slot(self) -> Optional[ItemSlot]:
        for tag in self.tags:  # Craft_Item and Tf_Gift fail this
            if tag.get("category") == "Type" and "internal_name" in tag:
                try:
                    return ItemSlot[
                        pascal_case(tag["internal_name"], strict=False)
                        .replace("Pda", "PDA")
                        .replace("Tf_Gift", "Gift")
                        .replace("Craft Item", "CraftItem")
                    ]
                except KeyError:
                    return tag["internal_name"]

    @property
    def def_index(self) -> int:
        """:class:`int`: The item's def index. This is used to form the item's SKU."""
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
        parts = [self.defindex, ";", self.quality.value]

        if self.unusual:
            parts.append(f";u{self.unusual.value}")

        if self.is_australium():
            parts.append(";australium")

        if not self.is_craftable():
            parts.append(";uncraftable")

        if self.wear:
            parts.append(f";w{self.wear}")  # TODO check

        if self.texture:
            parts.append(f";pk{self.texture}")

        if self.elevated:
            parts.append(";strange")

        if self.killstreak:
            parts.append(f";kt-{self.killstreak}")

        # if self.defindex:
        #     parts.append(f";td-{self.targetDefindex}")

        if self.festivized:
            parts.append(";festive")

        if self.craft_number:
            parts.append(f";n{self.selfNumber.value}")

        if self.crate_number:
            parts.append(f";c{self.selfNumber.value}")

        return "".join(parts)

    @classmethod
    def from_sku(cls):
        self = cls.__new__(cls)
        self.def_index = ...
        return self

    # TODO:
    # - festiveized
    # - effect
    # - to_listing?
    # - from_listing?


if TYPE_CHECKING:

    class BackPackItem(BackPackItem, CsoEconItem):
        # We don't want the extra bloat of betterproto.Message at runtime but we do want its fields
        ...


class BackPack(Inventory[BackPackItem]):
    """A class to represent the client's backpack."""

    def __init__(self, inventory: Inventory):  # noqa
        utils.update_class(inventory, self)
        self.items = [BackPackItem(item, _state=self._state) for item in inventory.items]  # type: ignore

    async def set_positions(self, items_and_positions: Iterable[tuple[BackPackItem, int]]) -> None:
        """|coro|
        Set the positions of items in the inventory.

        Parameters
        ----------
        items_and_positions: Iterable[tuple[:class:`BackPackItem`, :class:`int`]]
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
        type: :class:`BackpackSortType`
            The sort type to sort by, only types visible in game are usable.
        """
        msg = GCMsgProto(Language.SortItems, sort_type=type)
        await self._state.ws.send_gc_message(msg)
