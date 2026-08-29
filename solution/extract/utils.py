from typing import List
import re
from dataclasses import dataclass


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

    def get_meta_data(self) -> str:
        meta_data = {}
        for md in self.metadata:
            if md.strip():
                key = re.findall(r"(.*):", md)
                value = re.findall(r":(.*)", md)
            meta_data[key[0]] = value[0]
        return meta_data
