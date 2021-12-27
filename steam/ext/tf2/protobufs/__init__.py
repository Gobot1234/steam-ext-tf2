from steam.protobufs import PROTOBUFS

from ..enums import Language
from . import base as base, sdk, struct_messages

PROTOBUFS.update(
    {
        Language.SOUpdate: sdk.SingleObject,
        Language.SOCreate: sdk.SingleObject,
        Language.SOUpdateMultiple: sdk.MultipleObjects,
        Language.GameServerResetIdentityResponse: sdk.SingleObject,
        Language.SODestroy: sdk.SingleObject,
        Language.SOCacheSubscriptionRefresh: sdk.CacheSubscriptionRefresh,
        Language.SOCacheSubscribed: sdk.CacheSubscribed,
        Language.SOCacheSubscriptionCheck: sdk.CacheSubscribed,
        Language.ClientWelcome: base.ClientWelcome,
        Language.ServerWelcome: base.ServerWelcome,
        Language.ClientHello: base.ClientHello,
        Language.ClientGoodbye: base.ClientGoodbye,
        Language.ServerGoodbye: base.ServerGoodbye,
        Language.SystemMessage: base.SystemBroadcast,
        Language.UpdateItemSchema: base.UpdateItemSchema,
        Language.ClientDisplayNotification: base.ClientDisplayNotification,
        Language.GameServerCreateIdentityResponse: base.Item,
        Language.GameServerListResponse: base.GameAccountClient,
        Language.WarGlobalStatsResponse: base.Item,
        Language.SetItemPositions: base.SetItemPositions,
        Language.UseItemRequest: base.UseItem,
        Language.SortItems: base.SortItems,
        Language.AdjustItemEquippedState: base.AdjustItemEquippedState,
        Language.RequestInventoryRefresh: base.RequestInventoryRefresh,
        # struct messages
        Language.Craft: struct_messages.CraftRequest,
        Language.CraftResponse: struct_messages.CraftResponse,
        Language.SetItemStyle: struct_messages.SetItemStyleRequest,
        Language.Delete: struct_messages.DeleteItemRequest,
        Language.GiftWrapItem: struct_messages.WrapItemRequest,
        Language.UnwrapGiftRequest: struct_messages.UnwrapItemRequest,
        Language.DeliverGift: struct_messages.DeliverGiftRequest,
        Language.UnlockCrate: struct_messages.OpenCrateRequest,
    }
)
