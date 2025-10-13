import platform
from pathlib import Path
from typing import Optional
from functools import partial
from nicegui import events, ui
from nicegui import Event

DEFAULT_SHARED_DIR = Path(__file__).parent.parent.parent.parent/'data/shared'

class LocalFilePicker(ui.dialog):
    def __init__(self, directory: str, *,
                 upper_limit: Optional[str] = ..., multiple: bool = False, show_hidden_files: bool = False,
                 allowed_fmts: Optional[list[str]] = None) -> None:
        """Local File Picker

        This is a simple file picker that allows you to select a file from the local filesystem where NiceGUI is running.

        :param directory: The directory to start in.
        :param upper_limit: The directory to stop at (None: no limit, default: same as the starting directory).
        :param multiple: Whether to allow multiple files to be selected.
        :param show_hidden_files: Whether to show hidden files.
        """
        super().__init__()

        self.path = Path(directory).expanduser()
        if upper_limit is None:
            self.upper_limit = None
        else:
            self.upper_limit = Path(directory if upper_limit == ... else upper_limit).expanduser()
        self.show_hidden_files = show_hidden_files

        self.allowed_fmts = allowed_fmts
        self.navbar = None

        with self, ui.card():
            self.navbar_update()
            with ui.row():
                self.sidebar_build()
                self.grid = ui.aggrid({
                    'columnDefs': [{'field': 'name', 'headerName': 'File'}],
                    'rowSelection': 'multiple' if multiple else 'single',
                }, html_columns=[0]).classes('w-96').on('cellDoubleClicked', self.handle_double_click)
                with ui.row().classes('w-full justify-end').style('align-items: baseline;'):
                    if self.allowed_fmts:
                        ui.label(f'Поддерживаемые форматы: {", ".join(self.allowed_fmts)}')
                    ui.button('Cancel', on_click=self.close).props('outline')
                    ui.button('Ok', on_click=self._handle_ok)
        self.update_grid()

    def navbar_update(self):
        if platform.system() == 'Windows':
            if self.navbar is None:
                with ui.scroll_area().classes('w-full h-20'):
                    self.navbar = ui.row(wrap=False).classes('w-full').style('align-items: baseline;')
            self.navbar.clear()
            with self.navbar:
                for i, p in enumerate(self.path.parts):
                    ui.item(p).on_click(partial(self.navbar_click_handler, p, i))

    def navbar_click_handler(self, part: str, index: int, *args, **kwargs) -> None:
        new_path = Path(*[p for p in self.path.parts[:index + 1]])
        self.path = new_path
        self.update_grid()

    def sidebar_build(self):
        if platform.system() == 'Windows':
            grid = ui.aggrid({'columnDefs': [{'field': 'path', 'headerName': 'Быстрые ссылки'}], 'rowSelection': 'single'}, html_columns=[0]).classes('w-32').on('cellClicked', lambda e: self.sidebar_click_handler(e))
            grid.options['rowData'] = [
                {
                    'path': str(p),
                }
                for p in ['Рабочий стол', 'Загрузки', 'Документы']
            ]
            self.sidebar = grid
        else:
            self.sidebar = None

    def sidebar_click_handler(self, e: events.GenericEventArguments) -> None:
        variant = e.args.get('value')
        match variant:
            case 'Рабочий стол':
                self.path = Path.home() / 'Desktop'
            case 'Загрузки':
                self.path = Path.home() / 'Downloads'
            case 'Документы':
                self.path = Path.home() / 'Documents'
            case _:
                self.path = Path.home() / 'Desktop'
        self.sidebar.update()
        self.update_grid()

    def update_grid(self) -> None:
        paths = list(self.path.glob('*'))
        if not self.show_hidden_files:
            paths = [p for p in paths if not p.name.startswith('.')]
        if self.allowed_fmts:
            paths = [p for p in paths if p.suffix in self.allowed_fmts or p.is_dir()]
        paths.sort(key=lambda p: p.name.lower())
        paths.sort(key=lambda p: not p.is_dir())
        self.navbar_update()
        self.grid.options['rowData'] = [
            {
                'name': f'📁 <strong>{p.name}</strong>' if p.is_dir() else f'📄{p.name}',
                'path': str(p),
            }
            for p in paths
        ]
        if (self.upper_limit is None and self.path != self.path.parent) or \
                (self.upper_limit is not None and self.path != self.upper_limit):
            self.grid.options['rowData'].insert(0, {
                'name': '📁 <strong>..</strong>',
                'path': str(self.path.parent),
            })
        self.grid.update()

    async def handle_double_click(self, *args, **kwargs) -> None:
        self.path = Path((await self.grid.get_selected_row())['path'])
        if self.path.is_dir():
            self.update_grid()
        else:
            self.submit([str(self.path)])

    async def _handle_ok(self):
        rows = await self.grid.get_selected_rows()
        self.submit([r['path'] for r in rows])

class FilepickField(ui.row):
    def __init__(self, 
                 label:str, 
                 key:str, 
                 value:Path=None,
                 callback:Event[str, str]=None, 
                 len:int=4):
        super().__init__(wrap=False, align_items=None)
        self.classes('w-full no-wrap items-baseline')
        self.key = key
        self.value = value
        self.callback = callback
        self.len = len
        self._fmts = None
        self._upper_limit = None
        self.virtual_change = False
        with self:
            self.inp = ui.input(label, value=self.path_cutter(self.value), on_change=self.change_event_handler).classes('w-full')
            self.inp.on('click', self.click_inp_handler)
            self.btn = ui.button('...', on_click=self.file_pick)

    def set_value(self, value:Path, skip:bool=False):
        if skip:
            self.virtual_change = True
        self.value = value
        self.inp.set_value(self.path_cutter(self.value))

    def click_inp_handler(self, *args, **kwargs):
        if self.value:
            self.inp.set_value(str(self.value))
        self.virtual_change = False

    @property
    def upper_limit(self):
        if self._upper_limit:
            return self._upper_limit
        if platform.system() == 'Windows':
            return None
        return DEFAULT_SHARED_DIR

    @upper_limit.setter
    def upper_limit(self, value):
        self._upper_limit = value

    @property
    def formats(self):
        if self._fmts:
            return self._fmts
        return None

    @formats.setter
    def formats(self, fmts:list[str]):
        if not fmts:
            self._fmts = None
            return
        self._fmts = []
        for fmt in fmts:
            if fmt in self._fmts:
                continue
            if not fmt.startswith('.'):
                fmt = f'.{fmt}'
            self._fmts.append(fmt)

    async def file_pick(self, *args, **kwargs):
        self.virtual_change = True
        if self.value:
            path = self.value.parent
        else:
            path = DEFAULT_SHARED_DIR
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        result = await LocalFilePicker(path, upper_limit=self.upper_limit, allowed_fmts=self.formats)
        if result:
            self.set_value(Path(result[0]))
            if self.callback:
                self.callback.emit(self.key, self.value)

    def change_event_handler(self, *args, **kwargs):
        if self.callback and not self.virtual_change:
            self.callback.emit(self.key, self.inp.value)

    @classmethod
    def path_cutter(self, path:Path|None, max_items:int=4):
        if path is None:
            return ''
        elif len(path.parts) > max_items:
            return f'.../{"/".join(path.parts[-max_items:])}'
        return str(path)
