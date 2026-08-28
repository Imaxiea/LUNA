"""
Description: 定义了一个抽象基类，用于简化后期方法定义流程，使程序更加规范高效。
"""
import logging
from abc import abstractmethod, ABC
from time import sleep, time

# Abstract Base Class
class BaseModel(ABC):
    def __init__(self, name, base_url, api_key):
        self.name = name
        self.base_url = base_url
        self.api_key = api_key
        self.logger = logging.getLogger(name)

    @staticmethod
    @abstractmethod
    def _build_request(prompt, t, **kwargs):
        pass

    @staticmethod
    @abstractmethod
    def _send_request(request_data, t):
        pass

    @staticmethod
    @abstractmethod
    def _parse_response(response, t):
        pass

    def call(self, prompt, tim, retries=1):
        start = time()
        for attempt in range(retries):
            try:
                request = self._build_request(prompt, tim)
                response = self._send_request(request[0], request[1])
                end = int((time()-start)*1000)
                return [self._parse_response(response[0], response[1]), end]
            except Exception as e:
                self.logger.error(e)
                sleep(2 ** attempt)
                continue

        return 0
