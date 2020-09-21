from steam.protobufs import protobufs

from ..enums import Language
from . import base_gcmessages as messages

"""
protobufs.PROTOBUFS.update(
    {
        Language.ClientWelcome: messages.CMsgClientWelcome,
        Language.ServerWelcome: messages.CMsgServerWelcome,
        Language.ClientGoodbye: messages.CMsgClientGoodbye,
        Language.ServerGoodbye: messages.CMsgServerGoodbye,
        Language.SystemMessage: messages.CMsgSystemBroadcast,
        Language.ClientDisplayNotification: messages.CMsgGcClientDisplayNotification,
        Language.SOCacheSubscriptionCheck: messages.CMsgSOCacheSubscribed,
        Language.SOCacheSubscribed: messages.CSOEconItem,
        Language.SOCreate: messages.CSOEconGameAccountClient,
        Language.SOUpdate: messages.CMsgSOSingleObject,
        Language.SOUpdateMultiple: messages.CSOEconItem,
        Language.SODestroy: messages.CMsgSOSingleObject,
        Language.CraftResponse: messages.CMsgSOMultipleObjects,
        Language.GameServerCreateIdentityResponse: messages.CSOEconItem,
        Language.GameServerListResponse: messages.CSOEconGameAccountClient,
        Language.GameServerResetIdentityResponse: messages.CMsgSOSingleObject,
        Language.WarGlobalStatsResponse: messages.CSOEconItem,
    }
)
"""