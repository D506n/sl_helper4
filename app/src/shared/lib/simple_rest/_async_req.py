import asyncio
import json
import mimetypes
from asyncio import Task
from functools import wraps
from pathlib import Path
from typing import Awaitable

import httpx

from ._managers.limit_manager import AsyncLimitManager
from ._managers.xconnect_manager import Sess, sess_mngr
from ._service.abstract_req import AbstractReq, PydanticModel
from ._service.response_model import ResponseModel


class AsyncReq(AbstractReq):
    def __init__(self, url: str, req_type='GET', data: dict = None, headers: dict = None, cookie:dict=None, 
                 verify: dict = None, retries=5, retry_delay=5, timeout=10, sess_name: str = 'Base',
                 sess_wait_sec: float = 5, callback:Awaitable=None, files:list[Path]=None, response_model:PydanticModel=None,
                 limiter:AsyncLimitManager=None):
        super().__init__(url, req_type, data, headers, cookie, verify, retries, retry_delay, timeout, 
                         sess_name, sess_wait_sec, files=files, response_model=response_model)
        self.result_event = asyncio.Event()
        self.callback = callback
        self.callback_task: Task = None
        self.need_retry = False
        self.limiter = limiter
        if self.retries > 0:
            self.need_retry = True

    @staticmethod
    def __set_ready(func):
        @wraps(func)
        async def wrapper(obj:'AsyncReq', *args, **kwargs):
            try:
                result = await func(obj, *args, **kwargs)
            except:
                pass
            obj.result_event.set()
            return result
        return wrapper

    @staticmethod
    def __sync_set_ready(func):
        @wraps(func)
        def wrapper(obj:'AsyncReq', *args, **kwargs):
            try:
                result = func(obj, *args, **kwargs)
            except:
                pass
            obj.result_event.set()
            return result
        return wrapper

    @staticmethod
    def __get_connect(func):
        @wraps(func)
        async def wrapper(obj:'AsyncReq', *args, **kwargs):
            sess:Sess = await sess_mngr.get_sess(obj)
            result = await func(obj, *args, **kwargs, sess=sess)
            asyncio.create_task(sess.release_sess())
            return result
        return wrapper

    @staticmethod
    def __callback_send(func):
        @wraps(func)
        async def wrapper(obj:'AsyncReq', *args, **kwargs):
            result = await func(obj, *args, **kwargs)
            if isinstance(obj.callback, Awaitable):
                obj.callback_task = asyncio.create_task(obj.callback)
            elif not obj.callback == None:
                raise TypeError('Callback must be awaitable')
            return result
        return wrapper

    @staticmethod
    def __sync_callback_send(func):
        @wraps(func)
        def wrapper(obj:'AsyncReq', *args, **kwargs):
            result = func(obj, *args, **kwargs)
            if isinstance(obj.callback, Awaitable):
                obj.callback_task = asyncio.create_task(obj.callback)
            elif not obj.callback == None:
                raise TypeError('Callback must be awaitable')
            return result
        return wrapper

    @staticmethod
    def __result_to_model(func):
        @wraps(func)
        async def wrapper(obj:'AsyncReq', *args, **kwargs):
            try:
                result = await func(obj, *args, **kwargs)
                if isinstance(result, ResponseModel):
                    obj.result = result
                    return obj.result
            except Exception as e:
                obj.result = ResponseModel.from_exception(e)
            else:
                obj.result = ResponseModel.from_response(result)
            return obj.result
        return wrapper

    @staticmethod
    def __retry(func):
        @wraps(func)
        async def wrapper(obj:'AsyncReq', *args, **kwargs):
            while obj.retries > 0:
                try:
                    await func(obj, *args, **kwargs)
                except Exception as e:
                    obj.result = ResponseModel.from_exception(e)
                    return obj.result
                if obj.response.status_code in range(500, 600):
                    obj.retries -= 1
                else:
                    return obj.response
            last_response = ResponseModel.from_response(obj.response)
            obj.result = ResponseModel.from_exception(Exception('Retries exceeded'))
            obj.result.data = {'last_response': last_response.model_dump()}
            return obj.result
        return wrapper

    async def pack_files(self):
        '''Пакует список файлов в формат `{"file": (file.name, file.read_bytes(), mimetypes.guess_type(file)[0])}`'''
        files = {}
        for file in self.files:
            files['file'] = (file.name, file.read_bytes(), mimetypes.guess_type(file)[0])
        return files

    async def get_result(self, dump:bool=False):
        if self.result == None:
            await self.send()
            await self.result_event.wait()
        if dump:
            return self.result.model_dump()
        return self.result

    @__set_ready
    @__result_to_model
    @__get_connect
    @__callback_send
    @__retry
    async def send(self, *, sess:Sess):
        if self.limiter != None:
            await self.limiter.acquire()
        if isinstance(self.data, dict):
            self.data = json.dumps(self.data)
        if self.files != None and len(self.files) > 0:
            files = await self.pack_files()
        else:
            files = None
        if self.headers != None and self.headers.keys() != sess.headers.keys():
            sess.headers.update(self.headers)
        if self.cookie != None and self.cookie.keys() != sess.cookies.keys():
            sess.cookies.update(self.cookie)
        self.response = await sess.request(self.req_type, self.url, data=self.data, timeout=self.timeout, files=files)
        return self.response

    @__sync_set_ready
    @__sync_callback_send
    def sync_get_byte_stream(self, chunk_size=1024):
        if self.limiter != None:
            self.limiter.acquire()
        if isinstance(self.data, dict):
            self.data = json.dumps(self.data)
        if self.verify == None:
            verify = False
        else:
            verify = True
        if verify:
            cert = self.verify
        else:
            cert = None
        with httpx.Client(verify=verify, cert=cert) as client:
            response = client.request(self.req_type, self.url, data=self.data, headers=self.headers, cookies=self.cookie, timeout=self.timeout)
            for chunk in response.iter_bytes(chunk_size=chunk_size):
                yield chunk

    @__set_ready
    @__callback_send
    async def get_byte_stream(self, chunk_size=1024):
        if self.limiter != None:
            await self.limiter.acquire()
        sess = await sess_mngr.get_sess(self)
        if isinstance(self.data, dict):
            self.data = json.dumps(self.data)
        async with sess.stream(self.req_type, self.url, data=self.data, headers=self.headers, cookies=self.cookie, timeout=self.timeout) as self.response:
            async for chunk in self.response.aiter_bytes(chunk_size=chunk_size):
                if chunk == b'{"detail":"Not Found"}' in chunk:
                    self.result = ResponseModel(status_code=404, headers=self.response.headers, data={})
                else:
                    yield chunk

    async def _byte_gen(self, data:bytes, chunk_size=1024):
        while data:
            yield data[:chunk_size]
            data = data[chunk_size:]

    async def _path_gen(self, path:Path, chunk_size=1024):
        with open(path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    async def _choice_gen(self, data:bytes|Path, chunk_size=1024):
        if isinstance(data, Path):
            return await self._path_gen(data, chunk_size)
        else:
            return await self._byte_gen(data, chunk_size)

    async def send_byte_stream(self, data:bytes|Path, chunk_size=1024):
        if self.limiter != None:
            await self.limiter.acquire()
        self.data = await self._choice_gen(data, chunk_size)
        await self.send()