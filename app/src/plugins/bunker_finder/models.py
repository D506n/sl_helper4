from ...shared._settings.model import PluginItemSettings
from pydantic import BaseModel, Field, field_serializer
from pathlib import Path
from ...ui.components.settings_item import SettingsItem
from nicegui import ui

class FinderSettings(SettingsItem):
    def build(self):
        settings: Settings = [i for i in self.settings.read().plugins.items if i.title == 'Bunker Finder'][0]
        with self:
            ui.label('Настройки поиска по бункеру').classes('text-h6')
            ui.input('Время жизни кэша(дней)', value=settings.cache_ttl)
            ui.label('Чем меньше время жизни кэша, тем чаще плагин будет ходить на сервера бункера за актуальными данными по выгрузкам.')
            ui.input('Базовый URL*', value=settings.base_url)
            ui.input('Версия URL*', value=settings.url_ver)
            ui.input('Метод получения узла*', value=settings.node_method)
            ui.input('Метод получения списка узлов*', value=settings.node_list)
            ui.input('Метод получения дерева узлов*', value=settings.node_tree)
            ui.input('Проект*', value=settings.project)
            ui.input('Путь*', value=settings.path)
            ui.label('Звёздочкой отмечены поля, которые лучше не менять если не меняется API бункера, т.к. это может сломать плагин.')
        return super().build()

class FinderParams(BaseModel):
    path: Path = Field(None)

class Settings(PluginItemSettings):
    title: str = Field('Bunker Finder')
    show: bool = Field(True, description='Show')

    cache_ttl: int = Field(3, description='Cache TTL')
    base_url: str = Field("http://bunker-api-dot.yandex.net", description='Base URL')
    url_ver: str = Field("/v2", description='URL Version')
    node_method: str = Field("get_node", description='Node')
    node_list: str = Field("get_node_list", description='Node List API method')
    node_tree: str = Field("get_node_tree", description='Node Tree API method')
    project: str = Field("/dwh", description='Project')
    path: str = "/prod/reputter"

    @property
    def ui_builder(self):
        return FinderSettings