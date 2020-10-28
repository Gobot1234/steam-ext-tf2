# -*- coding: utf-8 -*-

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Iterator

import steam

if TYPE_CHECKING:
    from .enums import BackpackSortType
    from .protobufs.base_gcmessages import CsoEconItem, CsoEconItemAttribute, CsoEconItemEquipped

__all__ = (
    "BackPackItem",
    "BackPack",
)


class BackPackItem(steam.Item):
    """A class to represent an item from the client's backpack."""

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
    )

    def __init__(self, item: steam.Item):
        for name, attr in inspect.getmembers(item):
            try:
                setattr(self, name, attr)
            except (AttributeError, TypeError):
                pass
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
        attribute: list["CsoEconItemAttribute"]
        interior_item: "CsoEconItem"
        in_use: bool
        style: int
        original_id: int
        contains_equipped_state: bool
        equipped_state: list["CsoEconItemEquipped"]
        contains_equipped_state_v2: bool

    def __repr__(self) -> str:
        item_repr = super().__repr__()[6:-1]
        resolved = [item_repr]
        attrs = ("position",)
        resolved.extend(f"{attr}={getattr(self, attr)!r}" for attr in attrs)
        return f"<BackPackItem {' '.join(resolved)}>"

    async def delete(self) -> None:
        pass

    async def set_position(self, position: int) -> None:
        pass

    async def set_style(self, style: int) -> None:
        pass


class BackPack(steam.Inventory):
    """A class to represent the client's backpack."""

    def __init__(self, inventory: steam.Inventory):
        for name, attr in inspect.getmembers(inventory):
            try:
                setattr(self, name, attr)
            except (AttributeError, TypeError):
                pass
        self.items: list[BackPackItem] = [BackPackItem(item) for item in inventory.items]

    def __iter__(self) -> Iterator[BackPackItem]:
        return iter(self.items)

    async def sort(self, type: BackpackSortType) -> None:
        pass  # this may need to make the inventory be refetched?
