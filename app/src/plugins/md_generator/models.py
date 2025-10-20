from ...shared._settings.model import PluginItemSettings
from pydantic import BaseModel, Field, field_serializer
from pathlib import Path

class MDGenParams(BaseModel):
    path: Path = Field(None)
    # del_dubl: bool = Field(False, description='Удалить дубли')
    # need_quot: bool = Field(False, description='Добавить кавычки')
    # del_empty: bool = Field(False, description='Удалить пустые строки')
    # joiner: str = Field(', ', description='Соединитель')
    # splitter: str = Field('\n', description='Разделитель')
    # order: str = Field('Без сортировки', description='Сортировка', enum=['По возрастанию', 'По убыванию', 'Без сортировки'])
    # type: str = Field('строки', description='Тип сортировки', enum=['строки', 'числа'], alias='_type')
    # del_digits: bool = Field(False, description='Удалить числа')
    # only_digits: bool = Field(False, description='Оставить только числа')
    # delete_substring: str = Field('', description='Удалить подстроку')
    # del_substr_mode: str = Field('Строго', description='Режим', enum=['Строго', 'Рег. выражение'])

class Settings(PluginItemSettings):
    title: str = Field('Bunker Finder')
    show: bool = Field(True, description='Show')

    cache_ttl: int = Field(7, description='Cache TTL')
    base_url: str = Field("http://bunker-api-dot.yandex.net", description='Base URL')
    url_ver: str = Field("/v2", description='URL Version')
    node_method: str = Field("get_node", description='Node')
    node_list: str = Field("get_node_list", description='Node List API method')
    node_tree: str = Field("get_node_tree", description='Node Tree API method')
    project: str = Field("/dwh", description='Project')
    path: str = "/prod/reputter"