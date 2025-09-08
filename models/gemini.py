import os
from typing import Optional

import google.generativeai as genai
from dotenv import dotenv_values

CONFIG = dotenv_values("./config/.env")


class gemini_model:
    def __init__(self, model_name: str, system_prompt: str, api_key: Optional[str] = None):
        """
        Google Gemini provider using google-generativeai SDK.
        Conforms to the same interface as other model services with
        first_answer(prompt) and second_answer(prompt, format_prompt).
        """
        self.model_name = model_name
        self.system_prompt = system_prompt
        key = api_key or CONFIG.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not key:
            raise ValueError("GOOGLE_API_KEY not provided. Please enter it in the UI or .env")
        genai.configure(api_key=key)
        self.client = genai.GenerativeModel(self.model_name)

    def _generate(self, parts: list[str]) -> str:
        # Compose a single text prompt; Gemini supports multi-part but text is fine here
        text = "\n\n".join(parts)
        resp = self.client.generate_content(text)
        return (resp.text or "").strip()

    def first_answer(self, prompt: str) -> str:
        return self._generate([
            self.system_prompt,
            prompt,
        ])

    def second_answer(self, prompt, format_prompt: str) -> str:
        # prompt here is the list; cast to string as in other models
        return self._generate([
            format_prompt,
            str(prompt),
        ])
