"""
Description: deepseek的云端API调用逻辑。
"""
from typing import Any
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from Luna.model.Base import *
from openai import OpenAI, Stream
from pathlib import Path
from time import time
from colorama import init, Fore


init()
class Use(BaseModel):
    def __init__(self, name, base_url, api_key):
        super().__init__(name, base_url, api_key)
        self.name = 'Deepseek'
        self.api_key = self._load_api_key()
        self.base_url = "https://api.deepseek.com"
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    @staticmethod
    def _build_request(prompt, t:int, **kwargs) -> list[dict[str, str | list[dict[str, str | Any]] | bool] | int]:
        start = time()
        messages = [{"role": "user", "content": prompt}]
        if system_prompt := kwargs.get("system_prompt"):
            messages.insert(0, {"role": "system", "content": system_prompt})
        print(Fore.GREEN + f'{Fore.CYAN}[DEEPSEEK]{Fore.RESET} 请求已建立 (Duration Time: {int(time()-start+t)})')
        return [{
            'model': 'deepseek-v4-pro',
            'messages': messages,
            'stream': False,
        }, int(time()-start+t)]

    def _send_request(self, request_data, t:int) -> list[ChatCompletion | Stream[ChatCompletionChunk] | int]:
        start = time()
        response = self.client.chat.completions.create(**request_data)
        print(Fore.GREEN + f'{Fore.CYAN}[DEEPSEEK]{Fore.RESET} 请求已发送 (Duration Time: {int(time() - start + t)})')
        return [response, int(time()-start+t)]

    @staticmethod
    def _parse_response(response, t:int) -> list[Any | None]:
        start = time()
        message = response.choices[0].message
        thinking = getattr(message, "thinking", None) or \
                   getattr(message, "reasoning_content", None)
        content = message.content
        print(Fore.GREEN + f'{Fore.CYAN}[DEEPSEEK]{Fore.RESET} 请求已解析 (Duration Time: {int(time() - start + t)})')
        return [[thinking, content], int(time()-start+t)]

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

