import re

def replace_digits_with_x_regex(text):
    """
    Заменяет все цифры в тексте на символ 'X' используя регулярные выражения
    
    Args:
        text (str): Входной текст
        
    Returns:
        str: Текст с замененными цифрами
    """
    return re.sub(r'\d', 'X', text)