from pydantic import BaseModel, Field
from typing import List
from xxhash import xxh3_64_hexdigest
import orjson
from datetime import datetime

class CommonMenuItem(BaseModel):
    title: str = Field('Название пункта меню')
    show: bool = Field(True, description='Show')

class ListMenuItem(BaseModel):
    title: str = Field('Название пункта меню')
    items: List[CommonMenuItem] = Field(default_factory=list, description='Items')
    show: bool = Field(True, description='Show')

class ThemeSettings(CommonMenuItem):
    title: str = Field('Настройки интерфейса')
    dark_mode: bool|None = Field(None, description='Тема приложения', options_aliases = {'Светлая': False, 'Тёмная': True, 'Системная': None})
    seed_color: str = Field('rgba(173, 216, 230, 1)', description='Seed color', options_aliases = {'Синий': 'rgba(173, 216, 230, 1)', 'Зеленый': 'rgba(144, 238, 144, 1)', 'Красный': 'rgba(255, 182, 193, 1)', 'Оранжевый': 'rgba(255, 218, 185, 1)', 'Желтый': 'rgba(255, 255, 224, 1)', 'Фиолетовый': 'rgba(230, 230, 250, 1)', 'Серый': 'rgba(211, 211, 211, 1)'})

    def seed(self, opacity: float=1) -> str:
        if opacity == 1:
            return self.seed_color
        if opacity > 1:
            raise ValueError('Opacity must be between 0 and 1')
        return self.seed_color.replace('1)', f'{opacity})')

class NotificationSettings(CommonMenuItem):
    title: str = Field('Настройки уведомлений')
    min_duration: int = Field(5, description='Minimum duration of the notification in seconds')
    max_duration: int = Field(-1, description='Maximum duration of the notification in seconds')

class PluginItemSettings(CommonMenuItem):
    title: str = Field('Название плагина')

    @property
    def ui_builder(self):pass

class PluginsSettings(ListMenuItem):
    title: str = Field('Настройки плагинов')
    items: List[PluginItemSettings] = Field(default_factory=list, description='Items')

class Settings(BaseModel):
    theme: ThemeSettings = Field(default_factory=ThemeSettings, description='Theme')
    notifications: NotificationSettings = Field(default_factory=NotificationSettings, description='Notifications')
    plugins: PluginsSettings = Field(default_factory=PluginsSettings, description='Plugins')
    last_updated: datetime = Field(default_factory=datetime.now, description='Last updated')

    def hash(self) -> str:
        return xxh3_64_hexdigest(orjson.dumps(self.model_dump(mode='json'), option=orjson.OPT_SORT_KEYS|orjson.OPT_INDENT_2))