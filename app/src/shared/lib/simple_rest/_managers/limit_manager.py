import asyncio
import threading
import time
from datetime import datetime

from .._settings.settings import CONFIG


class AbstractLimitManager():
    def __init__(self, value: int = 100, refresh_period: int = 60, name='AbstractLimiter', debug:bool=False) -> None:
        self.value = value
        self.refresh_period = refresh_period
        self.name = name
        self.semaphore = threading.Semaphore(value)
        self.alive = True
        self.th = threading.Thread(target=self.main, daemon=True, name=self.name)
        self.debug = debug

    def start(self):
        self.th.start()

    def main(self):
        while self.alive:
            self.refresh()
            time.sleep(self.refresh_period)

    def refresh(self):
        dif = self.value - self.semaphore._value
        for _ in range(dif):
            self.semaphore.release()

    def stop(self):
        self.alive = False

    def acquire(self, blocking: bool = True, timeout: float | None = None) -> bool:
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError()

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError()

    async def __aenter__(self):
        raise NotImplementedError()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError()

class SyncLimitManager(AbstractLimitManager):
    def __init__(self, value: int = 100, refresh_period: int = 60, debug: bool = False) -> None:
        super().__init__(value, refresh_period, 'SyncLimitManager_refresh', debug=debug)
        self.semaphore: threading.Semaphore

    def acquire(self, blocking: bool = True, timeout: float | None = None):
        if self.debug and self.semaphore._value - 1 == 0:
            print(f'[{datetime.now().strftime("%H:%M:%S")}]{CONFIG.texts.limit_reached}')
        return self.semaphore.acquire(blocking, timeout)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

class AsyncLimitManager(AbstractLimitManager):
    def __init__(self, value: int = 100, refresh_period: int = 60, debug: bool = False) -> None:
        self.value = value
        self.initial_value = value
        self.refresh_period = refresh_period
        self.semaphore = asyncio.Semaphore(1)
        self.event = asyncio.Event()
        self.debug = debug
        self.alive = True

    async def acquire(self) -> bool:
        await self.semaphore.acquire()
        if self.debug and self.value - 1 <= 0:
            print(f'[{datetime.now().strftime("%H:%M:%S")}]{CONFIG.texts.limit_reached}')
        if self.value - 1 <= 0:
            self.event.clear()
            await self.event.wait()
        self.value -= 1
        self.semaphore.release()

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.stop()
    
    async def main(self):
        while self.alive:
            await self.refresh()
            await asyncio.sleep(self.refresh_period)

    async def refresh(self):
        if self.debug:
            print(f'[{datetime.now().strftime("%H:%M:%S")}]{CONFIG.texts.limit_refreshed}')
        self.value = self.initial_value
        self.event.set()

    async def start(self):
        asyncio.create_task(self.main())