from typing import TypeAlias, Literal, Callable

modes:TypeAlias = Literal['csv', 'xlsx', 'json', 'startrek']
table_row:TypeAlias = dict[str, str|int|float|bool|list|dict|None]
progress_callback:TypeAlias = Callable[[int|float], None]
raw_progress_callback:TypeAlias = Callable[[int|float, int|float], None]
message_callback:TypeAlias = Callable[[str], None]