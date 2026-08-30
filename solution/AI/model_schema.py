from pydantic import BaseModel, Field
from typing import List, Literal


class Customer(BaseModel):
    company: str
    contact: str | None
    industry: str | None


class Lane(BaseModel):
    origin_metro: str = Field(description="Origin City")
    origin_state: str = Field(description="Two-letter state code")
    dest_metro: str = Field(description="Destination City")
    dest_state: str = Field(description="Two-letter state code")
    pallets_per_shipment: int | None
    weight_lb_per_pallet: int | None
    shipments_per_month: int | None
    service_level: Literal["STANDARD", "EXPEDITED", "GUARANTEED"] = Field(
        default="STANDARD",
        description="Only use EXPEDITED or GUARANTEED when the customer asks for speed or a date guarantee.",
    )
    mode_quoted: str | None
    accessorials: List[str] | None = Field(
        description="""None. Add one only when the call gives you a reason, such as "there's no dock" implying a liftgate."""
    )
    serviceable: bool
    unserviceable_reason: Literal[
        "lane_not_in_rate_card",
        "equipment_not_offered",
        "commodity_not_accepted",
        "exceeds_capacity",
    ]|None = Field(description="if is serviceble, set the value to null")
    notes: str = Field(
        description="Record special requests, operational circumstances, corrections, requested alternatives, and important delivery details in notes."
    )


class Proposal(BaseModel):
    call_id: str | None
    customer: Customer
    lanes: List[Lane]
    total_monthly_shipments: int | None = Field(
        description="The sum of all lanes monthly shipment"
    )


class Rationale(BaseModel):
    rationale: str = Field(
        description="one sentence on why this mode and service level."
    )


class Proposal_addon(BaseModel):
    deal_summary: str = Field(
        description="""two or three sentences a rep can say out loud describing the customer's freight in the customer's own terms."""
    )
    assumptions: List[str] = Field(
        description="anything you inferred rather than heard. If the customer never said whether the origin had a dock and you assumed one, say so."
    )
    open_questions: List[str] = Field(
        description="what the rep should ask before this becomes a contract."
    )
    excluded: str | None = Field(
        description="Leave null if all lanes are serviceable. Otherwise, every lane or requirement you could not price, with the reason in plain language the customer would accept."
    )
