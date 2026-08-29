from ollama import chat


def get_ollama_response(context, pydantic_format = None):
    response = chat(
                model="qwen2.5:7b ",
                messages=context,
                format=pydantic_format.model_json_schema() if pydantic_format else None,
            )
    return response.message.content

class LLM:
    def __init__(self, system_prompt):
        self.context = [{"role": "system", "content": system_prompt}]

    def get_response(self, user_prompt: str, pydantic_format=None):

        self.context.append({"role": "user", "content": user_prompt})
        message = get_ollama_response(self.context,pydantic_format)         # Change your AI model here; Your model should have sometype of formatting
                                                                                        # like Pydantic or Json.
        formatted_response = (
            pydantic_format.model_validate_json(message)
            if pydantic_format
            else message
        )
        self.context.append({"role": "assistant", "content": message})

        return formatted_response

    def get_history(self):
        return self.context