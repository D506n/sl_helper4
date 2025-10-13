from logging import Handler, INFO
from typing import Self
from typing import TypedDict, Unpack
from warnings import warn
import asyncio
import logging
from typing import Literal
from ..formatters import ColoredFormatter

class BaseHandlerConfig(TypedDict):
    level: int
    fail_if_not_connected: bool

    @classmethod
    def default(self):
        return {'level': INFO, 'fail_if_not_connected': True}

    @classmethod
    def new(cls, **config:Unpack['BaseHandlerConfig']):
        current = cls.default()
        current.update(config)
        return current

class BaseHandler(Handler):
    def __init__(self, level:str|int|Literal['default']='default', fallback=True, formatter:logging.Formatter|Literal['default']|None=None):
        if level == 'default':
            level = logging.getLogger().level
        super().__init__(level)
        self.fallback = fallback
        self.main_task:asyncio.Task = None
        if formatter == 'default':
            formatter = logging.getLogger().handlers[0].formatter
        self.setFormatter(formatter)

    def emit(self, record):
        super().emit(record)

    @classmethod
    async def setup(cls, **config:Unpack[BaseHandlerConfig]) -> Self:
        raise NotImplementedError()

    async def _main(self):
        raise NotImplementedError()

    async def arun_main(self):
        task_name = f'{self.__class__.__name__}_main_task'
        self.main_task = asyncio.create_task(self._main(), name=task_name)
        self.main_task.add_done_callback(self.main_task_done)

    def main_task_done(self, task:asyncio.Task):
        try:
            task.result()
        except Exception as e:
            if self.fallback:
                raise SystemExit(f'Logger fail: {e}')
            else:
                warn(f'Cannot connect to Kafka: {e}', stacklevel=2)