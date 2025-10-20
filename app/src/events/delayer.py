import asyncio
from logging import getLogger
from nicegui import Event

logger = getLogger(__name__)

class EventDelayer():
    def __init__(self, event: Event, delay:int=0.5):
        self.delay = delay
        self.new_event = asyncio.Event()
        self.delay_now = False
        self.semaphore = asyncio.Semaphore(1)
        self.current_e = None
        self.bg_task = None
        self.event = event
        self.que = asyncio.Queue()

    async def wait_new_events(self, current_e):
        await asyncio.sleep(self.delay)
        while self.new_event.is_set():
            self.new_event.clear()
            while not self.que.empty():
                current_e = await self.que.get()
            await asyncio.sleep(self.delay)
        return current_e

    async def run(self):
        while True:
            e = await self.wait_new_events(await self.que.get())
            self.event.emit(e)

    def got_event(self, e):
        self.new_event.set()
        self.que.put_nowait(e)
        if self.bg_task is None:
            self.bg_task = asyncio.create_task(self.run())

class RunDelayer():
    def __init__(self, delayed_coro, delay:int=0.5):
        self.delay = delay
        self.new_event = asyncio.Event()
        self.delay_now = False
        self.semaphore = asyncio.Semaphore(1)
        self.current_e = None
        self.bg_task = None
        self.delayed_coro = delayed_coro
        self.que = asyncio.Queue()

    async def wait_new_events(self, current_e: Event):
        await asyncio.sleep(self.delay)
        while self.new_event.is_set():
            self.new_event.clear()
            while not self.que.empty():
                current_e = await self.que.get()
            await asyncio.sleep(self.delay)
        return current_e

    async def run(self):
        while True:
            e = await self.wait_new_events(await self.que.get())
            await self.delayed_coro(e)

    async def got_event(self, e: Event):
        self.new_event.set()
        await self.que.put(e)
        if self.bg_task is None:
            self.bg_task = asyncio.create_task(self.run())