"""
Description: llama的本地模型调用逻辑。
"""
import requests
from Luna.model.Base import *
from time import time
import colorama


colorama.init()
class Use(BaseModel):
    def __init__(self, name, base_url, api_key):
        super().__init__(name, base_url, api_key)
        self.name = 'llama3.1:8b-instruct-q5_K_M'
        self.api_key = None
        self.base_url = 'http://localhost:11434/api/generate'

    @staticmethod
    def _build_request(prompt, t:int, **kwargs):
        start = time()
        messages = [{"role": "user", "content": prompt}]
        if system_prompt := kwargs.get("system_prompt"):
            messages.insert(0, {"role": "system", "content": system_prompt})
        print(f'llama请求已建立 (Duration Time: {int(time() - start + t)})')
        return [{
            'model': 'qwen2.5:14b',
            'prompt': messages,
            'stream': False,
        }, int(time() - start + t)]

    def _send_request(self, request_data, t:int):
        start = time()
        response = requests.post(self.base_url, request_data)
        print(f'qwen请求已发送 (Duration Time: {int(time() - start + t)})')
        return [response, int(time() - start + t)]

    @staticmethod
    def _parse_response(response, t:int):
        start = time()
        result = response.json()['response']
        print(f'llama请求已解析 (Duration Time: {int(time() - start + t)})')
        return [result, int(time() - start + t)]
