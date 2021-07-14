from __future__ import annotations

from ....protobufs.struct_messages import StructMessage
from ....utils import StructIO

# some custom messages to make things a lot easier decoding/encoding wise


class CraftRequest(StructMessage):
    recipe: int
    items: list[int]

    def __bytes__(self) -> bytes:
        buffer = StructIO()
        buffer.write_struct("<hh", self.recipe, len(self.items))
        for item in self.items:
            buffer.write_u64(item)

        return buffer.buffer


class CraftResponse(StructMessage):
    recipe_id: int
    id_list: tuple[int, ...]
    being_used: bool

    def parse(self, data: bytes) -> CraftResponse:
        buffer = StructIO(data)
        self.recipe_id = buffer.read_i16()
        _ = buffer.read_u32()  # always 0 in mckay's experience
        id_count = buffer.read_i16()
        self.id_list = buffer.read_struct(f"<{id_count}Q")
        self.being_used = False

        return self


class SetItemStyleRequest(StructMessage):
    item_id: int
    style: int

    def __bytes__(self) -> bytes:
        buffer = StructIO()
        buffer.write_u64(self.item_id)
        buffer.write_u32(self.style)

        return buffer.buffer


class DeleteItemRequest(StructMessage):
    item_id: int


class WrapItemRequest(StructMessage):
    wrapping_paper_id: int
    item_id: int


class UnwrapItemRequest(StructMessage):
    gift_id: int


class DeliverGiftRequest(StructMessage):
    user_id64: int
    gift_id: int


class OpenCrateRequest(StructMessage):
    key_id: int
    crate_id: int
