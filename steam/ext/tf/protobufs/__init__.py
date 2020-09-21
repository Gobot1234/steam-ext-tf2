from __future__ import annotations

from steam.protobufs import MsgBase, T
from steam.protobufs.headers import GCMsgHdr, GCMsgHdrProto

from ..enums import Language


class GCMsg(MsgBase[T]):
    def __init__(self, msg: Language, data: bytes, parse: bool, **kwargs):
        self.header = GCMsgHdr(data)
        self.proto = False
        self.skip = self.header.SIZE
        super().__init__(msg, data, parse, **kwargs)
        self.msg = Language.try_value(msg)

    def parse(self, proto: type[T]) -> None:
        pass


class GCMsgProto(MsgBase[T]):
    def __init__(self, msg: Language, data: bytes, parse: bool, **kwargs):
        self.header = GCMsgHdrProto(data)
        self.proto = True
        self.skip = self.header.SIZE
        super().__init__(msg, data, parse, **kwargs)
        self.msg = Language.try_value(msg)

    def parse(self, proto: type[T]) -> None:
        pass

