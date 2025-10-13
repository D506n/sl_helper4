from .fast_table import FastTable
from pathlib import Path
from ._types import modes
from typing import Callable

MessageCallback = Callable[[str], None]
ProgressCallback = Callable[[int|float], None]

class FastConverter():
    '''Быстрый конвертер. Потребляет много памяти, но выполняет конвертацию быстрее.'''
    @staticmethod
    def start(source:str|Path, dest:Path, from_type:modes, to_type:modes, callback:BSignal = None, *args):
        '''Запускает процесс конвертации.\n
        Аргументы:
            `source` - путь к исходному файлу или строка с содержимым файла\n
            `dest` - путь к файлу, куда будет сохраняться результат если равно `None`, то результат будет возвращен в виде строки\n
            `from_type` - тип исходного файла\n
            `to_type` - тип результирующего файла\n
            `callback` - сигнал, который будет вызываться при каждом изменении состояния конвертации\n
        '''
        table = FastTable.read(source, from_type, *args)
        return table.save(dest, to_type, callback, *args)

class OptimizedConverter(FastConverter):
    '''Оптимизированный конвертер. Потребляет минимальное количество памяти, но выполняет конвертацию медленнее.'''
    def start(self, source:str|Path, dest:Path, from_type:modes, to_type:modes, callback:BSignal = None, *args):
        '''Запускает процесс конвертации.\n
        Аргументы:
            `source` - путь к исходному файлу или строка с содержимым файла\n
            `dest` - путь к файлу, куда будет сохраняться результат если равно `None`, то результат будет возвращен в виде строки\n
            `from_type` - тип исходного файла\n
            `to_type` - тип результирующего файла\n
            `callback` - сигнал, который будет вызываться при каждом изменении состояния конвертации\n
        '''
