import os
from typing import Optional

from dotenv import dotenv_values

try:
    # Official Mistral SDK
    from mistralai.client import MistralClient
except Exception as e:
    # Provide a helpful error on import problems
    raise ImportError("mistralai package is required. Please install with 'pip install mistralai'.") from e

CONFIG = dotenv_values("./config/.env")


class mistral_model:
    def __init__(self, model_name: str, system_prompt: str, api_key: Optional[str] = None):
        self.model_name = model_name
        self.system_prompt = system_prompt
        key = api_key or CONFIG.get("MISTRAL_API_KEY") or os.environ.get("MISTRAL_API_KEY")
        if not key:
            raise ValueError("MISTRAL_API_KEY not provided. Enter it in the UI or .env")
        self.client = MistralClient(api_key=key)

    def first_answer(self, prompt: str) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": str(prompt)},
        ]
        resp = self.client.chat(model=self.model_name, messages=messages)
        return resp.choices[0].message.content

    def second_answer(self, prompt, format_prompt: str) -> str:
        messages = [
            {"role": "system", "content": format_prompt},
            {"role": "user", "content": str(prompt)},
        ]
        resp = self.client.chat(model=self.model_name, messages=messages)
        return resp.choices[0].message.content
