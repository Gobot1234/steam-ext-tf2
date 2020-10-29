# -*- coding: utf-8 -*-

from steam.protobufs import PROTOBUFS

from ..enums import Language
from . import base_gcmessages as cso_messages, gcsdk_gcmessages as so_messages, struct_messages

GCMsgs = {
    Language.SOUpdate: so_messages.CMsgSOSingleObject,
    Language.SOCreate: so_messages.CMsgSOSingleObject,
    Language.SOUpdateMultiple: so_messages.CMsgSOMultipleObjects,
    Language.GameServerResetIdentityResponse: so_messages.CMsgSOSingleObject,
    Language.SODestroy: so_messages.CMsgSOSingleObject,
    Language.CraftResponse: so_messages.CMsgSOMultipleObjects,
    Language.SOCacheSubscriptionRefresh: so_messages.CMsgSOCacheSubscriptionRefresh,
    Language.SOCacheSubscribed: so_messages.CMsgSOCacheSubscribed,
    Language.SOCacheSubscriptionCheck: so_messages.CMsgSOCacheSubscribed,
    # struct messages
    Language.Craft: struct_messages.CraftRequest,
    Language.SetItemStyle: struct_messages.SetItemStyleRequest,
    Language.Delete: struct_messages.DeleteItemRequest,
    Language.GiftWrapItem: struct_messages.WrapItemRequest,
    Language.UnwrapGiftRequest: struct_messages.UnwrapItemRequest,
    Language.DeliverGift: struct_messages.DeliverGiftRequest,
    Language.UnlockCrate: struct_messages.OpenCrateRequest,
}

GCMsgProtos = {
    Language.ClientWelcome: cso_messages.CMsgClientWelcome,
    Language.ServerWelcome: cso_messages.CMsgServerWelcome,
    Language.ClientHello: cso_messages.CMsgClientHello,
    Language.ClientGoodbye: cso_messages.CMsgClientGoodbye,
    Language.ServerGoodbye: cso_messages.CMsgServerGoodbye,
    Language.SystemMessage: cso_messages.CMsgSystemBroadcast,
    Language.UpdateItemSchema: cso_messages.CMsgUpdateItemSchema,
    Language.ClientDisplayNotification: cso_messages.CMsgGcClientDisplayNotification,
    Language.GameServerCreateIdentityResponse: cso_messages.CsoEconItem,
    Language.GameServerListResponse: cso_messages.CsoEconGameAccountClient,
    Language.WarGlobalStatsResponse: cso_messages.CsoEconItem,
    Language.SetItemPositions: cso_messages.CMsgSetItemPositions,
    Language.UseItemRequest: cso_messages.CMsgUseItem,
    Language.SortItems: cso_messages.CMsgSortItems,
    Language.AdjustItemEquippedState: cso_messages.CMsgAdjustItemEquippedState,
}

PROTOBUFS.update({**GCMsgs, **GCMsgProtos})
