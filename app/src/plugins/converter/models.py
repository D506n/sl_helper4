from pydantic import BaseModel, Field, field_validator
from typing import Literal
from pathlib import Path
from ...shared.settings.models import PluginSettingsModel

FILE_TYPES = Literal['json', 'xlsx', 'csv', 'startrek']

class ConverterParams(BaseModel):
    type: Literal['Быстрый', 'Оптимизированный'] = Field('Быстрый', description='Тип конвертации')
    source_type: FILE_TYPES = Field('json', description='Тип файла источника')
    target_type: FILE_TYPES = Field('json', description='Тип файла цели')
    source_path: Path|None = Field(None, description='Путь к файлу источнику')
    target_path: Path|None = Field(None, description='Путь к файлу цели')
    source_text: str = Field('', description='Текст источника')
    target_text: str = Field('', description='Текст цели')
    splitter: str = Field(',', description='Разделитель (Только для CSV)')
    joiner: str = Field(',', description='Объединитель (Только для CSV)')
    done: bool = Field(False, description='Готово')

    @classmethod
    def path_view(cls, path:Path):
        if path is None:
            return
        if len(path.parts) > 4:
            return f"../{'/'.join(path.parts[-4:])}"
        return str(path)

    @field_validator('source_path', 'target_path')
    def validate_path(cls, v):
        if v is None:
            return v
        return Path(v)

class Settings(PluginSettingsModel):
    pass