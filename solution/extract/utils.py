from ollama import chat


class LLM:
    def __init__(self, system_prompt):
        self.context = [{"role": "system", "content": system_prompt}]

    def get_response(self, user_prompt, Proposal):
        self.context.append({"role": "user", "content": user_prompt})
        response = chat(
            model="qwen2.5:7b ",
            messages=self.context,
            format=Proposal.model_json_schema(),
        )
        proposal = Proposal.model_validate_json(response.message.content)
        self.context.append({"role": "assistant", "content": response.message.content})

        return proposal

    def get_history(self):
        return self.context


# def update_log(current_proposal, new_proposal):
