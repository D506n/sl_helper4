from pathlib import Path
from httpx import AsyncClient
from argparse import ArgumentParser
from dataclasses import dataclass
from typing import TypedDict, Literal
import json
import asyncio
from logging import getLogger, DEBUG
from datetime import datetime, timedelta
from .src.models.node import NodeModel
from .src.finder import find

logger = getLogger(__name__)
logger.setLevel(DEBUG)

@dataclass
class Args:
    no_cache: bool
    cache_path: Path
    hosts_path: Path
    settings_path: Path

class Hosts(TypedDict):
    base: str
    ver: str
    node: str
    node_list: str
    node_tree: str
    project: str
    path: str

def parse_args() -> Args:
    parser = ArgumentParser()
    parser.add_argument('-nc', '--no-cache', action='store_true')
    parser.add_argument('-p', '--cache-path', type=Path, default=Path(__file__).parent / 'cache')
    parser.add_argument('--hosts-path', type=Path, default=Path(__file__).parent / 'hosts.json')
    parser.add_argument('--settings-path', type=Path, default=Path(__file__).parent / 'settings.json')
    namespace = parser.parse_args()
    return Args(namespace.no_cache, namespace.cache_path, namespace.hosts_path, namespace.settings_path)

def load_hosts(path: Path) -> Hosts:
    with open(path, 'r') as f:
        return json.load(f)

async def add_node_data(node:dict, client:AsyncClient):
    if 'link' not in node:
        logger.debug('Node %s has no link', node['fullPath'])
        return
    data = await client.get(node['link'])
    node['data'] = data.json()

def _save_cache(cache_path: Path, data: dict):
    cold_path = cache_path/'cold'
    if not cold_path.exists():
        cold_path.mkdir(parents=True)
    save_path = cold_path/(datetime.now().strftime('%Y-%m-%d')+'.json')
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
        logger.debug('Saved cold cache to %s', save_path)

def save_cache(cache_path: Path, data: dict):
    if not cache_path.exists():
        cache_path.mkdir(parents=True)
    _save_cache(cache_path, data)

def _load_cache(cold_path: Path, ttl: int):
    dt = datetime.now()
    files_dates = [datetime.strptime(f.stem, '%Y-%m-%d') for f in cold_path.iterdir() if f.is_file() and f.name.endswith('.json')]
    suitable_files = [f for f in files_dates if f > dt - timedelta(days=ttl)]
    if not suitable_files:
        return {}
    suitable_files.sort()
    with open(Path(cold_path/(suitable_files[-1].strftime('%Y-%m-%d')+'.json')), 'r', encoding='utf-8') as f:
        return json.load(f)

def load_cache(cache_path: Path, ttl: int):
    if not cache_path.exists():
        cache_path.mkdir(parents=True)
        return {}
    cache_path = cache_path/'cold'
    if not cache_path.exists():
        cache_path.mkdir(parents=True)
        cache = {}
    else:
        cache = _load_cache(cache_path, ttl)
    return cache

def json_to_nodes(json_data: list[dict]):
    return {node.full_path: node for node in [NodeModel(**node) for node in json_data]}

def print_result(result: list[NodeModel]):
    print('Результаты поиска:')
    for res in result:
        print(res.full_path)

async def main():
    args = parse_args()
    hosts = load_hosts(args.hosts_path)
    settings = json.loads(args.settings_path.read_text(encoding='utf-8'))
    if not args.no_cache:
        cache = load_cache(args.cache_path, settings['cache_ttl_days'])
    else:
        cache = {}
    to_find = input('Введите путь, который хотите найти: ')
    if cache:
        nodes = json_to_nodes(cache)
        result = find(to_find, nodes)
        print_result(result)
        return

    async with AsyncClient(base_url=hosts['base']+hosts['ver']) as client:
        node_list_resp = await client.get(hosts['node_list']+'?node='+hosts['project']+hosts['path']+'&nodeinfo=true&version=stable&versioninfo=true&fileinfo=true')
        raw_nodes = node_list_resp.json()
        base = client.base_url
        client.base_url = ''
        await asyncio.gather(*[add_node_data(node, client) for node in raw_nodes])
        client.base_url = base
        save_cache(args.cache_path, raw_nodes)
    nodes = json_to_nodes(raw_nodes)
    result = find(to_find, nodes)
    print_result(result)

if __name__ == '__main__':
    asyncio.run(main())