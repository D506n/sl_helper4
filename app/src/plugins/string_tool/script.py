import re
from typing import Callable
from functools import partial

def compile_deleter(substring:str, mode:int, notify_callback:Callable[[str], None]):
    if mode == 'Строго':
        return partial(re.compile(re.escape(substring)).sub, '')
    try:
        return partial(re.compile(substring).sub, '')
    except:
        notify_callback(f'Не удалось скомпилировать регулярное выражение: {substring}')
        return re.compile(re.escape(substring))

def mult_str_to_list(text:str, splitter:str=None, del_empty:bool=False):
    if splitter == None:
        splitter = ['\n']
    else:
        splitter:list = list(set(splitter))
        splitter = list(map(re.escape, splitter))
        splitter.append('\n')
    pattern = r'|'.join(splitter)
    result = re.split(pattern, text)
    result = list(map(lambda x: x.strip(), result))
    if del_empty:
        while '' in result:
            result.remove('')
    return result

def delete_dubl(inp:list):
    result:list[str] = []
    for item in inp:
        if item not in result:
            result.append(item)
    return result

def add_quots(inp:str):
    return f"'{inp}'"

def count_result(text:str, joiner:str):
    if joiner == '':
        joiner = ', '
    elif joiner.lower() in ['none', 'null']:
        joiner = None
    return len(text.split(joiner))

def int_convert(some_str:str):
    try:
        result = int(some_str)
    except:
        result = None
    return result

def del_digits_func(text:str):
    return ''.join(filter(lambda x: not x.isdigit(), text))

def only_digits_func(text:str):
    return ''.join(filter(lambda x: x.isdigit(), text))

def main(text:str, 
         del_dubl:bool, 
         need_quot:bool, 
         order:str, 
         del_empty:bool, 
         joiner:str=', ', 
         _type:str='строки', 
         splitter:str=None,
         del_digits:bool=False,
         only_digits:bool=False,
         delete_substring:str='',
         del_substr_mode:str='Строго',
         notify_callback:Callable[[str], None]=None):
    result = mult_str_to_list(text, splitter, del_empty)
    if notify_callback is None:
        notify_callback = lambda x: None
    if delete_substring != '':
        deleter = compile_deleter(delete_substring, del_substr_mode, notify_callback)
        result = list(map(deleter, result))
    if del_digits:
        result = list(map(del_digits_func, result))
    elif only_digits:
        result = list(map(only_digits_func, result))
    if del_dubl:
        result = delete_dubl(result)
    if need_quot:
        result = list(map(add_quots, result))
    if _type.lower() == 'числа':
        try:
            result = list(map(int, result))
        except:
            notify_callback('Не удалось преобразовать строки в числа')
            result = []
    match order:
        case 'По возрастанию':
            result.sort()
        case 'По убыванию':
            result.sort(reverse=True)
        case _:
            pass
    if _type.lower() == 'числа':
        result = list(map(str, result))
    if del_empty:
        result = [x for x in result if len(x) > 0]
    if joiner == '':
        joiner = ', '
    elif joiner.lower() in ['none', 'null']:
        joiner = ''
    try:
        joiner = joiner.encode().decode('unicode-escape')
    except:
        notify_callback('Не удалось корректно обработать соединитель. Использовано значение по умолчанию.')
        joiner = ', '
    res_count = len(result)
    notify_callback(f'Обработано строк: {res_count}')
    result = joiner.join(result)
    return result