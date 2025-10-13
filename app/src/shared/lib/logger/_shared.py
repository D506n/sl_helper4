import logging
from functools import lru_cache
from pydantic import BaseModel
import re

class Static:
    color_reg = re.compile(r'\x1b\[\d{2}m')
    root: logging.Logger = None
    formatter: logging.Formatter = None

    @lru_cache()
    @staticmethod
    def compile_pattern(pattern:str):
        return re.compile(pattern)

    @lru_cache()
    @staticmethod
    def clear_text(text:str, pattern:re.Pattern|str):
        if isinstance(pattern, str):
            pattern = Static.compile_pattern(pattern)
        return pattern.sub('', text)