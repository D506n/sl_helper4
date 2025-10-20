import asyncio
import threading
from functools import wraps

THREAD_SEMAPHORE = threading.Semaphore(1)
ASYNC_SEMAPHORE = asyncio.Semaphore(1)

def thread_safe(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        THREAD_SEMAPHORE.acquire()
        result = func(*args, **kwargs)
        THREAD_SEMAPHORE.release()
        return result
    return wrapper

def async_safe(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        await ASYNC_SEMAPHORE.acquire()
        result = await func(*args, **kwargs)
        ASYNC_SEMAPHORE.release()
        return result
    return wrapper