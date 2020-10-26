# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Optional

from steam.protobufs import GetProtoType, MsgBase, T
from steam.protobufs.headers import GCMsgHdr, GCMsgHdrProto

from ..enums import Language
from .protobufs import PROTOBUFS


def get_cmsg(emsg: int) -> GetProtoType:
    """Get a protobuf from its EMsg.

    Parameters
    ----------
    emsg: :class:`int`
        The Language of the protobuf.

    Returns
    -------
    Optional[type[:class:`betterproto.Message`]]
        The uninitialized protobuf.
    """
    return PROTOBUFS.get(Language.try_value(emsg))


class GCMsgBase(MsgBase[T]):
    @property
    def msg(self) -> Language:
        """Union[:class:`.Language`, :class:`int`]: The :attr:`header.msg`."""
        return self.header.msg

    @msg.setter
    def msg(self, value: int) -> None:
        self.header.msg = Language.try_value(value)

    def parse(self) -> None:
        """Parse the payload/data into a protobuf."""
        if self.body is None:
            proto = get_cmsg(self.msg)
            self._parse(proto)


class GCMsg(GCMsgBase[T]):
    def __init__(
        self,
        msg: Language,
        data: Optional[bytes] = None,
        **kwargs,
    ):
        self.header = GCMsgHdr(data)
        self.skip = self.header.SIZE
        super().__init__(msg, data, **kwargs)


class GCMsgProto(GCMsgBase[T]):
    def __init__(
        self,
        msg: Language,
        data: Optional[bytes] = None,
        **kwargs,
    ):
        self.header = GCMsgHdrProto(data)
        self.skip = self.header.SIZE + self.header.header_length
        print(data[self.skip:])
        super().__init__(msg, data, **kwargs)
