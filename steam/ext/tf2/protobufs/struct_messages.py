from __future__ import annotations

from typing_extensions import Self

from ....protobufs.msg import GCMessage
from ....utils import StructIO
from ..enums import Language

# some custom messages to make things a lot easier decoding/encoding wise

class CraftRequest(GCMessage, msg=Language.Craft):
    recipe: int
    items: list[int]

    def __bytes__(self) -> bytes:
        with StructIO() as io:
            io.write_struct("<hh", self.recipe, len(self.items))
            for item in self.items:
                io.write_u64(item)

            return io.buffer


class CraftResponse(GCMessage, msg=Language.CraftResponse):
    recipe_id: int
    id_list: tuple[int, ...]
    being_used: bool

    def parse(self, data: bytes) -> CraftResponse:
        with StructIO(data) as io:
            self.recipe_id = io.read_i16()
            _ = io.read_u32()  # always 0 in mckay's experience
            id_count = io.read_i16()
            self.id_list = io.read_struct(f"<{id_count}Q")
            self.being_used = False

        return self


class SetItemStyleRequest(GCMessage, msg=Language.SetItemStyle):
    item_id: int
    style: int

    def __bytes__(self) -> bytes:
        with StructIO() as io:
            io.write_u64(self.item_id)
            io.write_u32(self.style)

            return io.buffer


class DeleteItemRequest(GCMessage, msg=Language.Delete):
    item_id: int


class WrapItemRequest(GCMessage, msg=Language.GiftWrapItem):
    wrapping_paper_id: int
    item_id: int


class UnwrapItemRequest(GCMessage, msg=Language.UnwrapGiftRequest):
    gift_id: int


class DeliverGiftRequest(GCMessage, msg=Language.DeliverGift):
    user_id64: int
    gift_id: int


class OpenCrateRequest(GCMessage, msg=Language.UnlockCrate):
    key_id: int
    crate_id: int


class CacheSubscribedCheck(GCMessage, msg=Language.SOCacheSubscriptionCheck):
    def parse(self, data: bytes) -> Self:
        return self  # IDK how to decode this but I don't want to have to special case this
