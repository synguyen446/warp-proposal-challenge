
from __future__ import annotations
import argparse
import re
from pathlib import Path
from solution.AI.model_schema import Proposal, Lane, Customer

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}
NUMBER = (
    r"(?:one|two|three|four|five|six|seven|eight|nine)\s+hundred|"
    r"\d+(?:\.\d+)?|one|two|three|four|five|six|seven|eight|nine|ten|"
    r"twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety"
)
CITY_STATES = {
    "atlanta": ("Atlanta", "GA"),
    "boston": ("Boston", "MA"),
    "charlotte": ("Charlotte", "NC"),
    "chicago": ("Chicago", "IL"),
    "dallas": ("Dallas", "TX"),
    "newark": ("Newark", "NJ"),
    "phoenix": ("Phoenix", "AZ"),
}


def number(value: str) -> int | None:
    value = value.lower().strip()
    if value.replace(".", "", 1).isdigit():
        return round(float(value))
    if value.endswith(" hundred"):
        first = value.removesuffix(" hundred")
        return NUMBER_WORDS.get(first, 0) * 100 or None
    return NUMBER_WORDS.get(value)


def metadata_value(text: str, key: str) -> str | None:
    match = re.search(rf"^{key}:\s*(.+)$", text, re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else None


def customer_dialogue(text: str) -> str:
    return " ".join(
        match.group(1).strip()
        for match in re.finditer(
            r"^\[\d{1,2}:\d{2}\]\s*CUSTOMER:\s*(.*)$",
            text,
            re.MULTILINE | re.IGNORECASE,
        )
    )


def extract(transcript_path: Path) -> Proposal:
    text = transcript_path.read_text(encoding="utf-8")
    customer_text = customer_dialogue(text)
    lower = customer_text.lower()

    contact_match = re.search(
        r"thanks for making time,?\s+([A-Z][a-z'-]+)",
        text,
        re.IGNORECASE,
    )
    industry_match = re.search(
        r"we(?:'re| are)\s+(?:a|an)\s+([^.!?]+)",
        customer_text,
        re.IGNORECASE,
    )
    industry = industry_match.group(1).strip() if industry_match else None
    if industry:
        industry = re.sub(r"\bdistributor\b", "distribution", industry, flags=re.I)
        industry = industry[:1].upper() + industry[1:]

    location_matches = []
    for name, location in CITY_STATES.items():
        match = re.search(rf"\b{re.escape(name)}\b", lower)
        if match:
            location_matches.append((match.start(), location))
    mentioned_locations = [
        location for _, location in sorted(location_matches)
    ]

    lane = Lane()
    if len(mentioned_locations) >= 2:
        origin, destination = mentioned_locations[:2]
        lane.origin_metro, lane.origin_state = origin
        lane.dest_metro, lane.dest_state = destination

    pallet_match = re.search(
        rf"\b(?P<value>{NUMBER})\s+(?:pallets?|skids?)\b",
        customer_text,
        re.IGNORECASE,
    )
    weight_match = re.search(
        rf"\b(?P<value>{NUMBER})\s+(?:pounds?|lbs?)\s+"
        r"(?:per|a|each)\s+(?:pallet|skid)\b",
        customer_text,
        re.IGNORECASE,
    )
    monthly_match = re.search(
        rf"\b(?P<value>{NUMBER})\s+(?:(?:shipments?|loads?)\s+)?"
        r"(?:per\s+month|a\s+month|monthly)\b",
        customer_text,
        re.IGNORECASE,
    )

    lane.pallets_per_shipment = (
        number(pallet_match.group("value")) if pallet_match else None
    )
    lane.weight_lb_per_pallet = (
        number(weight_match.group("value")) if weight_match else None
    )
    lane.shipments_per_month = (
        number(monthly_match.group("value")) if monthly_match else None
    )

    if "guaranteed" in lower:
        lane.service_level = "GUARANTEED"
    elif re.search(r"\b(?:expedited|rush|urgent)\b", lower):
        lane.service_level = "EXPEDITED"
    elif "standard" in lower:
        lane.service_level = "STANDARD"

    if "liftgate" in lower or "lift gate" in lower or "no dock" in lower:
        lane.accessorials.append("LIFTGATE_DEL")

    notes = []
    if "no dock" in lower and lane.dest_metro:
        notes.append(f"No dock at the {lane.dest_metro} branch.")
    if "proper dock" in lower and "forklift" in lower and lane.origin_metro:
        notes.append(f"{lane.origin_metro} origin has dock and forklift.")
    lane.notes = " ".join(notes)

    # Serviceability is deliberately left unknown. Rate-card code must set it.
    lanes = [lane] if lane.origin_metro and lane.dest_metro else []
    total = sum(item.shipments_per_month or 0 for item in lanes)

    return Proposal(
        call_id=metadata_value(text, "CALL") or transcript_path.stem,
        customer=Customer(
            company=metadata_value(text, "CUSTOMER"),
            contact=contact_match.group(1).title() if contact_match else None,
            industry=industry,
        ),
        lanes=lanes,
        total_monthly_shipments=total,
    )


def run_pipeline_no_ai(audio_file: str) -> str:

    facts = extract(audio_file)
    proposal = facts.model_dump_json(indent=2)

    output_path = Path(f"out/{audio_file}.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        proposal.model_dump_json(indent=2),
        encoding="utf-8",
    )

    return output_path

