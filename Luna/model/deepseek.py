from typing import Any
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from Luna.model.Base import *
from openai import OpenAI, Stream
from pathlib import Path


class Archi(BaseModel):
    def __init__(self, name, base_url, api_key):
        super().__init__(name, base_url, api_key)
        self.api_key = self._load_api_key()
        self.base_url = "https://api.deepseek.com"

    @staticmethod
    def _build_request(prompt, **kwargs) -> dict:
        messages = [{"role": "user", "content": prompt}]
        if system_prompt := kwargs.get("system_prompt"):
            messages.insert(0, {"role": "system", "content": system_prompt})
        return {
            'model': 'deepseek-v4-pro',
            'messages': messages,
            'stream': False,
        }

    def _send_request(self, request_data) -> ChatCompletion | Stream[ChatCompletionChunk]:
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        response = client.chat.completions.create(**request_data)
        return response

    @staticmethod
    def _parse_response(response) -> list[Any | None]:
        message = response.choices[0].message
        thinking = getattr(message, "thinking", None) or \
                   getattr(message, "reasoning_content", None)
        content = message.content
        return [thinking, content]

    @staticmethod
    def _load_api_key() -> str | None:
        try:
            config_path = Path(__file__).parent / 'API_Keys' / 'apis'
            with open(config_path, 'r') as f:
                for line in f:
                    if 'Deepseek:' in line:
                        return line.replace('Deepseek:', '').strip()
            return None
        except FileNotFoundError:
            return None

