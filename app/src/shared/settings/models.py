from pydantic import BaseModel, Field
from nicegui import ui
from pathlib import Path
import orjson
from xxhash import xxh3_64_hexdigest
from importlib import import_module
from logging import getLogger
from typing import Self

logger = getLogger(__file__)

class PluginSettingsModel(BaseModel):
    id: str = Field()
    url: str = Field()
    icon: str = Field('star')
    label: str = Field('Plugin')

    @classmethod
    def from_file(cls, file_path: Path) -> Self:
        if not file_path.exists():
            raise FileNotFoundError('Settings file not found')
        data = orjson.loads(file_path.read_text('utf-8'))
        if 'id' not in data:
            id = xxh3_64_hexdigest(file_path.parent.name)
            data['id'] = id
        if 'url' not in data:
            url = f'/{file_path.parent.name}'
            data['url'] = url
        return cls.model_validate(data)

    def layout(self) -> ui.card:
        pass

    def build_ui(self) -> ui.card:
        with ui.card().classes('w-full') as card:
            ui.label(self.label).classes('text-h5')
            ui.splitter(horizontal=True)
            self.layout()
        if len(card.slots['default'].children) <= 2:
            card.delete()
        return card

    def save_to_file(self, file_path: Path):
        file_path.write_text(self.model_dump_json(indent=2), 'utf-8')

class PluginModule():
    class Settings(PluginSettingsModel):
        pass

class UISettingsModel(BaseModel):
    dark_mode: bool|None = Field(None)
    seed_color: str = Field('rgba(173, 216, 230, 1)')

class NotificationSettingsModel(BaseModel):
    min_duration: int = Field(5)
    max_duration: int = Field(-1)

class SettingsModel(BaseModel):
    ui: UISettingsModel = Field(default_factory=UISettingsModel)
    notifications: NotificationSettingsModel = Field(default_factory=NotificationSettingsModel)
    plugins: dict[str, PluginSettingsModel] = Field(default_factory=dict)

    @classmethod
    def load_from_file(cls, file_path: Path):
        if not file_path.exists():
            return cls()
        data = orjson.loads(file_path.read_text('utf-8'))
        return cls.model_validate(data)

    def load_plugins(self, plugins_dir: Path):
        loaded_plugins = set()
        for plugin in self.plugins:
            loaded_plugins.add(plugin.id)
        for plugin_path in plugins_dir.iterdir():
            if plugin_path.is_dir() and not plugin_path.name.startswith('_'):
                try:
                    module:PluginModule = import_module(f'src.plugins.{plugin_path.name}.models')
                    model = module.Settings.from_file(plugin_path / 'settings.json')
                    if model.id not in loaded_plugins:
                        self.plugins[plugin_path.name] = model
                        loaded_plugins.add(model.id)
                        logger.info(f'Loaded plugin settings: {plugin_path.name}')
                    else:
                        logger.info(f'Plugin {plugin_path.name} already loaded')
                except Exception as e:
                    logger.error(f'Failed to load plugin {plugin_path.name}. Error: {e}')