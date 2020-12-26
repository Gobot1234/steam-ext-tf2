# -*- coding: utf-8 -*-

from ...enums import Enum, IntEnum

__all__ = (
    "GCGoodbyeReason",
    "TradeResponse",
    "Mercenary",
    "ItemSlot",
    "WearLevel",
    "BackpackSortType",
    "ItemFlags",
    "ItemQuality",
    "Language",
)


# fmt: off
class GCGoodbyeReason(IntEnum):
    GCGoingDown = 1
    NoSession   = 2


class TradeResponse(IntEnum):
    Accepted                        = 0
    Declined                        = 1
    TradeBannedInitiator            = 2
    TradeBannedTarget               = 3
    TargetAlreadyTrading            = 4
    Disabled                        = 5
    NotLoggedIn                     = 6
    Cancel                          = 7
    TooSoon                         = 8
    TooSoonPenalty                  = 9
    ConnectionFailed                = 10
    AlreadyTrading                  = 11
    AlreadyHasTradeRequest          = 12
    NoResponse                      = 13
    CyberCafeInitiator              = 14
    CyberCafeTarget                 = 15
    SchoolLabInitiator              = 16
    SchoolLabTarget                 = 16
    InitiatorBlockedTarget          = 18
    InitiatorNeedsVerifiedEmail     = 20
    InitiatorNeedsSteamGuard        = 21
    TargetAccountCannotTrade        = 22
    InitiatorSteamGuardDuration     = 23
    InitiatorPasswordResetProbation = 24
    InitiatorNewDeviceCooldown      = 25
    OKToDeliver                     = 50


class Mercenary(IntEnum):
    Scout    = 1
    Sniper   = 2
    Soldier  = 3
    Demoman  = 4
    Medic    = 5
    Heavy    = 6
    Pyro     = 7
    Spy      = 8
    Engineer = 9


class ItemSlot(IntEnum):
    Primary   = 0
    Secondary = 1
    Melee     = 2
    Sapper    = 4
    PDA       = 5
    PDA2      = 6
    Cosmetic1 = 7
    Cosmetic2 = 8
    Action    = 9
    Cosmetic3 = 10
    Taunt1    = 11
    Taunt2    = 12
    Taunt3    = 13
    Taunt4    = 14
    Taunt5    = 15
    Taunt6    = 16
    Taunt7    = 17
    Taunt8    = 18
    Misc      = 100  # not actually real but good for BackPackItem.slot
    Gift      = 101  # same as above


class WearLevel(Enum):
    FactoryNew    = "Factory New"
    MinimalWear   = "Minimal Wear"
    FieldTested   = "Field Tested"
    WellWorn      = "Well Worn"
    BattleScarred = "Battle Scarred"


class BackpackSortType(IntEnum):  # N.B only in game ones will actually work
    Name     = 1
    Defindex = 2
    Rarity   = 3
    Type     = 4
    Date     = 5
    Class    = 101
    Slot     = 102


class ItemFlags(IntEnum):
    CannotTrade = 1 << 0
    CannotCraft = 1 << 1
    NotEcon     = 1 << 3
    Preview     = 1 << 7


class ItemQuality(IntEnum):
    Normal          = 0
    Genuine         = 1
    Vintage         = 3
    Rarity3         = 4
    Unusual         = 5
    Unique          = 6
    Community       = 7
    Valve           = 8
    SelfMade        = 9
    Customized      = 10
    Strange         = 11
    Completed       = 12
    Haunted         = 13
    Collectors      = 14
    DecoratedWeapon = 15


class Language(IntEnum):
    SOCreate                                    = 21
    SOUpdate                                    = 22
    SODestroy                                   = 23
    SOCacheSubscribed                           = 24
    SOCacheUnsubscribed                         = 25
    SOUpdateMultiple                            = 26
    SOCacheSubscriptionCheck                    = 27
    SOCacheSubscriptionRefresh                  = 28
    SOCacheSubscribedUpToDate                   = 29

    Base                                        = 1000
    SetSingleItemPosition                       = 1001
    Craft                                       = 1002
    CraftResponse                               = 1003
    Delete                                      = 1004
    VerifyCacheSubscription                     = 1005
    NameItem                                    = 1006
    UnlockCrate                                 = 1007
    UnlockCrateResponse                         = 1008
    PaintItem                                   = 1009
    PaintItemResponse                           = 1010
    GoldenWrenchBroadcast                       = 1011
    MOTDRequest                                 = 1012
    MOTDRequestResponse                         = 1013
    NameBaseItem                                = 1019
    NameBaseItemResponse                        = 1020
    CustomizeItemTexture                        = 1023
    CustomizeItemTextureResponse                = 1024
    UseItemRequest                              = 1025
    UseItemResponse                             = 1026
    RespawnPostLoadoutChange                    = 1029
    RemoveItemName                              = 1030
    RemoveItemPaint                             = 1031
    GiftWrapItem                                = 1032
    GiftWrapItemResponse                        = 1033
    DeliverGift                                 = 1034
    DeliverGiftResponseReceiver                 = 1036
    UnwrapGiftRequest                           = 1037
    UnwrapGiftResponse                          = 1038
    SetItemStyle                                = 1039
    UsedClaimCodeItem                           = 1040
    SortItems                                   = 1041
    LookupAccount                               = 1043
    LookupAccountResponse                       = 1044
    LookupAccountName                           = 1045
    LookupAccountNameResponse                   = 1046
    UpdateItemSchema                            = 1049
    RequestInventoryRefresh                     = 1050
    RemoveCustomTexture                         = 1051
    RemoveCustomTextureResponse                 = 1052
    RemoveMakersMark                            = 1053
    RemoveMakersMarkResponse                    = 1054
    RemoveUniqueCraftIndex                      = 1055
    RemoveUniqueCraftIndexResponse              = 1056
    SaxxyBroadcast                              = 1057
    BackpackSortFinished                        = 1058
    AdjustItemEquippedState                     = 1059
    CollectItem                                 = 1061
    ItemAcknowledged                            = 1062
    PresetsSelectPresetForClass                 = 1063
    PresetsSetItemPosition                      = 1064
    ReportAbuse                                 = 1065
    ReportAbuseResponse                         = 1066
    PresetsSelectPresetForClassReply            = 1067
    NameItemNotification                        = 1068
    ClientDisplayNotification                   = 1069
    ApplyStrangePart                            = 1070
    IncrementKillCountAttribute                 = 1071
    IncrementKillCountResponse                  = 1072
    RemoveStrangePart                           = 1073
    ResetStrangeScores                          = 1074
    GiftedItems                                 = 1075
    ApplyUpgradeCard                            = 1077
    RemoveUpgradeCard                           = 1078
    ApplyStrangeRestriction                     = 1079
    ClientRequestMarketData                     = 1080
    ClientRequestMarketDataResponse             = 1081
    ApplyXifier                                 = 1082
    ApplyXifierResponse                         = 1083
    TrackUniquePlayerPairEvent                  = 1084
    FulfillDynamicRecipeComponent               = 1085
    FulfillDynamicRecipeComponentResponse       = 1086
    SetItemEffectVerticalOffset                 = 1087
    SetHatEffectUseHeadOrigin                   = 1088
    ItemEaterRecharger                          = 1089
    ItemEaterRechargerResponse                  = 1090
    ApplyBaseItemXifier                         = 1091
    ApplyClassTransmogrifier                    = 1092
    ApplyHalloweenSpellbookPage                 = 1093
    RemoveKillStreak                            = 1094
    RemoveKillStreakResponse                    = 1095
    TFSpecificItemBroadcast                     = 1096
    IncrementKillCountAttributeMultiple         = 1097
    DeliverGiftResponseGiver                    = 1098
    SetItemPositions                            = 1100
    LookupMultipleAccountNames                  = 1101
    LookupMultipleAccountNamesResponse          = 1102
    TradingBase                                 = 1500
    TradingInitiateTradeRequest                 = 1501
    TradingInitiateTradeResponse                = 1502
    TradingStartSession                         = 1503
    TradingSessionClosed                        = 1509
    TradingCancelSession                        = 1510
    TradingInitiateTradeRequestResponse         = 1514
    ServerBrowserFavoriteServer                 = 1601
    ServerBrowserBlacklistServer                = 1602
    ServerRentalsBase                           = 1700
    ItemPreviewCheckStatus                      = 1701
    ItemPreviewStatusResponse                   = 1702
    ItemPreviewRequest                          = 1703
    ItemPreviewRequestResponse                  = 1704
    ItemPreviewExpire                           = 1705
    ItemPreviewExpireNotification               = 1706
    ItemPreviewItemBoughtNotification           = 1708
    DevNewItemRequest                           = 2001
    DevNewItemRequestResponse                   = 2002
    DevDebugRollLootRequest                     = 2003
    StoreGetUserData                            = 2500
    StoreGetUserDataResponse                    = 2501
    StorePurchaseFinalize                       = 2512
    StorePurchaseFinalizeResponse               = 2513
    StorePurchaseCancel                         = 2514
    StorePurchaseCancelResponse                 = 2515
    StorePurchaseQueryTxn                       = 2508
    StorePurchaseQueryTxnResponse               = 2509
    StorePurchaseInit                           = 2510
    StorePurchaseInitResponse                   = 2511
    GCToGCDirtySDOCache                         = 2516
    GCToGCDirtyMultipleSDOCache                 = 2517
    GCToGCUpdateSQLKeyValue                     = 2518
    GCToGCBroadcastConsoleCommand               = 2521
    ServerVersionUpdated                        = 2522
    ApplyAutograph                              = 2523
    GCToGCWebAPIAccountChanged                  = 2524
    RequestAnnouncements                        = 2525
    RequestAnnouncementsResponse                = 2526
    RequestPassportItemGrant                    = 2527
    ClientVersionUpdated                        = 2528
    ItemPurgatoryFinalizePurchase               = 2531
    ItemPurgatoryFinalizePurchaseResponse       = 2532
    ItemPurgatoryRefundPurchase                 = 2533
    ItemPurgatoryRefundPurchaseResponse         = 2534
    GCToGCPlayerStrangeCountAdjustments         = 2535
    RequestStoreSalesData                       = 2536
    RequestStoreSalesDataResponse               = 2537
    RequestStoreSalesDataUpToDateResponse       = 2538
    GCToGCPingRequest                           = 2539
    GCToGCPingResponse                          = 2540
    GCToGCGetUserSessionServer                  = 2541
    GCToGCGetUserSessionServerResponse          = 2542
    GCToGCGetUserServerMembers                  = 2543
    GCToGCGetUserServerMembersResponse          = 2544
    GCToGCGrantSelfMadeItemToAccount            = 2555
    GCToGCThankedByNewUser                      = 2556
    ShuffleCrateContents                        = 2557

    PingRequest                                 = 3001
    PingResponse                                = 3002
    ClientWelcome                               = 4004
    ServerWelcome                               = 4005
    ClientHello                                 = 4006
    ServerHello                                 = 4007
    ClientGoodbye                               = 4008
    ServerGoodbye                               = 4009

    SystemMessage                               = 4001
    ReplicateConVars                            = 4002
    ConVarUpdated                               = 4003
    InviteToParty                               = 4501
    InvitationCreated                           = 4502
    PartyInviteResponse                         = 4503
    KickFromParty                               = 4504
    LeaveParty                                  = 4505
    ServerAvailable                             = 4506
    ClientConnectToServer                       = 4507
    GameServerInfo                              = 4508
    Error                                       = 4509
    ReplayUploadedToYouTube                     = 4510
    LANServerAvailable                          = 4511

    ReportWarKill                               = 5001
    VoteKickBanPlayer                           = 5018
    VoteKickBanPlayerResult                     = 5019
    FreeTrialChooseMostHelpfulFriend            = 5022
    RequestTF2Friends                           = 5023
    RequestTF2FriendsResponse                   = 5024
    ReplaySubmitContestEntry                    = 5026
    ReplaySubmitContestEntryResponse            = 5027
    SaxxyAwarded                                = 5029
    FreeTrialThankedBySomeone                   = 5028
    FreeTrialThankedSomeone                     = 5030
    FreeTrialConvertedToPremium                 = 5031
    CoachingAddToCoaches                        = 5200
    CoachingAddToCoachesResponse                = 5201
    CoachingRemoveFromCoaches                   = 5202
    CoachingRemoveFromCoachesResponse           = 5203
    CoachingFindCoach                           = 5204
    CoachingFindCoachResponse                   = 5205
    CoachingAskCoach                            = 5206
    CoachingAskCoachResponse                    = 5207
    CoachingCoachJoinGame                       = 5208
    CoachingCoachJoining                        = 5209
    CoachingCoachJoined                         = 5210
    CoachingLikeCurrentCoach                    = 5211
    CoachingRemoveCurrentCoach                  = 5212
    CoachingAlreadyRatedCoach                   = 5213
    DuelRequest                                 = 5500
    DuelResponse                                = 5501
    DuelResults                                 = 5502
    DuelStatus                                  = 5503
    HalloweenReservedItem                       = 5607
    HalloweenGrantItem                          = 5608
    HalloweenGrantItemResponse                  = 5609
    HalloweenServerBossEvent                    = 5612
    HalloweenMerasmus2012                       = 5613
    HalloweenUpdateMerasmusLootLevel            = 5614
    GameServerLevelInfo                         = 5700
    GameServerAuthChallenge                     = 5701
    GameServerAuthChallengeResponse             = 5702
    GameServerCreateIdentity                    = 5703
    GameServerCreateIdentityResponse            = 5704
    GameServerList                              = 5705
    GameServerListResponse                      = 5706
    GameServerAuthResult                        = 5707
    GameServerResetIdentity                     = 5708
    GameServerResetIdentityResponse             = 5709
    ClientUseServerModificationItem             = 5710
    ClientUseServerModificationItemResponse     = 5711
    GameServerUseServerModificationItem         = 5712
    GameServerUseServerModificationItemResponse = 5713
    GameServerServerModificationItemExpired     = 5714
    GameServerModificationItemState             = 5715
    GameServerAckPolicy                         = 5716
    GameServerAckPolicyResponse                 = 5717
    QPScoreServers                              = 5800
    QPScoreServersResponse                      = 5801
    QPPlayerJoining                             = 5802
    GameMatchSignOut                            = 6204
    CreateOrUpdateParty                         = 6233
    AbandonCurrentGame                          = 6235
    EMsgForceSOCacheResend                      = 6237
    RequestChatChannelList                      = 6260
    RequestChatChannelListResponse              = 6261
    ReadyUp                                     = 6270
    KickedFromMatchmakingQueue                  = 6271
    LeaverDetected                              = 6272
    LeaverDetectedResponse                      = 6287
    PlayerFailedToConnect                       = 6288
    ExitMatchmaking                             = 6289
    AcceptInvite                                = 6291
    AcceptInviteResponse                        = 6292
    MatchmakingProgress                         = 6293
    MvMVictoryInfo                              = 6294
    GameServerMatchmakingStatus                 = 6295
    CreateOrUpdatePartyReply                    = 6296
    MvMVictory                                  = 6297
    MvMVictoryReply                             = 6298
    GameServerKickingLobby                      = 6299
    LeaveGameAndPrepareToJoinParty              = 6300
    RemovePlayerFromLobby                       = 6301
    SetLobbySafeToLeave                         = 6302
    UpdatePeriodicEvent                         = 6400
    ClientVerificationChallenge                 = 6500
    ClientVerificationChallengeResponse         = 6501
    ClientVerificationVerboseResponse           = 6502
    ClientSetItemSlotAttribute                  = 6503
    PlayerSkillRatingAdjustment                 = 6504
    WarIndividualUpdate                         = 6505
    WarJoinWar                                  = 6506
    WarRequestGlobalStats                       = 6507
    WarGlobalStatsResponse                      = 6508
    WorldStatusBroadcast                        = 6518
    DevGrantWarKill                             = 10001
