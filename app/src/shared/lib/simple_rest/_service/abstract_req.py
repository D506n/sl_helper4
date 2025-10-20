import threading
from contextlib import _AsyncGeneratorContextManager
from pathlib import Path

from httpx import Response
from pydantic import BaseModel

from .._service.response_model import ResponseModel


class PydanticModel(BaseModel):pass
class ErrorModel(BaseModel):pass

class AbstractReq():
    __slots__ = ('req_type', 'url', 'headers', 'data', 'result', 'retries', 'retry_delay', 'timeout', 'cookie', 
                 'verify', 'sess_name', 'sess_wait', 'response', 'result_event', 'response_model', 'check', 'files',)
    def __init__(self, url:str, req_type='GET', data: dict=None, headers:dict=None, cookie:dict=None, verify:dict=None,
                 retries=5, retry_delay=5, timeout=10, sess_name:str='Base', sess_wait_sec:float=5, files:list[Path]=None,
                 response_model:PydanticModel=None):
        self.req_type = req_type
        self.url = url
        self.headers = headers
        self.data = data
        self.result: ResponseModel|_AsyncGeneratorContextManager[Response] = None
        self.retries = retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.cookie = cookie
        self.verify = verify
        self.sess_name = sess_name
        self.sess_wait = sess_wait_sec
        self.response = None
        self.result_event = threading.Event()
        self.response_model = response_model
        self.check = None
        self.files = files