from pathlib import Path
from functools import lru_cache

@lru_cache()
def find_data_path(start_path: Path):
    """
    Рекурсивно ищет папку 'data' в текущей директории и выше.
    
    Если папка 'data' не найдена в текущей директории, функция рекурсивно 
    поднимается вверх по дереву каталогов до тех пор, пока не найдет папку 'data' 
    или не достигнет корня проекта. Если папка 'data' не найдена, возвращается 
    путь к папке 'data' в текущей рабочей директории.

    Args:
        start_path (Path): Путь, с которого начинается поиск. Может быть путем 
                           к файлу или директории.

    Returns:
        Path: Путь к папке 'data'. Если папка не найдена, возвращается путь 
              к папке 'data' в текущей рабочей директории (Path.cwd() / 'data').
    """
    if start_path.is_file():
        start_path = start_path.parent
    if (start_path/'data').exists():
        return start_path/'data'
    if start_path == Path.cwd():
        return Path.cwd()/'data'
    return find_data_path(start_path.parent)