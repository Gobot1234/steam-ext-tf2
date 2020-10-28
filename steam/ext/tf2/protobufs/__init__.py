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
