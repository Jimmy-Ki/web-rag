import requests
import json
import re
from typing import Generator


class GPTStreamer:
    def __init__(self, gpt_api_key: str, gpt_api_url: str, model: str, stream: bool, system_prompt: str, temperature: float):
        self.GPT_API_KEY = gpt_api_key
        self.GPT_API_URL = gpt_api_url
        self.model = model
        self.stream = stream
        self.system_prompt = system_prompt
        self.temperature = temperature
        print("最后接受的模型:" + self.model)

    def generate_response(self, prompt: str) -> Generator[str, None, None]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.GPT_API_KEY}"
        }

        gpt_data = {
            "model": self.model,
            "messages": prompt,
            "stream": self.stream,
            "temperature": self.temperature
        }

        response = requests.post(self.GPT_API_URL, headers=headers, json=gpt_data, stream=True)
        for line in response.iter_lines():
            if line:
                yield f"{line.decode('utf-8')}\n\n"
    def get_response(self, prompt: str) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.GPT_API_KEY}"
        }

        gpt_data = {
            "model": self.model,
            "messages": prompt,
            "stream": False,
            "temperature": self.temperature
        }

        response = requests.post(self.GPT_API_URL, headers=headers, json=gpt_data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']