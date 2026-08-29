from validate import round2
import pandas as pd
from solution.model_schema import Lane, Proposal


def check_and_get_servicability(
    lane: Lane, df: pd.DataFrame, price_config: dict
) -> bool:
    match = df.loc[
        (df["origin_metro"] == lane["origin_metro"])
        & (df["dest_metro"] == lane["dest_metro"])
    ]

    if lane["serviceable"] == True:
        if match.empty:
            lane["serviceable"] = False
            lane["unserviceable_reason"] = "lane_not_in_rate_card"
            return False
        else:
            lane["lane_id"] = match["lane_id"].item()

        if lane["pallets_per_shipment"] > price_config["ltl_max_pallets"]:
            lane["serviceable"] = False
            lane["unserviceable_reason"] = "exceeds_capacity"
            return False
        return True
    else:
        return False


def get_mode_quoted(lane: Lane, price_config: dict):
    if (
        lane["pallets_per_shipment"] >= price_config["ftl_pallet_threshold"]
        or lane["weight_lb_per_shipment"] >= price_config["ftl_weight_threshold_lb"]
    ):
        lane["mode_quoted"] = "LTL and FTL"
    elif lane["pallets_per_shipment"] > price_config["ltl_max_pallets"]:
        lane["mode_quoted"] = "FTL"

    else:
        lane["mode_quoted"] = "LTL"


def get_pricing(
    lane: Lane,
    accessorials_rate: pd.DataFrame,
    rate_card: pd.DataFrame,
    service_levels: pd.DataFrame,
    volume_tiers: pd.DataFrame,
    price_config: pd.DataFrame,
):

    def get_linehaul(lane: Lane, service_levels: pd.DataFrame) -> float:
        lane_id = lane["lane_id"]
        df_rate_card = rate_card.loc[rate_card["lane_id"] == lane_id]
        if lane["mode_quoted"] == "LTL":

            ltl_min_charge = df_rate_card["ltl_min_charge"].item()
            ltl_base = df_rate_card["ltl_base"].item()
            ltl_per_pallet = df_rate_card["ltl_per_pallet"].item()

            linehaul_base = max(
                ltl_min_charge, ltl_base + ltl_per_pallet * lane["pallets_per_shipment"]
            )

        else:
            linehaul_base = df_rate_card["ftl_flat_rate"].item()

        df = service_levels.loc[service_levels["code"] == lane["service_level"]]
        linehaul_multiplier = df["linehaul_multiplier"].item()
        linehaul = round2(linehaul_base * linehaul_multiplier)
        return linehaul

    def get_accessorials(lane: Lane, accessorials_rate: pd.DataFrame) -> float:
        accessorials_total = 0
        accessorials = []
        for a in lane["accessorials"]:
            df = accessorials_rate.loc[accessorials_rate["code"] == a]
            rate = df["rate"].item()
            code = df["code"].item()
            accessorials.append({"code": code, "amount": rate})
            accessorials_total += rate
        return accessorials, round2(accessorials_total)

    def get_discount(lane: Lane, volume_tiers: pd.DataFrame) -> float:
        shipments_per_month = lane["shipments_per_month"]
        tier = volume_tiers.loc[
            (volume_tiers["min_monthly_shipments"] < shipments_per_month)
            & (volume_tiers["max_monthly_shipments"] > shipments_per_month)
        ]

        return tier["discount_pct"].item()

    def get_total_amount(pricing: dict, lane: Lane) -> float:
        shipment_subtotal = round2(
            pricing["linehaul"]
            + pricing["fuel_surcharge"]
            + pricing["accessorials_total"]
        )
        discount = round2(shipment_subtotal * pricing["discount_pct"] / 100)
        shipment_total = round2(shipment_subtotal - discount)
        lane_monthly_total = round2(shipment_total * lane["shipments_per_month"])

        return shipment_subtotal, discount, shipment_total, lane_monthly_total

    pricing = {}
    pricing["linehaul"] = get_linehaul(lane, service_levels)
    pricing["fuel_surcharge"] = round2(
        pricing["linehaul"] * price_config["fuel_surcharge_pct"] / 100
    )
    pricing["accessorials"], pricing["accessorials_total"] = get_accessorials(
        lane, accessorials_rate
    )
    pricing["discount_pct"] = get_discount(lane, volume_tiers)
    (
        pricing["shipment_subtotal"],
        pricing["discount"],
        pricing["shipment_total"],
        pricing["monthly_total"],
    ) = get_total_amount(pricing, lane)

    lane["pricing"] = pricing


def get_transit_days(lane: Lane, rate_card: pd.DataFrame, service_levels: pd.DataFrame):
    lane_id = lane["lane_id"]
    df_rate_card = rate_card.loc[rate_card["lane_id"] == lane_id]
    df_sl = service_levels.loc[service_levels["code"] == lane["service_level"]]

    transit_days_delta = df_sl["transit_days_delta"].item()
    transit_days_standard = df_rate_card["transit_days_standard"].item()

    lane["transit_days"] = max(1, transit_days_delta + transit_days_standard)


def get_volume_tier(
    proposal: Proposal, volume_tiers: pd.DataFrame, monthly_total_shipment: float
):
    tier = volume_tiers.loc[
        (volume_tiers["min_monthly_shipments"] <= monthly_total_shipment)
        & (volume_tiers["max_monthly_shipments"] >= monthly_total_shipment)
    ]

    if tier.empty:  # Proposal exceed 250 shipments
        tier = volume_tiers.loc[volume_tiers["tier_name"] == "Enterprise"]

    proposal["volume_tier"] = {
        "tier_name": tier["tier_name"].item(),
        "total_monthly_shipments": monthly_total_shipment,
        "discount_pct": tier["discount_pct"].item(),
    }
