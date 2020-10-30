# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Any

from ..utils import BytesBuffer

# some custom messages to make things a lot easier decoding/encoding wise


class MessageBase:
    def __init__(self, **kwargs):
        for key in self.__annotations__:
            setattr(self, key, None)

        for key, value in kwargs.items():
            if key not in self.__annotations__:
                raise TypeError(f"__init__ got an unexpected key word argument {key}")
            setattr(self, key, value)

    def from_dict(self, dict: dict[str, Any]) -> MessageBase:
        for key, value in dict.items():
            if key not in self.__annotations__:
                raise TypeError(f"{self.__class__.__name__} got an unexpected key word argument {key}")
            setattr(self, key, value)

        return self

    def to_dict(self) -> dict[str, Any]:
        return {key: getattr(self, key) for key in self.__annotations__}

    def __bytes__(self) -> bytes:
        buffer = BytesBuffer()
        for key in self.__annotations__:
            buffer.write_uint64(getattr(self, key))

        return buffer.getvalue()


class CraftRequest(MessageBase):
    recipe: int
    items: list[int]

    def __bytes__(self) -> bytes:
        buffer = BytesBuffer()
        buffer.write_int16(self.recipe)
        buffer.write_int16(len(self.items))
        for item in self.items:
            buffer.write_uint64(item)

        return buffer.getvalue()


class CraftResponse(MessageBase):
    blueprint: int
    unknown: int
    id_list: list[int]

    def parse(self, data: bytes) -> CraftResponse:
        buffer = BytesBuffer(data)
        self.blueprint = buffer.read_int16()
        self.unknown = buffer.read_uint32()
        id_count = buffer.read_int16()
        self.id_list = [buffer.read_uint64() for _ in range(id_count)]

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
