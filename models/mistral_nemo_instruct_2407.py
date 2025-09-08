from huggingface_hub import InferenceClient
from dotenv import dotenv_values
import os

CONFIG = dotenv_values("./config/.env")


class mistral_nemo_instruct_2407:

    def __init__(self, model_name, system_prompt, api_key: str | None = None):
        """
        Initializes the Mistral-Nemo-Instruct-2407 with the given parameters.

        Parameters:
        model_name (str): The name of the model to use.
        system_prompt (str): The system prompt to use.
        """
        self.model_name = model_name
        token = api_key or CONFIG.get("HF_API_TOKEN") or os.environ.get("HF_API_TOKEN")
        self.client = InferenceClient(
            repo_id=self.model_name,
            token=token,
        )
        self.system_prompt = system_prompt

    def first_answer(self, prompt):
        """
        Generates a response from the model based on the provided prompt.

        Parameters:
        prompt (str): The user query to generate a response for.

        Returns:
        str: The response from the model as a string formatted as a list.
        """

        response1 = self.client.chat_completion(
            messages=[{"role": "system", "content": self.system_prompt},
                      {"role": "user", "content": prompt}],
            max_tokens=500)
        return response1.choices[0].message.content

    def second_answer(self, prompt, format_prompt):
        """
        Generates a response from the model based on the provided prompt and a format prompt.

        Parameters:
        prompt (str): The user query to generate a response for.

        Returns:
        str: The response from the model as a string formatted as a list.
        """
        response2 = self.client.chat_completion(
            messages=[{"role": "system", "content": format_prompt},
                      {"role": "user", "content": f"{prompt}"}],
            max_tokens=500)
        return response2.choices[0].message.content
