"""
Description: 定义了一个抽象基类，用于简化后期方法定义流程，使程序更加规范高效。
"""
import logging
from abc import abstractmethod, ABC
from time import sleep

# Abstract Base Class
class BaseModel(ABC):
    def __init__(self, name, base_url, api_key):
        self.name = name
        self.base_url = base_url
        self.api_key = api_key
        self.logger = logging.getLogger(name)

    @staticmethod
    @abstractmethod
    def _build_request(prompt, **kwargs):
        pass

    @staticmethod
    @abstractmethod
    def _send_request(request_data):
        pass

    @staticmethod
    @abstractmethod
    def _parse_response(response):
        pass

    def call(self, prompt, retries=1):
        for attempt in range(retries):
            try:
                request = self._build_request(prompt)
                response = self._send_request(request)
                return self._parse_response(response)
            except Exception as e:
                self.logger.error(e)
                sleep(2 ** attempt)
                continue

        return 0
