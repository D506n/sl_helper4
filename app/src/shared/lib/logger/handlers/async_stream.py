from .aio_streams.abstract import AIOStream
from .aio_streams import AIOConsoleStream, AIOFileStream
from .base import BaseHandler, BaseHandlerConfig
from logging import INFO
import logging
from typing import Unpack
import asyncio
from warnings import warn
from typing import Literal

class AsyncStreamHandlerConfig(BaseHandlerConfig):
    level: int
    stream: type[AIOStream]

    @classmethod
    def default(cls):
        return {'level': INFO, 'stream': AIOConsoleStream}

    @classmethod
    def new(cls, **config:Unpack['AsyncStreamHandlerConfig']):
        current = cls.default()
        current.update(config)
        return current

class AsyncStreamHandler(BaseHandler):
    def __init__(self, 
                 level:int|str|Literal['default'] = 'default',
                 stream:Literal['console', 'file'] = 'console', 
                 fallback=True, 
                 formatter:logging.Formatter|Literal['default']|None='default'):
        super().__init__(level, fallback, formatter)
        self.stream = AIOConsoleStream() if stream == 'console' else AIOFileStream()
        self.queue:asyncio.Queue[logging.LogRecord] = asyncio.Queue()
        self.main_task:asyncio.Task = None

    def emit(self, record):
        self.queue.put_nowait(record)

    async def _main(self):
        while True:
            record = await self.queue.get()
            try:
                await self.stream.write(self.format(record))
            except Exception as e:
                warn(f'Cannot write to stream: {e}', stacklevel=2)
            self.queue.task_done()

    @classmethod
    async def setup(cls, **custom_config:Unpack['AsyncStreamHandlerConfig']):
        inst = cls(**AsyncStreamHandlerConfig.new(**custom_config))
        inst.main_task = asyncio.create_task(inst._main())
        inst.main_task.add_done_callback(inst.main_task_done)
        return inst