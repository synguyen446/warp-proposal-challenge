# from google import genai
# from google.genai import types
# client = genai.Client(api_key="")
# def get_flash_response(context, pydantic_format = None):
#     response = client.models.generate_content(
#         model="gemini-3.5-flash-lite",
#         contents=str(context),
#         config=types.GenerateContentConfig(
#             response_mime_type="application/json",
#             response_schema=pydantic_format.model_json_schema(),
#         ),
#     )
#     return response.text

# from ollama import chat
# def get_ollama_response(context, pydantic_format = None):
#     response = chat(
#                 model="qwen2.5:7b ",
#                 messages=context,
#                 format=pydantic_format.model_json_schema() if pydantic_format else None,
#             )
#     return response.message.content

class LLM:
    def __init__(self, system_prompt):
        self.context = [{"role": "system", "content": system_prompt}]

    def get_response(self, user_prompt: str, pydantic_format=None):

        self.context.append({"role": "user", "content": user_prompt})
        # message = get_ollama_response(self.context,pydantic_format)         # Change your AI model here; Your model should have some type of formatting
                                                                                        # like Pydantic or Json.
        message = get_flash_response(self.context,pydantic_format)  
        formatted_response = (
            pydantic_format.model_validate_json(message)
            if pydantic_format
            else message
        )
        self.context.append({"role": "assistant", "content": message})

        return formatted_response

    def get_history(self):
        return self.context