from typing import List
from dataclasses import dataclass
from solution.extract.model_schema import Proposal
from solution.extract.utils import LLM
from solution.extract.prompt import SYSTEM_PROMPT
from pathlib import Path
import re
import pickle as pkl


@dataclass
class TurnBundle:
    rep: str
    customer: str


class Dialogue:
    def __init__(self, path: str):
        with open(path, "r") as file:
            content: list = file.readlines()
        self.metadata = content[:5]
        self.dialogue = content[5:]

    def construct_turns(self) -> List[TurnBundle]:
        bundles: List[TurnBundle] = []
        rep_buffer: List[str] = []

        for raw in self.dialogue:
            line = raw.strip()
            if not line:
                continue

            m = re.match(r"\[\d{2}:\d{2}\]\s+(REP|CUSTOMER):\s*(.*)", line)
            if not m:
                continue

            speaker, text = m.group(1), m.group(2).strip()

            if speaker == "REP":
                rep_buffer.append(text)
            else:
                if rep_buffer:
                    bundles.append(
                        TurnBundle(
                            rep=" ".join(rep_buffer),
                            customer=text,
                        )
                    )
                    rep_buffer = []

        return bundles

    def get_meta_data(self):
        meta_data = {}
        for md in self.metadata:
            if md.strip():
                key = re.findall(r"(.*):", md)
                value = re.findall(r":(.*)", md)
            meta_data[key[0]] = value[0]
        return meta_data


def main():
    d_object = Dialogue(
        "/home/nsyn1/warp-proposal-challenge/calls/call_06_meridian.txt"
    )
    turns = d_object.construct_turns()
    meta_data = d_object.get_meta_data()
    model = LLM(system_prompt=SYSTEM_PROMPT)
    proposal = model.get_response(user_prompt=str(meta_data), Proposal=Proposal)

    print(f"Total turn dialogue {len(turns)}")
    for i, turn in enumerate(turns):
        print(f"Processing turn {i+1}...")
        proposal = model.get_response(
            user_prompt=f"REP: {turn.rep}, CUSTOMER: {turn.customer}",
            Proposal=Proposal,
        )

    print("Complete Processed Proposal.")

    model_history = model.get_history()

    with open("model_history.pkl", "wb") as file:
        pkl.dump(model_history, file)

    output_path = Path("out/call_06_meridian.txt.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        proposal.model_dump_json(indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
