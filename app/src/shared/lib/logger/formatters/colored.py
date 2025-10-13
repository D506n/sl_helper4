import logging
from functools import lru_cache
from colorama import Fore
import sys
from pydantic import BaseModel, Field
from typing import Literal, TypeAlias

Colors: TypeAlias = Literal['black', 
                            'red', 
                            'green', 
                            'yellow', 
                            'blue', 
                            'magenta', 
                            'cyan', 
                            'white', 
                            'reset', 
                            'lightblack_ex', 
                            'lightred_ex', 
                            'lightgreen_ex', 
                            'lightyellow_ex', 
                            'lightblue_ex', 
                            'lightmagenta_ex', 
                            'lightcyan_ex', 
                            'lightwhite_ex']

class FieldSettings(BaseModel):
    width: int = Field(gt=3)
    align: Literal['left', 'center', 'right'] = Field(default='left')
    color: Colors|dict[str, Colors]|None = Field(default=None)
    clipping: Literal['start', 'end'] = Field(default='start')

DEFAULT_FIELD_SETTINGS = {
    'levelname': FieldSettings.model_validate({
        'width': 10, 
        'align': 'center', 
        'color': {
            'INFO': 'green', 
            'WARNING': 'yellow', 
            'ERROR': 'red', 
            'CRITICAL': 'red', 
            'DEBUG': 'white'}}),
    'name': FieldSettings.model_validate({'width': 20, 'align': 'center', 'color': 'blue', 'clipping': 'end'}),
    'asctime': FieldSettings.model_validate({'width': 19, 'align': 'center', 'color': 'yellow'}),
    "message": FieldSettings.model_validate({'width': 80, 'align': 'left', 'color': 'blue'})}

class ColoredFormatter(logging.Formatter):
    def __init__(self, 
                 fmt=None, 
                 datefmt=None, 
                 field_settings:dict[str, FieldSettings|dict]=None, 
                 force_color=False,
                 save_original=False):
        self.force_color = force_color
        fmt = fmt or '[%(levelname)s|%(name)s:%(lineno)-4s|%(asctime)s] %(message)s'
        datefmt = datefmt or '%Y-%m-%d %H:%M:%S'
        super().__init__(fmt, datefmt)
        if field_settings is None:
            self.field_settings = DEFAULT_FIELD_SETTINGS
        else:
            self.field_settings = {field:FieldSettings.model_validate(settings) for field, settings in field_settings.items()}
        self.save_original = save_original

    @lru_cache()
    def line_color(self, text:str, color:str):
        return f"{Fore.__getattribute__(color.upper())}{text}{Fore.RESET}"

    @lru_cache()
    def color_define(self, text:str, field:str):
        conditions:dict = self.field_settings[field].color
        return conditions.get(text, 'white')

    @lru_cache()
    def line_slice(self, text:str, width:int, clipping:str='start'):
        if len(text) <= width:
            return text
        if clipping == 'start':
            return text[:width-3]+'...'
        elif clipping == 'end':
            return '...'+text[-width+3:]
        logging.getLogger(__name__).warning(f"Clipping {clipping} is not supported")
        return text

    @lru_cache()
    def line_align(self, text:str, width:int, adj:str):
        match adj:
            case 'left':
                return f'{text:<{width}}'
            case 'right':
                return f'{text:>{width}}'
            case 'center':
                return f'{text:^{width}}'
            case _:
                logging.getLogger(__name__).warning(f"Alignment {adj} is not supported")
                return text
        return text

    @lru_cache()
    def custom_text_format(self, text:str, width:int, align:str, color:str|None, clipping:str='start'):
        text = self.line_slice(text, width, clipping)
        text = self.line_align(text, width, align)
        if color and (sys.stdout.isatty() or self.force_color):
            text = self.line_color(text, color)
        return text

    def copy_record(self, record:logging.LogRecord):
        new_record = logging.LogRecord(record.name, 
                                       record.levelno, 
                                       record.pathname, 
                                       record.lineno, 
                                       record.msg, record.args, 
                                       record.exc_info, 
                                       record.funcName, 
                                       record.stack_info)
        for field, value in record.__dict__.items():
            new_record.__dict__[field] = value
        return new_record

    def format_fields(self, record:logging.LogRecord):
        new_record = self.copy_record(record)
        new_record.message = new_record.getMessage()
        for field, settings in self.field_settings.items():
            if field in new_record.__dict__ and field:
                text = new_record.__dict__[field]
                width = settings.width
                align = settings.align
                clipping = settings.clipping
                color = settings.color
                if isinstance(color, dict):
                    color = self.color_define(text, field)
                text = self.custom_text_format(text, width, align, color, clipping)
                new_record.__dict__[field] = text
        return new_record    

    def format(self, record):
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        new_record = self.format_fields(record)
        formated = self.formatMessage(new_record)
        return formated