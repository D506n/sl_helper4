from functools import lru_cache

@lru_cache(maxsize=100)
def hex_to_rgba(hex_color: str, alpha: float=1) -> str:
    """Преобразует hex-цвет в rgba строку с заданной прозрачностью"""
    if alpha < 0 or alpha > 1:
        raise ValueError("Прозрачность должна быть в диапазоне от 0 до 1")
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    if len(hex_color) != 6:
        raise ValueError("Неверный формат hex-цвета")
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    except ValueError:
        raise ValueError("Неверные символы в hex-цвете")
    return f'rgba({r}, {g}, {b}, {alpha})'