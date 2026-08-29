from solution.AI.model_schema import Proposal
from solution.AI.model import LLM
from solution.extract.utils import Dialogue
from solution.prompt import SYSTEM_PROMPT_EXTRACT
from pathlib import Path
import pickle as pkl


def extract_data(audio_file: str) -> str:
    d_object = Dialogue(audio_file)
    turns = d_object.construct_turns()
    meta_data = d_object.get_meta_data()
    model = LLM(system_prompt=SYSTEM_PROMPT_EXTRACT)

    proposal = model.get_response(user_prompt=str(meta_data), pydantic_format=Proposal)

    print(f"Total turn dialogue {len(turns)}")
    for i, turn in enumerate(turns):
        print(f"Processing turn {i+1}...")
        proposal = model.get_response(
            user_prompt=f"REP: {turn.rep}, CUSTOMER: {turn.customer}",
            pydantic_format=Proposal,
        )
        output_path = Path(f"out/intermidate/{audio_file}.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
                proposal.model_dump_json(indent=2),
                encoding="utf-8",
            )
        input()

    print("Complete Processed Proposal.")

    model_history = model.get_history()

    with open("model_history.pkl", "wb") as file:
        pkl.dump(model_history, file)

    output_path = Path(f"out/{audio_file}.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        proposal.model_dump_json(indent=2),
        encoding="utf-8",
    )

    return output_path
