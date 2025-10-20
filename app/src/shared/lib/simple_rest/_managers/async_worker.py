import asyncio
import time
from pathlib import Path
from threading import Event, Thread
from typing import Awaitable, BinaryIO

from .._settings.settings import CONFIG


class WorkerStorage:
    worker:'SimpleRestWorker' = None

class TempFileCM():
    def __init__(self, file:BinaryIO, delete:bool=True):
        self.delete = delete
        self.file:BinaryIO = file
        self.path = Path(file.name)

    def __enter__(self):
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
        if self.delete:
            self.path.unlink()

class AsyncTask():
    def __init__(self, task:Awaitable):
        if not WorkerStorage.worker:
            raise WorkerNotInitialized()
        self.task = task
        self.done_event = Event()
        self.result = None

    async def __call__(self):
        self.result = await self.task
        self.done_event.set()

    def join(self):
        self.done_event.wait()
        return self.result

class AsyncTaskGroup(AsyncTask):
    def __init__(self, *tasks:AsyncTask):
        super().__init__(tasks)
        self.task: tuple[Awaitable]

    async def __call__(self):
        self.result = await asyncio.gather(*self.task, return_exceptions=True)
        self.done_event.set()

class StreamTask(AsyncTask):
    def __init__(self, task:Awaitable):
        super().__init__(task)

    async def __call__(self):
        return self.task

    def join(self):
        return self.task

class WorkerExists(Exception):
    def __init__(self):
        super().__init__('Worker already exists')

class WorkerNotInitialized(Exception):
    def __init__(self):
        super().__init__('Worker must be initialized example: worker = SimpleRestWorker()')

class SimpleRestWorker():
    def __init__(self):
        self.runned = True
        self.loop = asyncio.new_event_loop()
        self.thread = Thread(target=self.loop.run_forever)
        self.thread.start()
        if not WorkerStorage.worker:
            WorkerStorage.worker = self
        else:
            raise WorkerExists()
        self.refresh_task = self.execute_nowait(asyncio.to_thread(self.refresh_limit))

    def new_task(self, task:AsyncTask):
        fut = asyncio.run_coroutine_threadsafe(task(), self.loop)
        return fut

    def execute(self, task:Awaitable):
        internal_task = AsyncTask(task)
        self.new_task(internal_task)
        return internal_task.join()

    def execute_nowait(self, task:Awaitable):
        internal_task = AsyncTask(task)
        self.new_task(internal_task)
        return internal_task

    def execute_group(self, *tasks:Awaitable):
        internal_task = AsyncTaskGroup(*tasks)
        self.new_task(internal_task)
        return internal_task.join()

    def execute_group_nowait(self, *tasks:Awaitable):
        internal_task = AsyncTaskGroup(*tasks)
        self.new_task(internal_task)
        return internal_task

    def execute_stream(self, task:Awaitable):
        internal_task = StreamTask(task)
        self.new_task(internal_task)
        return internal_task.join()

    def execute_stream_nowait(self, task:Awaitable):
        internal_task = StreamTask(task)
        self.new_task(internal_task)
        return internal_task

    def stop(self):
        self.runned = False
        WorkerStorage.worker = None
        self.loop.stop()

    def refresh_limit(self):
        while self.runned:
            ref_delay = CONFIG.request_limit_period
            for i in range(ref_delay):
                time.sleep(1)
                if not self.runned:
                    return
            # limit_manager.refresh()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()