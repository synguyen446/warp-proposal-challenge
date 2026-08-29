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
        None,
    ] = Field(description="if is serviceble, set the value to null")
    notes: str = Field(
        description="Record special requests, operational circumstances, corrections, requested alternatives, and important delivery details in notes."
    )


class Proposal(BaseModel):
    call_id: str | None
    customer: Customer
    lanes: List[Lane]
    total_monthly_shipments: int
    blockers: List[str]


