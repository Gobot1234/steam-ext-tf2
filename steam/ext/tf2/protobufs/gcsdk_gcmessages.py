# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: gcsdk_gcmessages.proto
# plugin: python-betterproto

from dataclasses import dataclass
from typing import List

import betterproto


class PartnerAccountType(betterproto.Enum):
    NONE = 0
    PerfectWorld = 1
    Nexon = 2


class GCConnectionStatus(betterproto.Enum):
    HaveSession = 0
    GcGoingDown = 1
    NoSession = 2
    NoSessionInLogonQueue = 3
    NoSteam = 4
    Suspended = 5


@dataclass(eq=False, repr=False)
class CMsgSOIDOwner(betterproto.Message):
    type: int = betterproto.uint32_field(1)
    id: int = betterproto.uint64_field(2)


@dataclass(eq=False, repr=False)
class CMsgSOSingleObject(betterproto.Message):
    owner: float = betterproto.fixed64_field(1)
    type_id: int = betterproto.int32_field(2)
    object_data: bytes = betterproto.bytes_field(3)
    version: float = betterproto.fixed64_field(4)
    owner_soid: "CMsgSOIDOwner" = betterproto.message_field(5)
    service_id: int = betterproto.uint32_field(6)


@dataclass(eq=False, repr=False)
class CMsgSOMultipleObjects(betterproto.Message):
    owner: float = betterproto.fixed64_field(1)
    objects: List["CMsgSOMultipleObjectsSingleObject"] = betterproto.message_field(2)
    version: float = betterproto.fixed64_field(3)
    owner_soid: "CMsgSOIDOwner" = betterproto.message_field(6)
    service_id: int = betterproto.uint32_field(7)


@dataclass(eq=False, repr=False)
class CMsgSOMultipleObjectsSingleObject(betterproto.Message):
    type_id: int = betterproto.int32_field(1)
    object_data: bytes = betterproto.bytes_field(2)


@dataclass(eq=False, repr=False)
class CMsgSOCacheSubscribed(betterproto.Message):
    owner: float = betterproto.fixed64_field(1)
    objects: List["CMsgSOCacheSubscribedSubscribedType"] = betterproto.message_field(2)
    version: float = betterproto.fixed64_field(3)
    owner_soid: "CMsgSOIDOwner" = betterproto.message_field(4)
    service_id: int = betterproto.uint32_field(5)
    service_list: List[int] = betterproto.uint32_field(6)
    sync_version: float = betterproto.fixed64_field(7)


@dataclass(eq=False, repr=False)
class CMsgSOCacheSubscribedSubscribedType(betterproto.Message):
    type_id: int = betterproto.int32_field(1)
    object_data: List[bytes] = betterproto.bytes_field(2)


@dataclass(eq=False, repr=False)
class CMsgSOCacheSubscribedUpToDate(betterproto.Message):
    version: float = betterproto.fixed64_field(1)
    owner_soid: "CMsgSOIDOwner" = betterproto.message_field(2)
    service_id: int = betterproto.uint32_field(3)
    service_list: List[int] = betterproto.uint32_field(4)
    sync_version: float = betterproto.fixed64_field(5)


@dataclass(eq=False, repr=False)
class CMsgSOCacheUnsubscribed(betterproto.Message):
    owner: float = betterproto.fixed64_field(1)


@dataclass(eq=False, repr=False)
class CMsgSOCacheSubscriptionCheck(betterproto.Message):
    owner: float = betterproto.fixed64_field(1)
    version: float = betterproto.fixed64_field(2)
    owner_soid: "CMsgSOIDOwner" = betterproto.message_field(3)
    service_id: int = betterproto.uint32_field(4)
    service_list: List[int] = betterproto.uint32_field(5)
    sync_version: float = betterproto.fixed64_field(6)


@dataclass(eq=False, repr=False)
class CMsgSOCacheSubscriptionRefresh(betterproto.Message):
    owner: float = betterproto.fixed64_field(1)
    owner_soid: "CMsgSOIDOwner" = betterproto.message_field(2)


@dataclass(eq=False, repr=False)
class CMsgSOCacheVersion(betterproto.Message):
    version: float = betterproto.fixed64_field(1)


@dataclass(eq=False, repr=False)
class CMsgGCMultiplexMessage(betterproto.Message):
    msgtype: int = betterproto.uint32_field(1)
    payload: bytes = betterproto.bytes_field(2)
    steamids: List[float] = betterproto.fixed64_field(3)


@dataclass(eq=False, repr=False)
class CGCToGCMsgMasterAck(betterproto.Message):
    dir_index: int = betterproto.uint32_field(1)
    machine_name: str = betterproto.string_field(3)
    process_name: str = betterproto.string_field(4)
    type_instances: List[int] = betterproto.uint32_field(5)


@dataclass(eq=False, repr=False)
class CGCToGCMsgMasterAckResponse(betterproto.Message):
    eresult: int = betterproto.int32_field(1)


@dataclass(eq=False, repr=False)
class CGCToGCMsgMasterStartupComplete(betterproto.Message):
    gc_info: List["CGCToGCMsgMasterStartupCompleteGCInfo"] = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class CGCToGCMsgMasterStartupCompleteGCInfo(betterproto.Message):
    dir_index: int = betterproto.uint32_field(1)
    machine_name: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class CGCToGCMsgRouted(betterproto.Message):
    msg_type: int = betterproto.uint32_field(1)
    sender_id: float = betterproto.fixed64_field(2)
    net_message: bytes = betterproto.bytes_field(3)


@dataclass(eq=False, repr=False)
class CGCToGCMsgRoutedReply(betterproto.Message):
    msg_type: int = betterproto.uint32_field(1)
    net_message: bytes = betterproto.bytes_field(2)


@dataclass(eq=False, repr=False)
class CMsgGCUpdateSubGCSessionInfo(betterproto.Message):
    updates: List["CMsgGCUpdateSubGCSessionInfoCMsgUpdate"] = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class CMsgGCUpdateSubGCSessionInfoCMsgUpdate(betterproto.Message):
    steamid: float = betterproto.fixed64_field(1)
    ip: float = betterproto.fixed32_field(2)
    trusted: bool = betterproto.bool_field(3)


@dataclass(eq=False, repr=False)
class CMsgGCRequestSubGCSessionInfo(betterproto.Message):
    steamid: float = betterproto.fixed64_field(1)


@dataclass(eq=False, repr=False)
class CMsgGCRequestSubGCSessionInfoResponse(betterproto.Message):
    ip: float = betterproto.fixed32_field(1)
    trusted: bool = betterproto.bool_field(2)


@dataclass(eq=False, repr=False)
class CMsgGCToGCIncrementRecruitmentLevel(betterproto.Message):
    steamid: float = betterproto.fixed64_field(1)


@dataclass(eq=False, repr=False)
class CMsgSOCacheHaveVersion(betterproto.Message):
    soid: "CMsgSOIDOwner" = betterproto.message_field(1)
    version: float = betterproto.fixed64_field(2)
    service_id: int = betterproto.uint32_field(3)


@dataclass(eq=False, repr=False)
class CMsgConnectionStatus(betterproto.Message):
    status: "GCConnectionStatus" = betterproto.enum_field(1)
    client_session_need: int = betterproto.uint32_field(2)
    queue_position: int = betterproto.int32_field(3)
    queue_size: int = betterproto.int32_field(4)
    wait_seconds: int = betterproto.int32_field(5)
    estimated_wait_seconds_remaining: int = betterproto.int32_field(6)


@dataclass(eq=False, repr=False)
class CMsgGCToGCSOCacheSubscribe(betterproto.Message):
    subscriber: float = betterproto.fixed64_field(1)
    subscribe_to: float = betterproto.fixed64_field(2)
    sync_version: float = betterproto.fixed64_field(3)
    have_versions: List["CMsgGCToGCSOCacheSubscribeCMsgHaveVersions"] = betterproto.message_field(4)


@dataclass(eq=False, repr=False)
class CMsgGCToGCSOCacheSubscribeCMsgHaveVersions(betterproto.Message):
    service_id: int = betterproto.uint32_field(1)
    version: int = betterproto.uint64_field(2)


@dataclass(eq=False, repr=False)
class CMsgGCToGCSOCacheUnsubscribe(betterproto.Message):
    subscriber: float = betterproto.fixed64_field(1)
    unsubscribe_from: float = betterproto.fixed64_field(2)


@dataclass(eq=False, repr=False)
class CMsgGCClientPing(betterproto.Message):
    pass
