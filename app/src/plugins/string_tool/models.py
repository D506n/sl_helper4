from ...shared.settings import PluginSettingsModel
from pydantic import BaseModel, Field

class StringToolParams(BaseModel):
    text: str = Field(..., description='Текст для обработки')
    del_dubl: bool = Field(False, description='Удалить дубли')
    need_quot: bool = Field(False, description='Добавить кавычки')
    del_empty: bool = Field(False, description='Удалить пустые строки')
    joiner: str = Field(', ', description='Соединитель')
    splitter: str = Field('\n', description='Разделитель')
    order: str = Field('Без сортировки', description='Сортировка', enum=['По возрастанию', 'По убыванию', 'Без сортировки'])
    type: str = Field('строки', description='Тип сортировки', enum=['строки', 'числа'], alias='_type')
    del_digits: bool = Field(False, description='Удалить числа')
    only_digits: bool = Field(False, description='Оставить только числа')
    delete_substring: str = Field('', description='Удалить подстроку')
    del_substr_mode: str = Field('Строго', description='Режим', enum=['Строго', 'Рег. выражение'])

class Settings(PluginSettingsModel):
    pass
    # title: str = Field('String Tool')
    # show: bool = Field(False, description='Show')
