from solution.extract.utils import LLM
from solution.extract.model_schema import Proposal
from solution.prompt import SYSTEM_PROMPT_COMPARE_PIPELINE


def run_compare_pipeline(old_proposal: Proposal, new_proposal: Proposal) -> dict:
    changes = {}

    def deep_compare(old: Proposal, new: Proposal, path="") -> None:
        if isinstance(old, dict):
            for key in (old if len(old) > len(new) else new):
                if (
                    key == "assumptions"
                    or key == "open_questions"
                    or key == "deal_summary"
                ):
                    continue
                if isinstance(old.get(key), list) or isinstance(old.get(key), dict):
                    try:
                        deep_compare(old[key], new[key], path + f"/{key}")
                    except KeyError:
                        if key not in old.keys():
                            print(f"Change at {path}/{key}: None -> {new[key]}")
                            changes[f"{path}/{key}"] = f"None -> {new[key]}"
                        else:
                            print(f"Change at {path}/{key}: {old[key]} -> None")
                            changes[f"{path}/{key}"] = f"{old[key]} -> None"
                else:
                    try:
                        if old[key] != new[key]:
                            print(f"Change at {path}/{key}: {old[key]} -> {new[key]}")
                            changes[f"{path}/{key}"] = f"{old[key]} -> {new[key]}"
                    except KeyError:
                        if key not in old.keys():
                            print(f"Change at {path}/{key}: None -> {new[key]}")
                            changes[f"{path}/{key}"] = f"None -> {new[key]}"
                        else:
                            print(f"Change at {path}/{key}: {old[key]} -> None")
                            changes[f"{path}/{key}"] = f"{old[key]} -> None"
        else:
            for i in range(len(old)):
                if isinstance(old[i], list) or isinstance(old[i], dict):
                    deep_compare(old[i], new[i], path + f"/{i}")
                else:
                    if old[i] != new[i]:
                        print(f"Change at {path}/{i}: {old[i]} -> {new[i]}")
                        changes[f"{path}/{i}"] = f"{old[i]} -> {new[i]}"

    deep_compare(old_proposal, new_proposal)

    model = LLM(system_prompt=SYSTEM_PROMPT_COMPARE_PIPELINE)
    response = model.get_response(user_prompt=f"Here are the changes {changes}")
    return {"summary": response}
