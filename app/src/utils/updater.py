from pathlib import Path
from xxhash import xxh3_128_hexdigest
import json
from httpx import AsyncClient
# from ..shared.lib.logging.formatters import ColoredConsoleFormatter, MonocolorFormatter
# from ..shared.lib.logging.handlers import AsyncConsoleHandler, AsyncFileHandler
# import asyncio

APP_PATH = Path(__file__).parent.parent.parent

class Updater():
    def __init__(self, app_path:Path=None, cache_path:Path=None, updates_url:str=None):
        self.app_path = app_path or self.get_app_path()
        self.cache_path = cache_path or self.app_path/'data/update_cache'
        self.updates_url = updates_url or 'https://github.com/D506n/sl_helper4/releases/download/latest/update_cache.json'
        self.client = AsyncClient()

    def get_app_path(self):
        return Path(__file__).parent.parent.parent

    def get_file_hash(self, file_path: Path) -> str:
        with open(file_path, 'rb') as f:
            return xxh3_128_hexdigest(f.read())

def get_file_hash(file_path: Path) -> str:
    with open(file_path, 'rb') as f:
        return xxh3_128_hexdigest(f.read())

def scan_dir(root:Path, cache:dict[str, str], fmts:set[str], exclude:set[str]) -> dict[str, str]:
    if not isinstance(exclude, set):
        exclude = set(exclude)
    if not isinstance(fmts, list):
        fmts = list(fmts)
    for path in root.iterdir():
        if path.name in exclude or (path.is_file() and path.suffix not in fmts) or (path.is_dir() and path.name.startswith('__')):
            continue
        if path.is_dir():
            c = scan_dir(path, cache, fmts, exclude)
            cache.update(c)
            continue
        h = get_file_hash(path)
        if h != cache.get(path.name, None):
            cache[str(path).lower().replace(str(APP_PATH).lower(), 'app')] = h
    return cache

def work_dir(path:Path, cache_path:Path, fmts:set[str], exclude:set[str]):
    cache = scan_dir(path, {}, fmts, exclude)
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False)
    return cache

def read_cache(path:Path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    result = {'core': None, 'plugins':{}}
    app_path = Path.cwd()/'app'
    cache_path = Path.cwd()/'update_cache'
    if not cache_path.exists():
        cache_path.mkdir(parents=True, exist_ok=True)
    core_cache_path = cache_path/'core.json'
    if not core_cache_path.exists():
        result['core'] = work_dir(app_path, core_cache_path, ['.py'], {'__pycache__', '.venv', 'plugins'})
    else:
        result['core'] = read_cache(core_cache_path)
    plugins_path = app_path/'src/plugins'
    for plugin in plugins_path.iterdir():
        if plugin.is_dir() and not plugin.name.startswith('__'):
            plugin_cache_path = cache_path/f'{plugin.name}.json'
            if not plugin_cache_path.exists():
                result['plugins'][plugin.name] = work_dir(plugin, plugin_cache_path, ['.py'], {'__pycache__'})
            else:
                result['plugins'][plugin.name] = read_cache(plugin_cache_path)
    return result

if __name__ == "__main__":
    with open('test.json', 'w', encoding='utf-8') as f:
        json.dump(main(), f, ensure_ascii=False, indent=4)