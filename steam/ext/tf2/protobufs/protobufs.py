# -*- coding: utf-8 -*-

from steam.protobufs import PROTOBUFS

from ..enums import Language
from . import base_gcmessages as cso_messages, base_gcmessages as messages, gcsdk_gcmessages as so_messages

PROTOBUFS.update(
    {
        Language.ClientWelcome: messages.CMsgClientWelcome,
        Language.ServerWelcome: messages.CMsgServerWelcome,
        Language.ClientGoodbye: messages.CMsgClientGoodbye,
        Language.ServerGoodbye: messages.CMsgServerGoodbye,
        Language.SystemMessage: messages.CMsgSystemBroadcast,
        Language.UpdateItemSchema: messages.CMsgUpdateItemSchema,
        Language.ClientDisplayNotification: messages.CMsgGcClientDisplayNotification,
        Language.SOCacheSubscriptionCheck: so_messages.CMsgSOCacheSubscribed,
        Language.SOUpdate: so_messages.CMsgSOSingleObject,
        Language.SOCreate: so_messages.CMsgSOSingleObject,
        Language.SOUpdateMultiple: so_messages.CMsgSOMultipleObjects,
        Language.GameServerResetIdentityResponse: so_messages.CMsgSOSingleObject,
        Language.SODestroy: so_messages.CMsgSOSingleObject,
        Language.CraftResponse: so_messages.CMsgSOMultipleObjects,
        Language.SOCacheSubscriptionRefresh: so_messages.CMsgSOCacheSubscriptionRefresh,
        Language.SOCacheSubscribed: cso_messages.CsoEconItem,
        Language.GameServerCreateIdentityResponse: cso_messages.CsoEconItem,
        Language.GameServerListResponse: cso_messages.CsoEconGameAccountClient,
        Language.WarGlobalStatsResponse: cso_messages.CsoEconItem,
    }
)
