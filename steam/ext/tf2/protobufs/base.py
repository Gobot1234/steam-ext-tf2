# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: base_gcmessages.proto
# plugin: python-betterproto

from dataclasses import dataclass
from typing import List

import betterproto


@dataclass(eq=False, repr=False)
class StorePurchaseInitLineItem(betterproto.Message):
    item_def_id: int = betterproto.uint32_field(1)
    quantity: int = betterproto.uint32_field(2)
    cost_in_local_currency: int = betterproto.uint32_field(3)
    purchase_type: int = betterproto.uint32_field(4)


@dataclass(eq=False, repr=False)
class StorePurchaseInit(betterproto.Message):
    country: str = betterproto.string_field(1)
    language: int = betterproto.int32_field(2)
    currency: int = betterproto.int32_field(3)
    line_items: List["StorePurchaseInitLineItem"] = betterproto.message_field(4)


@dataclass(eq=False, repr=False)
class StorePurchaseInitResponse(betterproto.Message):
    result: int = betterproto.int32_field(1)
    txn_id: int = betterproto.uint64_field(2)


@dataclass(eq=False, repr=False)
class SystemBroadcast(betterproto.Message):
    message: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class ClientHello(betterproto.Message):
    version: int = betterproto.uint32_field(1)


@dataclass(eq=False, repr=False)
class ServerHello(betterproto.Message):
    version: int = betterproto.uint32_field(1)


@dataclass(eq=False, repr=False)
class ClientWelcome(betterproto.Message):
    version: int = betterproto.uint32_field(1)
    game_data: bytes = betterproto.bytes_field(2)
    txn_country_code: str = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class ServerWelcome(betterproto.Message):
    min_allowed_version: int = betterproto.uint32_field(1)
    active_version: int = betterproto.uint32_field(2)


@dataclass(eq=False, repr=False)
class ClientGoodbye(betterproto.Message):
    reason: int = betterproto.int64_field(1)


@dataclass(eq=False, repr=False)
class ServerGoodbye(betterproto.Message):
    reason: int = betterproto.int64_field(1)


@dataclass(eq=False, repr=False)
class ServerAvailable(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class LanServerAvailable(betterproto.Message):
    lobby_id: int = betterproto.fixed64_field(1)


@dataclass(eq=False, repr=False)
class GameAccountClient(betterproto.Message):
    additional_backpack_slots: int = betterproto.uint32_field(1)
    trial_account: bool = betterproto.bool_field(2)
    need_to_choose_most_helpful_friend: bool = betterproto.bool_field(4)
    in_coaches_list: bool = betterproto.bool_field(5)
    trade_ban_expiration: int = betterproto.fixed32_field(6)
    duel_ban_expiration: int = betterproto.fixed32_field(7)
    preview_item_def: int = betterproto.uint32_field(8)
    phone_verified: bool = betterproto.bool_field(19)
    skill_rating_6_v6: int = betterproto.uint32_field(20)
    skill_rating_9_v9: int = betterproto.uint32_field(21)
    competitive_access: bool = betterproto.bool_field(23)
    matchmaking_ranked_ban_expiration: int = betterproto.uint32_field(18)
    matchmaking_ranked_low_priority_expiration: int = betterproto.uint32_field(24)
    matchmaking_ranked_ban_last_duration: int = betterproto.uint32_field(25)
    matchmaking_ranked_low_priority_last_duration: int = betterproto.uint32_field(26)
    matchmaking_casual_ban_expiration: int = betterproto.uint32_field(27)
    matchmaking_casual_low_priority_expiration: int = betterproto.uint32_field(28)
    matchmaking_casual_ban_last_duration: int = betterproto.uint32_field(29)
    matchmaking_casual_low_priority_last_duration: int = betterproto.uint32_field(30)
    phone_identifying: bool = betterproto.bool_field(31)
    disable_party_quest_progress: bool = betterproto.bool_field(32)
    quest_reward_credits: int = betterproto.uint32_field(33)
    matchmaking_last_casual_excessive_reports_auto_ban_time: int = betterproto.uint32_field(34)
    matchmaking_last_comp_excessive_reports_auto_ban_time: int = betterproto.uint32_field(35)


@dataclass(eq=False, repr=False)
class CriteriaCondition(betterproto.Message):
    op: int = betterproto.int32_field(1)
    field: str = betterproto.string_field(2)
    required: bool = betterproto.bool_field(3)
    float_value: float = betterproto.float_field(4)
    string_value: str = betterproto.string_field(5)


@dataclass(eq=False, repr=False)
class Criteria(betterproto.Message):
    item_level: int = betterproto.uint32_field(1)
    item_quality: int = betterproto.int32_field(2)
    item_level_set: bool = betterproto.bool_field(3)
    item_quality_set: bool = betterproto.bool_field(4)
    initial_inventory: int = betterproto.uint32_field(5)
    initial_quantity: int = betterproto.uint32_field(6)
    ignore_enabled_flag: bool = betterproto.bool_field(8)
    conditions: List["CriteriaCondition"] = betterproto.message_field(9)
    recent_only: bool = betterproto.bool_field(10)
    tags: str = betterproto.string_field(11)
    equip_regions: str = betterproto.string_field(12)


@dataclass(eq=False, repr=False)
class Recipe(betterproto.Message):
    def_index: int = betterproto.uint32_field(1)
    name: str = betterproto.string_field(2)
    n_a: str = betterproto.string_field(3)
    desc_inputs: str = betterproto.string_field(4)
    desc_outputs: str = betterproto.string_field(5)
    di_a: str = betterproto.string_field(6)
    di_b: str = betterproto.string_field(7)
    di_c: str = betterproto.string_field(8)
    do_a: str = betterproto.string_field(9)
    do_b: str = betterproto.string_field(10)
    do_c: str = betterproto.string_field(11)
    requires_all_same_class: bool = betterproto.bool_field(12)
    requires_all_same_slot: bool = betterproto.bool_field(13)
    class_usage_for_output: int = betterproto.int32_field(14)
    slot_usage_for_output: int = betterproto.int32_field(15)
    set_for_output: int = betterproto.int32_field(16)
    input_items_criteria: List["Criteria"] = betterproto.message_field(20)
    output_items_criteria: List["Criteria"] = betterproto.message_field(21)
    input_item_dupe_counts: List[int] = betterproto.uint32_field(22)


@dataclass(eq=False, repr=False)
class DevNewItemRequest(betterproto.Message):
    receiver: int = betterproto.fixed64_field(1)
    criteria: "Criteria" = betterproto.message_field(2)


@dataclass(eq=False, repr=False)
class DevDebugRollLootRequest(betterproto.Message):
    receiver: int = betterproto.fixed64_field(1)
    loot_list_name: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class IncrementKillCountAttribute(betterproto.Message):
    killer_steam_id: int = betterproto.uint64_field(1)
    victim_steam_id: int = betterproto.uint64_field(2)
    item_id: int = betterproto.uint64_field(3)
    event_type: int = betterproto.uint32_field(4)
    increment_value: int = betterproto.uint32_field(5)


@dataclass(eq=False, repr=False)
class IncrementKillCountAttributeMultiple(betterproto.Message):
    msgs: List["IncrementKillCountAttribute"] = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class TrackUniquePlayerPairEvent(betterproto.Message):
    killer_steam_id: int = betterproto.uint64_field(1)
    victim_steam_id: int = betterproto.uint64_field(2)
    item_id: int = betterproto.uint64_field(3)
    event_type: int = betterproto.uint32_field(4)


@dataclass(eq=False, repr=False)
class ApplyStrangeCountTransfer(betterproto.Message):
    tool_item_id: int = betterproto.uint64_field(1)
    item_src_item_id: int = betterproto.uint64_field(2)
    item_dest_item_id: int = betterproto.uint64_field(3)


@dataclass(eq=False, repr=False)
class ApplyStrangePart(betterproto.Message):
    strange_part_item_id: int = betterproto.uint64_field(1)
    item_item_id: int = betterproto.uint64_field(2)


@dataclass(eq=False, repr=False)
class ApplyStrangeRestriction(betterproto.Message):
    strange_part_item_id: int = betterproto.uint64_field(1)
    item_item_id: int = betterproto.uint64_field(2)
    strange_attr_index: int = betterproto.uint32_field(3)


@dataclass(eq=False, repr=False)
class ApplyUpgradeCard(betterproto.Message):
    upgrade_card_item_id: int = betterproto.uint64_field(1)
    subject_item_id: int = betterproto.uint64_field(2)


@dataclass(eq=False, repr=False)
class ItemAttribute(betterproto.Message):
    def_index: int = betterproto.uint32_field(1)
    value: int = betterproto.uint32_field(2)
    value_bytes: bytes = betterproto.bytes_field(3)


@dataclass(eq=False, repr=False)
class ItemEquipped(betterproto.Message):
    new_class: int = betterproto.uint32_field(1)
    new_slot: int = betterproto.uint32_field(2)


@dataclass(eq=False, repr=False)
class Item(betterproto.Message):
    id: int = betterproto.uint64_field(1)
    account_id: int = betterproto.uint32_field(2)
    inventory: int = betterproto.uint32_field(3)
    def_index: int = betterproto.uint32_field(4)
    quantity: int = betterproto.uint32_field(5)
    level: int = betterproto.uint32_field(6)
    quality: int = betterproto.uint32_field(7)
    flags: int = betterproto.uint32_field(8)
    origin: int = betterproto.uint32_field(9)
    custom_name: str = betterproto.string_field(10)
    custom_desc: str = betterproto.string_field(11)
    attribute: List["ItemAttribute"] = betterproto.message_field(12)
    interior_item: "Item" = betterproto.message_field(13)
    in_use: bool = betterproto.bool_field(14)
    style: int = betterproto.uint32_field(15)
    original_id: int = betterproto.uint64_field(16)
    contains_equipped_state: bool = betterproto.bool_field(17)
    equipped_state: List["ItemEquipped"] = betterproto.message_field(18)
    contains_equipped_state_v2: bool = betterproto.bool_field(19)


@dataclass(eq=False, repr=False)
class AdjustItemEquippedState(betterproto.Message):
    item_id: int = betterproto.uint64_field(1)
    new_class: int = betterproto.uint32_field(2)
    new_slot: int = betterproto.uint32_field(3)


@dataclass(eq=False, repr=False)
class SortItems(betterproto.Message):
    sort_type: int = betterproto.uint32_field(1)


@dataclass(eq=False, repr=False)
class ClaimCode(betterproto.Message):
    account_id: int = betterproto.uint32_field(1)
    code_type: int = betterproto.uint32_field(2)
    time_acquired: int = betterproto.uint32_field(3)
    code: str = betterproto.string_field(4)


@dataclass(eq=False, repr=False)
class StoreGetUserData(betterproto.Message):
    price_sheet_version: int = betterproto.fixed32_field(1)


@dataclass(eq=False, repr=False)
class StoreGetUserDataResponse(betterproto.Message):
    result: int = betterproto.int32_field(1)
    currency: int = betterproto.int32_field(2)
    country: str = betterproto.string_field(3)
    price_sheet_version: int = betterproto.fixed32_field(4)
    experiment_data: int = betterproto.uint64_field(5)
    featured_item_idx: int = betterproto.int32_field(6)
    show_hat_descriptions: bool = betterproto.bool_field(7)
    price_sheet: bytes = betterproto.bytes_field(8)
    default_item_sort: int = betterproto.int32_field(9)
    popular_items: List[int] = betterproto.uint32_field(10)


@dataclass(eq=False, repr=False)
class UpdateItemSchema(betterproto.Message):
    items_game: bytes = betterproto.bytes_field(1)
    item_schema_version: int = betterproto.fixed32_field(2)
    items_game_url: str = betterproto.string_field(3)
    signature: bytes = betterproto.bytes_field(4)


@dataclass(eq=False, repr=False)
class Error(betterproto.Message):
    error_text: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class RequestInventoryRefresh(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class ConVarValue(betterproto.Message):
    name: str = betterproto.string_field(1)
    value: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class ReplicateConVars(betterproto.Message):
    convars: List["ConVarValue"] = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class UseItem(betterproto.Message):
    item_id: int = betterproto.uint64_field(1)
    target_steam_id: int = betterproto.fixed64_field(2)
    gift_potential_targets: List[int] = betterproto.uint32_field(3)
    duel_class_lock: int = betterproto.uint32_field(4)
    initiator_steam_id: int = betterproto.fixed64_field(5)
    itempack_ack_immediately: bool = betterproto.bool_field(6)


@dataclass(eq=False, repr=False)
class ReplayUploadedToYouTube(betterproto.Message):
    youtube_url: str = betterproto.string_field(1)
    youtube_account_name: str = betterproto.string_field(2)
    session_id: int = betterproto.uint64_field(3)


@dataclass(eq=False, repr=False)
class ConsumableExhausted(betterproto.Message):
    item_def_id: int = betterproto.int32_field(1)


@dataclass(eq=False, repr=False)
class ItemAcknowledged(betterproto.Message):
    account_id: int = betterproto.uint32_field(1)
    inventory: int = betterproto.uint32_field(2)
    def_index: int = betterproto.uint32_field(3)
    quality: int = betterproto.uint32_field(4)
    rarity: int = betterproto.uint32_field(5)
    origin: int = betterproto.uint32_field(6)
    is_strange: int = betterproto.uint32_field(7)
    is_unusual: int = betterproto.uint32_field(8)
    wear: float = betterproto.float_field(9)


@dataclass(eq=False, repr=False)
class SetPresetItemPosition(betterproto.Message):
    class_id: int = betterproto.uint32_field(1)
    preset_id: int = betterproto.uint32_field(2)
    slot_id: int = betterproto.uint32_field(3)
    item_id: int = betterproto.uint64_field(4)


@dataclass(eq=False, repr=False)
class SetItemPositions(betterproto.Message):
    item_positions: List["SetItemPositionsItemPosition"] = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class SetItemPositionsItemPosition(betterproto.Message):
    item_id: int = betterproto.uint64_field(1)
    position: int = betterproto.uint32_field(2)


@dataclass(eq=False, repr=False)
class ItemPresetInstance(betterproto.Message):
    class_id: int = betterproto.uint32_field(2)
    preset_id: int = betterproto.uint32_field(3)
    slot_id: int = betterproto.uint32_field(4)
    item_id: int = betterproto.uint64_field(5)


@dataclass(eq=False, repr=False)
class SelectPresetForClass(betterproto.Message):
    class_id: int = betterproto.uint32_field(1)
    preset_id: int = betterproto.uint32_field(2)


@dataclass(eq=False, repr=False)
class CsoClassPresetClientData(betterproto.Message):
    account_id: int = betterproto.uint32_field(1)
    class_id: int = betterproto.uint32_field(2)
    active_preset_id: int = betterproto.uint32_field(3)


@dataclass(eq=False, repr=False)
class ReportAbuse(betterproto.Message):
    target_steam_id: int = betterproto.fixed64_field(1)
    description: str = betterproto.string_field(4)
    gid: int = betterproto.uint64_field(5)
    abuse_type: int = betterproto.uint32_field(2)
    content_type: int = betterproto.uint32_field(3)
    target_game_server_ip: int = betterproto.fixed32_field(6)
    target_game_server_port: int = betterproto.uint32_field(7)


@dataclass(eq=False, repr=False)
class ReportAbuseResponse(betterproto.Message):
    target_steam_id: int = betterproto.fixed64_field(1)
    result: int = betterproto.uint32_field(2)
    error_message: str = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class NameItemNotification(betterproto.Message):
    player_steamid: int = betterproto.fixed64_field(1)
    item_def_index: int = betterproto.uint32_field(2)
    item_name_custom: str = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class ClientDisplayNotification(betterproto.Message):
    notification_title_localization_key: str = betterproto.string_field(1)
    notification_body_localization_key: str = betterproto.string_field(2)
    body_substring_keys: List[str] = betterproto.string_field(3)
    body_substring_values: List[str] = betterproto.string_field(4)


@dataclass(eq=False, repr=False)
class ShowItemsPickedUp(betterproto.Message):
    player_steamid: int = betterproto.fixed64_field(1)


@dataclass(eq=False, repr=False)
class UpdatePeriodicEvent(betterproto.Message):
    account_id: int = betterproto.uint32_field(1)
    event_type: int = betterproto.uint32_field(2)
    amount: int = betterproto.uint32_field(3)


@dataclass(eq=False, repr=False)
class IncrementKillCountResponse(betterproto.Message):
    killer_account_id: int = betterproto.uint32_field(1)
    num_kills: int = betterproto.uint32_field(2)
    item_def: int = betterproto.uint32_field(3)
    level_type: int = betterproto.uint32_field(4)


@dataclass(eq=False, repr=False)
class RemoveStrangePart(betterproto.Message):
    item_id: int = betterproto.uint64_field(1)
    strange_part_score_type: int = betterproto.uint32_field(2)


@dataclass(eq=False, repr=False)
class RemoveUpgradeCard(betterproto.Message):
    item_id: int = betterproto.uint64_field(1)
    attribute_index: int = betterproto.uint32_field(2)


@dataclass(eq=False, repr=False)
class RemoveCustomizationAttributeSimple(betterproto.Message):
    item_id: int = betterproto.uint64_field(1)


@dataclass(eq=False, repr=False)
class ResetStrangeScores(betterproto.Message):
    item_id: int = betterproto.uint64_field(1)


@dataclass(eq=False, repr=False)
class ItemPreviewItemBoughtNotification(betterproto.Message):
    item_def_index: int = betterproto.uint32_field(1)


@dataclass(eq=False, repr=False)
class StorePurchaseCancel(betterproto.Message):
    txn_id: int = betterproto.uint64_field(1)


@dataclass(eq=False, repr=False)
class StorePurchaseCancelResponse(betterproto.Message):
    result: int = betterproto.uint32_field(1)


@dataclass(eq=False, repr=False)
class StorePurchaseFinalize(betterproto.Message):
    txn_id: int = betterproto.uint64_field(1)


@dataclass(eq=False, repr=False)
class StorePurchaseFinalizeResponse(betterproto.Message):
    result: int = betterproto.uint32_field(1)
    item_ids: List[int] = betterproto.uint64_field(2)


@dataclass(eq=False, repr=False)
class BannedWordListRequest(betterproto.Message):
    ban_list_group_id: int = betterproto.uint32_field(1)
    word_id: int = betterproto.uint32_field(2)


@dataclass(eq=False, repr=False)
class GiftedItems(betterproto.Message):
    gifter_steam_id: int = betterproto.uint64_field(1)
    was_random_person: bool = betterproto.bool_field(2)
    recipient_account_ids: List[int] = betterproto.uint32_field(3)


@dataclass(eq=False, repr=False)
class CollectItem(betterproto.Message):
    collection_item_id: int = betterproto.uint64_field(1)
    subject_item_id: int = betterproto.uint64_field(2)


@dataclass(eq=False, repr=False)
class ClientMarketDataRequest(betterproto.Message):
    user_currency: int = betterproto.uint32_field(1)


@dataclass(eq=False, repr=False)
class ClientMarketDataEntry(betterproto.Message):
    item_def_index: int = betterproto.uint32_field(1)
    item_quality: int = betterproto.uint32_field(2)
    item_sell_listings: int = betterproto.uint32_field(3)
    price_in_local_currency: int = betterproto.uint32_field(4)


@dataclass(eq=False, repr=False)
class ClientMarketData(betterproto.Message):
    entries: List["ClientMarketDataEntry"] = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class ApplyToolToItem(betterproto.Message):
    tool_item_id: int = betterproto.uint64_field(1)
    subject_item_id: int = betterproto.uint64_field(2)


@dataclass(eq=False, repr=False)
class ApplyToolToBaseItem(betterproto.Message):
    tool_item_id: int = betterproto.uint64_field(1)
    baseitem_def_index: int = betterproto.uint32_field(2)


@dataclass(eq=False, repr=False)
class RecipeComponent(betterproto.Message):
    subject_item_id: int = betterproto.uint64_field(1)
    attribute_index: int = betterproto.uint64_field(2)


@dataclass(eq=False, repr=False)
class FulfillDynamicRecipeComponent(betterproto.Message):
    tool_item_id: int = betterproto.uint64_field(1)
    consumption_components: List["RecipeComponent"] = betterproto.message_field(2)


@dataclass(eq=False, repr=False)
class SetItemEffectVerticalOffset(betterproto.Message):
    item_id: int = betterproto.uint64_field(1)
    offset: float = betterproto.float_field(2)


@dataclass(eq=False, repr=False)
class SetHatEffectUseHeadOrigin(betterproto.Message):
    item_id: int = betterproto.uint64_field(1)
    use_head: bool = betterproto.bool_field(2)


@dataclass(eq=False, repr=False)
class DeliverGiftResponseGiver(betterproto.Message):
    response_code: int = betterproto.uint32_field(1)
    receiver_account_name: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class GameAccountForGameServers(betterproto.Message):
    disable_party_quest_progress: bool = betterproto.bool_field(6)


@dataclass(eq=False, repr=False)
class CWorkshopPopulateItemDescriptionsRequest(betterproto.Message):
    appid: int = betterproto.uint32_field(1)
    languages: List[
        "CWorkshopPopulateItemDescriptionsRequestItemDescriptionsLanguageBlock"
    ] = betterproto.message_field(2)


@dataclass(eq=False, repr=False)
class CWorkshopPopulateItemDescriptionsRequestSingleItemDescription(betterproto.Message):
    gameitemid: int = betterproto.uint32_field(1)
    item_description: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class CWorkshopPopulateItemDescriptionsRequestItemDescriptionsLanguageBlock(betterproto.Message):
    language: str = betterproto.string_field(1)
    descriptions: List["CWorkshopPopulateItemDescriptionsRequestSingleItemDescription"] = betterproto.message_field(2)


@dataclass(eq=False, repr=False)
class CWorkshopGetContributorsRequest(betterproto.Message):
    appid: int = betterproto.uint32_field(1)
    gameitemid: int = betterproto.uint32_field(2)


@dataclass(eq=False, repr=False)
class CWorkshopGetContributorsResponse(betterproto.Message):
    contributors: List[int] = betterproto.fixed64_field(1)


@dataclass(eq=False, repr=False)
class CWorkshopSetItemPaymentRulesRequest(betterproto.Message):
    appid: int = betterproto.uint32_field(1)
    gameitemid: int = betterproto.uint32_field(2)
    associated_workshop_files: List[
        "CWorkshopSetItemPaymentRulesRequestWorkshopItemPaymentRule"
    ] = betterproto.message_field(3)
    partner_accounts: List["CWorkshopSetItemPaymentRulesRequestPartnerItemPaymentRule"] = betterproto.message_field(4)


@dataclass(eq=False, repr=False)
class CWorkshopSetItemPaymentRulesRequestWorkshopItemPaymentRule(betterproto.Message):
    workshop_file_id: int = betterproto.uint64_field(1)
    revenue_percentage: float = betterproto.float_field(2)
    rule_description: str = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class CWorkshopSetItemPaymentRulesRequestPartnerItemPaymentRule(betterproto.Message):
    account_id: int = betterproto.uint32_field(1)
    revenue_percentage: float = betterproto.float_field(2)
    rule_description: str = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class CWorkshopSetItemPaymentRulesResponse(betterproto.Message):
    pass