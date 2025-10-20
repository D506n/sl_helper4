from .models import ConverterParams
from pathlib import Path

class Errors():
    class ValidationError(Exception):
        '''Базовый класс для ошибок валидации параметров.'''
        def __init__(self, *args):
            super().__init__(*args)
            self.msg = 'Ошибка валидации параметров.'

    class TypeSourceTarget(ValidationError):
        def __init__(self, *args):
            super().__init__(*args)
            self.msg = 'Формат источника и результата не могут совпадать.'

    class SourcePathNotExists(ValidationError):
        def init__(self, *args):
            super().__init__(*args)
            self.msg = 'Файл источник данных не существует.'

    class EmptySource(ValidationError):
        def __init__(self, *args):
            super().__init__(*args)
            self.msg = 'Отсутствует файл или строка источник данных.'

    class OptSourcePath(ValidationError):
        def __init__(self, *args):
            super().__init__(*args)
            self.msg = 'Для оптимизированного режима необходим файл источник данных.'

    class NotImplemented(ValidationError):
        def __init__(self, *args):
            super().__init__(*args)
            self.msg = 'Работа конвертера с выбранными параметрами на данный момент невозможна.'

def validate_params(params: ConverterParams):
    if params.source_type == params.target_type:
        raise Errors.TypeSourceTarget()
    if params.source_path is None and not params.source_text:
        raise Errors.EmptySource()
    if params.source_type == 'startrek':
        raise NotImplementedError()
    if params.type == 'Оптимизированный' and params.source_type == 'startrek':
        raise NotImplementedError()
    if params.type == 'Оптимизированный' and params.target_type == 'startrek':
        raise NotImplementedError()
    if params.type == 'Оптимизированный' and not params.source_path:
        raise Errors.OptSourcePath()
    if params.source_path and not Path(params.source_path).exists():
        raise Errors.SourcePathNotExists()