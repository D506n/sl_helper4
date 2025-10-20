from fastapi import Request, Response
from typing import Callable, Awaitable
from logging import getLogger
from typing import Literal
from fastapi.responses import RedirectResponse, FileResponse
from asyncio import iscoroutinefunction

logger = getLogger('http')

def logging_middleware(log_level:Literal['debug', 'info', 'warning', 'error', 'critical'] = 'info'):
    async def logging_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]):
        logger.debug("Request: %s %s", request.method, request.url)
        try:
            result = await call_next(request)
        except Exception as e:
            logger.error("Exception: %s", e)
            return
        status = str(result.status_code)
        if (request.url.path != "/health" or log_level == "debug") and result.status_code < 400:
            logger.info("%s %s code: %s", request.method, request.url, status)
        elif result.status_code >= 400:
            logger.error("%s %s code: %s", request.method, request.url, status)
        return result
    return logging_middleware

def redirect_middleware(redirect_mapping: dict[str, str|Awaitable[Response]]):
    '''Мидлварь для обхода перехвата запросов nicegui. Когда нужно чтобы отработало как fastapi а не nicegui.'''
    async def redirect_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]):
        if request.url.path in redirect_mapping:
            if iscoroutinefunction(redirect_mapping[request.url.path]):
                return await redirect_mapping[request.url.path]()
            elif 'favicon.ico' in request.url.path:
                return FileResponse(redirect_mapping[request.url.path])
            return RedirectResponse(redirect_mapping[request.url.path])
        return await call_next(request)
    return redirect_middleware