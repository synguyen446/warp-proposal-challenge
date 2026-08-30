import json

from solution.data.data import *
from solution.data.utils import *



def compute_data(proposal_file: str):


    with open(
        proposal_file,
        "r",
    ) as file:
        proposal = json.load(file)
    lanes = proposal["lanes"]

    monthly_total_all_lanes = 0
    monthly_total_shipment = 0

    for lane in lanes:
        # STEP 0
        is_serviceable = check_and_get_servicability(
            lane, RATE_CARD_DF, PRICE_CONFIG_DICT
        )

        if not is_serviceable:  # skip lane data computation if cannot service without dropping the lane entirely
            continue

        # STEP 1
        pallets_per_shipment = lane["pallets_per_shipment"]
        weight_lb_per_pallet = lane["weight_lb_per_pallet"]
        lane["weight_lb_per_shipment"] = pallets_per_shipment * weight_lb_per_pallet

        # STEP 2,3,4,5,7
        get_mode_quoted(lane, PRICE_CONFIG_DICT)

        # STEP 3,
        get_pricing(
            lane,
            ACCESSORIALS_RATE_DF,
            RATE_CARD_DF,
            SERVICE_LEVELS_DF,
            VOLUME_TIERS_DF,
            PRICE_CONFIG_DICT,
        )

        # STEP 8
        get_transit_days(lane, RATE_CARD_DF, SERVICE_LEVELS_DF)

        monthly_total_all_lanes += lane["pricing"]["monthly_total"]
        monthly_total_shipment += lane["shipments_per_month"]


    # STEP 6
    get_volume_tier(proposal, VOLUME_TIERS_DF, monthly_total_shipment)
    proposal["monthly_total"] = monthly_total_all_lanes
    proposal["annual_total"] = monthly_total_all_lanes * 12

    output = f"{proposal_file}_computed.json"

    with open(output, "w") as f:
        json.dump(proposal, f, indent=2)

    return output
