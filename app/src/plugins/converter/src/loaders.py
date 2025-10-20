import orjson
import openpyxl as excl
from pathlib import Path
import aiofiles
from aiofiles.base import AiofilesContextManager
from typing import AsyncGenerator, TextIO, TypeAlias, Callable, Any

progress_callback:TypeAlias = Callable[[int|float], None]
message_callback:TypeAlias = Callable[[str], None]

def json_read_gen(file:TextIO, progress:progress_callback=None):
    result = ''
    square_braces = 0
    curly_braces = 0
    read_progress = 0
    while True:
        line = file.readline()
        if '[' in line and square_braces == 0:
            square_braces += 1
            continue
        if ']' in line and square_braces == 1 and curly_braces == 0:
            break
        if '{' in line and square_braces == 0:
            continue
        if '{' in line and square_braces == 1:
            curly_braces += 1
        if '}' in line:
            curly_braces -= 1
        if '},' in line and curly_braces == 0:
            line = line.replace('},', '}')
        result += line.strip()
        read_progress += 1
        if result.endswith('}'):
            res:dict = orjson.loads(result)
            if progress != None:
                progress(read_progress)
            yield res
            result = ''

async def json_loader(obj:str|Path, optimized:bool=False, *args, **kwargs) -> list[dict]|AsyncGenerator[dict, Any, None]:

    if isinstance(obj, Path) and not optimized:
        async with aiofiles.open(obj, 'r', encoding='utf-8') as f:
            return orjson.loads(await f.read())

    elif isinstance(obj, str):
        return orjson.loads(obj)

    elif isinstance(obj, Path) and optimized:
        async with aiofiles.open(obj, 'r', encoding='utf-8') as f:
            return json_read_gen(f)

    else:
        raise NotImplementedError(f'Unknown object type and optimized combination: {type(obj)}, {optimized}')

def _fast_csv_reader(data:list[str], splitter:str=','):
    keys = data[0].split(splitter)
    data = data[1:]
    return [dict(zip(keys, row.split(splitter))) for row in data]

async def csv_read_gen(file:AiofilesContextManager, splitter:str=','):
    keys = None
    async for row in file:
        row: str
        if not keys:
            keys = row.split(splitter)
            continue
        yield dict(zip(keys, row.split(splitter)))

async def csv_loader(obj:str|Path, optimized:bool=False, splitter:str=',', *args, **kwargs) -> list[dict]|AsyncGenerator[dict, Any, None]:

    if isinstance(obj, Path) and not optimized:
        async with aiofiles.open(obj, 'r', encoding='utf-8') as f:
            data = await f.readlines()
            return _fast_csv_reader(data, splitter=splitter)

    elif isinstance(obj, str):
        return _fast_csv_reader(obj.splitlines(), splitter=splitter)

    elif isinstance(obj, Path) and optimized:
        async with aiofiles.open(obj, 'r', encoding='utf-8') as f:
            return await csv_read_gen(f, splitter=splitter)