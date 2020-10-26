# -*- coding: utf-8 -*-

from typing import Generator, TYPE_CHECKING

import steam

if TYPE_CHECKING:
    from .protobufs.base_gcmessages import CsoEconItem, CsoEconItemAttribute, CsoEconItemEquipped

__all__ = (
    "BackPackItem",
    "BackPack",
)


class BackPackItem(steam.Item):
    id: int
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


class BackPack(steam.Inventory):
    items: list[BackPackItem]

    def __iter__(self) -> Generator[BackPackItem, None, None]:
        return super().__iter__()
