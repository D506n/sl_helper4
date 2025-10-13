import logging
import os
import orjson
import sys

from pydantic import BaseModel
from pathlib import Path
from .handlers.base import BaseHandler, BaseHandlerConfig
from ._shared import Static
from typing import TypedDict, Literal, TypeAlias, Unpack
from io import StringIO


LOGGING_LEVELS: TypeAlias = Literal[0, 10, 20, 30, 40, 50, 'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

class SubloggerConfig(TypedDict):
    name: str
    level: LOGGING_LEVELS | None
    fmt: str | None
    datefmt: str | None

class LoggerConfig(TypedDict):
    filename: Path | None
    filemode: str
    format: str
    datefmt: str | None
    style: str
    level: LOGGING_LEVELS | None
    stream: StringIO | None
    force: bool | None
    encoding: str | None
    errors: str | None

def get_config(custom_config:LoggerConfig=None):
    '''Собирает конфигурацию логгера из конфигурационного файла или переменной окружения LOGGER_CONFIG. А так же добавляет к ней
    настройки из переменной custom_config.'''
    config = {
        'filename': None,
        'filemode': 'a',
        'format': '[%(levelname)s|%(name)s:%(lineno)-3s|%(asctime)s] %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S',
        'style': None,
        'level': 20,
        'stream': sys.stdout,
        'force': True,
        'encoding': 'utf-8',
        'errors': None
        }
    if os.getenv('LOGGER_CONFIG'):
        config_path = Path(os.getenv('LOGGER_CONFIG'))
    else:
        config_path = Path(__file__).cwd() / 'logger.json'
    if config_path.exists():
        with open(config_path, 'r') as f:
            new_config = orjson.loads(f.read())
    else:
        new_config = {}
    if new_config:
        config.update(new_config)
    if custom_config:
        config.update(custom_config)
    return config

def setup_root_logger(logger_cls:type[logging.Logger]=None, 
                      formatter:logging.Formatter=None, 
                      **custom_config:Unpack[LoggerConfig]):
    '''Настраивает корневой логгер.'''
    config = get_config(custom_config)
    if logger_cls:
        logging.setLoggerClass(logger_cls)
    config = {key: value for key, value in config.items() if value is not None}
    logging.basicConfig(**config)
    root_logger = logging.getLogger()
    root_logger.setLevel(config.get('level', 20))
    if formatter:
        root_logger.handlers[0].setFormatter(formatter)
        Static.formatter = formatter
    Static.root = root_logger
    root_logger.info('Logger setup complete')

async def setup_handlers(*handlers:tuple[type[BaseHandler], Unpack[BaseHandlerConfig]], rewrite:bool=True):
    if not Static.root:
        raise RuntimeError('Root logger not initialized')
    if rewrite:
        Static.root.handlers = []
    for hndlr in handlers:
        if len(hndlr) == 2:
            handler, config = hndlr
        else:
            handler, config = hndlr[0], {}
        hnd = await handler.setup(**config)
        if Static.formatter:
            hnd.setFormatter(Static.formatter)
        Static.root.addHandler(hnd)
        Static.root.info(f'Handler {handler.__name__} added')

async def add_handlers(*handlers:BaseHandler, rewrite:bool=True):
    if not Static.root:
        raise RuntimeError('Root logger not initialized')
    if not handlers:
        return
    if rewrite:
        Static.root.handlers = []
    for hndlr in handlers:
        await hndlr.arun_main()
        Static.root.addHandler(hndlr)
        Static.root.info(f'Handler {hndlr.__class__.__name__} added')

def setup_subloggers(*configs:SubloggerConfig):
    if not Static.root:
        raise RuntimeError('Root logger not initialized')
    for config in configs:
        logger = logging.getLogger(config['name'])
        level = config.get('level')
        fmt = config.get('fmt')
        datefmt = config.get('datefmt')
        if level:
            logger.setLevel(level)
        if fmt:
            if logger.handlers:
                for handler in logger.handlers:
                    handler.setFormatter(type(handler.formatter)(fmt, datefmt))
            else:
                for handler in Static.root.handlers:
                    hcls = type(handler)
                    new_handler = hcls()
                    new_handler.setLevel(level)
                    new_handler.setFormatter(type(handler.formatter)(fmt, datefmt))
                    logger.addHandler(new_handler)