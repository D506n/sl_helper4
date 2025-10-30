from ...shared.settings.models import PluginSettingsModel
from pydantic import BaseModel, Field
from typing import List, Self
from pathlib import Path
import orjson
from functools import cached_property

class Settings(PluginSettingsModel):
    exclude_symbols: List[str] = Field(default_factory=lambda: ['@', 'https://staff.yandex-team.ru/', '-'])
    templates_path: Path = Field(Path(__file__).parent.parent.parent.parent/'data/shared/md_generator_templates.json')

    @classmethod
    def get_exclude_symbols(cls):
        inst: Self = cls.from_file(Path(__file__).parent / 'settings.json')
        return inst.exclude_symbols

class TemplateModel(BaseModel):
    name: str = Field()
    template: str = Field()
    description: str = Field('')
    splitter: str = Field('\n,')
    joiner: str = Field('\n')
    exclude_symbols: List[str] = Field(default_factory=Settings.get_exclude_symbols)

    @cached_property
    def words(self):
        return self.template.split(' ')

class TemplatesListModel(BaseModel):
    templates: List[TemplateModel] = Field()

    @classmethod
    def from_file(cls, file_path: Path) -> Self:
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch(exist_ok=True)
            file_path.write_text(orjson.dumps({'templates': []}).decode(), 'utf-8')
            return cls.model_validate({'templates': []})
        data = orjson.loads(file_path.read_text('utf-8'))
        return cls.model_validate(data)