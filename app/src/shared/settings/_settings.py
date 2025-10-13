from pathlib import Path
from aiosqlite import connect, Connection
import orjson
from typing import Awaitable

TABLE_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    type TEXT,
    control TEXT,
    init_params TEXT,
    group_name TEXT
)
"""

def convert(value:str, type_string):
    match type_string:
        case 'str':
            return value
        case 'int':
            return int(value)
        case 'float':
            return float(value)
        case 'bool':
            return bool(value)
        case 'dict':
            return orjson.loads(value)
        case 'list':
            return [v.strip() for v in value.split(',')]
        case _:
            raise ValueError(f"Unknown type: {type_string}")

def type_conversion(func):
    async def wrapper(*args, **kwargs):
        result, type_string = await func(*args, **kwargs)
        result = convert(result, type_string)
        return result
    return wrapper

class SettingsProvider():
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.__db: Connection = None
        self.refresh_callback: Awaitable = None

    async def start(self):
        if not self.db_path.exists():
            self.db_path.touch()
            self.__db = await connect(self.db_path)
            await self.apply_defaults()
        else:
            self.__db = await connect(self.db_path)

    async def apply_defaults(self):
        try:
            async with self.db.execute(TABLE_CREATE_SQL):
                await self.db.commit()
            data = orjson.loads((self.db_path.parent / 'defaults.json').read_text())
            for setting in data:
                await self.set(**setting)
            await self.db.commit()
        except Exception as e:
            print(e)

    async def stop(self):
        await self.db.close()

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    @property
    def db(self) -> Connection:
        return self.__db

    def standard_init_params(self, control: str, value: str) -> dict:
        match control:
            case 'TextField':
                return str({'value': value})
            case 'Dropdown':
                options = [v.strip() for v in value.split(',')]
                return str({'options': options, 'value': options[0]})
            case _:
                return str({})

    async def set(self, key: str, value: str, type_str: str = None, control: str = None, init_params: dict = None, group: str = None):
        current_data = await self.get(key, need_all=True)
        if current_data is not None:
            if type_str is None:
                type_str = current_data[2]
            if control is None:
                control = current_data[3]
            if init_params is None:
                init_params = current_data[4]
            if group is None:
                group = current_data[5]
        if type_str is None:
            type_str = 'str'
        if control is None:
            control = 'TextField'
        if init_params is None:
            init_params = self.standard_init_params(control, value)
        if group is None:
            group = 'other'
        async with self.db.execute("INSERT OR REPLACE INTO settings (key, value, type, control, init_params, group_name) VALUES (?, ?, ?, ?, ?, ?)", (key, value, type_str.lower(), control, init_params, group)):
            await self.db.commit()

    async def get(self, key: str, need_all: bool = False):
        if need_all:
            sql = 'SELECT * FROM settings WHERE key = ?'
        else:
            sql = 'SELECT value, type FROM settings WHERE key = ?'
        async with self.db.execute(sql, (key,)) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            return row

    async def get_by_group(self, group: str):
        async with self.db.execute('SELECT * FROM settings WHERE group_name = ?', (group,)) as cursor:
            rows = await cursor.fetchall()
            return rows

    async def get_control_data(self, key: str):
        async with self.db.execute('SELECT * FROM settings WHERE key = ?', (key,)) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            key, value, type_str, control, init_params, group_name = row
            init_params = orjson.loads(init_params)
            if 'value' in init_params:
                init_params['value'] = convert(value, type_str)
            return {'control': control, 'init_params': init_params}

    async def delete(self, key: str):
        async with self.db.execute("DELETE FROM settings WHERE key = ?", (key,)):
            await self.db.commit()

    async def clear(self):
        async with self.db.execute("DELETE FROM settings"):
            await self.db.commit()

    async def get_all(self, order_by: str = None) -> dict[str, dict[str, str]]:
        sql = 'SELECT * FROM settings'
        if order_by is not None:
            sql += f' ORDER BY {order_by}'
        async with self.db.execute(sql) as cursor:
            rows = await cursor.fetchall()
            return {row[0]: dict(zip(['key', 'value', 'type', 'control', 'init_params', 'group_name'], row)) for row in rows} 