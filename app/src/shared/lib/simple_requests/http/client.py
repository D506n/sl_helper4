from httpx import AsyncClient, USE_CLIENT_DEFAULT
from contextlib import asynccontextmanager
from .req import HTTPRequest
from functools import wraps
from pydantic import BaseModel
from typing import AsyncIterator

def build_request_wrap(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        req = func(*args, **kwargs)
        req = HTTPRequest.from_request(req, body=kwargs.get("data"))
        req.resp_model = kwargs.get("resp_model")
        return req
    return wrapper

def send_wrap(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        resp = await func(*args, **kwargs)
        req: HTTPRequest = kwargs.get("request") or args[1]
        req.stream = kwargs.get("stream", False)
        req.resp_model = kwargs.get("resp_model")
        return req.parse_response(resp)
    return wrapper

class HTTPClient(AsyncClient):
    @build_request_wrap
    def build_request(self, method, url, *, content = None, data = None, files = None, json = None, params = None, headers = None, cookies = None, timeout = ..., extensions = None, resp_model: type[BaseModel] = None) -> HTTPRequest:
        timeout = USE_CLIENT_DEFAULT if timeout is ... else timeout
        return super().build_request(method, url, content=content, data=data, files=files, json=json, params=params, headers=headers, cookies=cookies, timeout=timeout, extensions=extensions)

    @send_wrap
    async def send(self, request: HTTPRequest, *, stream = False, auth = ..., follow_redirects = ..., resp_model: type[BaseModel] = None):
        auth = USE_CLIENT_DEFAULT if auth is ... else auth
        follow_redirects = USE_CLIENT_DEFAULT if follow_redirects is ... else follow_redirects
        return await super().send(request.original_request, stream=stream, auth=auth, follow_redirects=follow_redirects)

    @asynccontextmanager
    async def stream(self, method, url, *, content = None, data = None, files = None, json = None, params = None, headers = None, cookies = None, auth = ..., follow_redirects = ..., timeout = ..., extensions = None, resp_model: type[BaseModel] = None) -> AsyncIterator[HTTPRequest]:
        req = self.build_request(method, url, content=content, data=data, files=files, json=json, params=params, headers=headers, cookies=cookies, timeout=timeout, extensions=extensions, resp_model=resp_model)
        resp = await self.send(req, stream=True, auth=auth, follow_redirects=follow_redirects, resp_model=resp_model)
        try:
            yield resp
        finally:
            await resp.aclose()

    async def request(self, method, url, *, content = None, data = None, files = None, json = None, params = None, headers = None, cookies = None, auth = ..., follow_redirects = ..., timeout = ..., extensions = None, resp_model: type[BaseModel] = None):
        req = self.build_request(method, url, content=content, data=data, files=files, json=json, params=params, headers=headers, cookies=cookies, timeout=timeout, extensions=extensions, resp_model=resp_model)
        return await self.send(req, auth=auth, follow_redirects=follow_redirects, resp_model=resp_model)

    async def get(self, url, *, params = None, headers = None, cookies = None, auth = ..., follow_redirects = ..., timeout = ..., extensions = None, resp_model: type[BaseModel] = None):
        return await self.request('GET', url, params=params, headers=headers, cookies=cookies, auth=auth, follow_redirects=follow_redirects, timeout=timeout, extensions=extensions, resp_model=resp_model)

    async def post(self, url, *, content = None, data = None, files = None, json = None, params = None, headers = None, cookies = None, auth = ..., follow_redirects = ..., timeout = ..., extensions = None, resp_model: type[BaseModel] = None):
        return await self.request('POST', url, content=content, data=data, files=files, json=json, params=params, headers=headers, cookies=cookies, auth=auth, follow_redirects=follow_redirects, timeout=timeout, extensions=extensions, resp_model=resp_model)

    async def put(self, url, *, content = None, data = None, files = None, json = None, params = None, headers = None, cookies = None, auth = ..., follow_redirects = ..., timeout = ..., extensions = None, resp_model: type[BaseModel] = None):
        return await self.request('PUT', url, content=content, data=data, files=files, json=json, params=params, headers=headers, cookies=cookies, auth=auth, follow_redirects=follow_redirects, timeout=timeout, extensions=extensions, resp_model=resp_model)

    async def patch(self, url, *, content = None, data = None, files = None, json = None, params = None, headers = None, cookies = None, auth = ..., follow_redirects = ..., timeout = ..., extensions = None, resp_model: type[BaseModel] = None):
        return await self.request('PATCH', url, content=content, data=data, files=files, json=json, params=params, headers=headers, cookies=cookies, auth=auth, follow_redirects=follow_redirects, timeout=timeout, extensions=extensions, resp_model=resp_model)

    async def head(self, url, *, params = None, headers = None, cookies = None, auth = ..., follow_redirects = ..., timeout = ..., extensions = None, resp_model: type[BaseModel] = None):
        return await self.request('HEAD', url, params=params, headers=headers, cookies=cookies, auth=auth, follow_redirects=follow_redirects, timeout=timeout, extensions=extensions, resp_model=resp_model)

    async def delete(self, url, *, params = None, headers = None, cookies = None, auth = ..., follow_redirects = ..., timeout = ..., extensions = None, resp_model: type[BaseModel] = None):
        return await self.request('DELETE', url, params=params, headers=headers, cookies=cookies, auth=auth, follow_redirects=follow_redirects, timeout=timeout, extensions=extensions, resp_model=resp_model)

    async def options(self, url, *, params = None, headers = None, cookies = None, auth = ..., follow_redirects = ..., timeout = ..., extensions = None, resp_model: type[BaseModel] = None):
        return await self.request('OPTIONS', url, params=params, headers=headers, cookies=cookies, auth=auth, follow_redirects=follow_redirects, timeout=timeout, extensions=extensions, resp_model=resp_model)