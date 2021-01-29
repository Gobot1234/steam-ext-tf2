# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, TypeVar

import betterproto

from .base_gcmessages import CsoEconItem
from steam.utils import BytesBuffer

T = TypeVar("T", bound="MessageBase")

# some custom messages to make things a lot easier decoding/encoding wise


class MessageMeta(type):
    def __new__(mcs, name: str, bases: tuple[type, ...], attrs: dict[str, Any]) -> MessageBase:
        attrs["__slots__"] = slots = tuple(attrs.get("__annotations__", ()))
        exec(
            f"def __init__(self, {', '.join(f'{slot}=None' for slot in slots)}): "
            f"{' '.join(f'self.{slot} = {slot};' for slot in slots) or 'pass'}\n"
            f"attrs['__init__'] = __init__"
        )
        return super().__new__(mcs, name, bases, attrs)


class MessageBase(metaclass=MessageMeta):
    def from_dict(self: T, dict: dict[str, Any]) -> T:
        self.__init__(**dict)
        return self

    def to_dict(self, *_) -> dict[str, Any]:
        return {key: getattr(self, key) for key in self.__annotations__}

    def __bytes__(self) -> bytes:
        buffer = BytesBuffer()
        for key in self.__annotations__:
            buffer.write_uint64(getattr(self, key))

        return buffer.getvalue()

    def parse(self: T, data: bytes) -> T:
        ...


class CraftRequest(MessageBase):
    recipe: int
    items: list[int]

    def __bytes__(self) -> bytes:
        buffer = BytesBuffer()
        buffer.write_struct("<hh", self.recipe, len(self.items))
        for item in self.items:
            buffer.write_uint64(item)

        return buffer.getvalue()


class CraftResponse(MessageBase):
    recipe_id: int
    id_list: tuple[int, ...]

    def parse(self, data: bytes) -> CraftResponse:
        buffer = BytesBuffer(data)
        self.recipe_id = buffer.read_int16()
        _ = buffer.read_uint32()  # always 0 in mckay's experience
        id_count = buffer.read_int16()
        self.id_list = buffer.read_struct(f"<{'Q' * id_count}", 8 * id_count)

        return self


class SetItemStyleRequest(MessageBase):
    item_id: int
    style: int

    def __bytes__(self) -> bytes:
        buffer = BytesBuffer()
        buffer.write_uint64(self.item_id)
        buffer.write_uint32(self.style)

        return buffer.getvalue()


class DeleteItemRequest(MessageBase):
    item_id: int


class WrapItemRequest(MessageBase):
    wrapping_paper_id: int
    item_id: int


class UnwrapItemRequest(MessageBase):
    gift_id: int


class DeliverGiftRequest(MessageBase):
    user_id64: int
    gift_id: int


class OpenCrateRequest(MessageBase):
    key_id: int
    crate_id: int


# not strictly a struct message but its one I have to do

@dataclass(eq=False, repr=False)
class UpdateMultipleItems(betterproto.Message):
    owner: int = betterproto.fixed64_field(1)
    objects: List["InnerItem"] = betterproto.message_field(2)
    version: float = betterproto.fixed64_field(3)


@dataclass(eq=False, repr=False)
class InnerItem(betterproto.Message):
    type_id: int = betterproto.uint32_field(1)
    inner: "CsoEconItem" = betterproto.message_field(2)
