import json
from solution.prompt import SYSTEM_PROMPT_DATA
from solution.AI.model_schema import Proposal_addon, Rationale
from solution.AI.model import LLM
import pickle as pkl

def llm_evaluate(proposal_file: str):    
    model = LLM(system_prompt=SYSTEM_PROMPT_DATA)

    with open(
            proposal_file,
            "r",
        ) as file:
            proposal = json.load(file)
    lanes = proposal["lanes"]

    for lane in lanes:
        response = model.get_response(
                user_prompt=f"{str(lane)} rationale per lane - one sentence on why this mode and service level.",
                pydantic_format=Rationale,
            )
        lane["rationale"] = response.model_dump()["rationale"]


    with open("./model_history.pkl", "rb") as file:
        model_history = pkl.load(file)

    response = model.get_response(
            user_prompt=f"Data: {str(lane)}, Dialogue: {str(model_history)}",
            pydantic_format=Proposal_addon,
        )

    
    for category in response.model_dump().keys():
        proposal[category] = response.model_dump()[category]

    with open(f'{proposal_file}_with_ai', "w") as f:
        json.dump(proposal, f, indent=2)

