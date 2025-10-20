from nicegui import ui
from nicegui import Event
from nicegui import events
from ...events import EventDelayer
from .models import StringToolParams
from functools import partial
from .script import main
from ...shared.plug_lib import PluginUI
from ...shared.notificator import NotifyEvent
from ...ui.components.dropdown import DropDownBtn

class EventsStore():
    def __init__(self):
        self.params_changed = Event[str]()
        self.result = Event[str]()
        self.dd_event = Event[str, str]()

class StringToolUI(PluginUI):
    def __init__(self, url: str, notify: NotifyEvent):
        super().__init__(url, notify)
        self.params = StringToolParams(text='')
        self.events = EventsStore()
        self.run_delayer = EventDelayer(self.events.params_changed)
        self.events.params_changed.subscribe(self.run)
        self.events.result.subscribe(lambda e: self.result_field.set_value(e))
        self.events.dd_event.subscribe(self.change_dd_handler)

    def change_dd_handler(self, key:str, val:str):
        setattr(self.params, key, val)
        self.events.params_changed.emit('event')

    def run_delayed(self, *args, **kwargs):
        self.run_delayer.got_event('event')

    def notify_callback(self, msg:str):
        self.notify.emit({'message': msg, 'timeout': 5000})

    def run(self, *args, **kwargs):
        result = main(**self.params.model_dump(by_alias=True), notify_callback=self.notify_callback)
        self.events.result.emit(result)

    def checkbox_click(self, field:str, e:events.ValueChangeEventArguments, *args, **kwargs):
        setattr(self.params, field, e.value)
        self.events.params_changed.emit(field)

    def input_change(self, field, e:events.ValueChangeEventArguments, *args, **kwargs):
        setattr(self.params, field, e.value)
        self.run_delayed(e.value)

    def copy_result(self):
        if self.result_field.value:
            ui.clipboard.write(self.result_field.value)
            self.notify.emit({'message': 'Результат скопирован в буфер обмена', 'timeout': 500, 'close_button': None})
        else:
            self.notify.emit({'message': 'Нечего копировать', 'timeout': 500, 'close_button': None})

    def layout(self):
        with ui.row():
            ui.checkbox('Удалить дубли', value=self.params.del_dubl, on_change=partial(self.checkbox_click, 'del_dubl'))
            ui.checkbox('Добавлять кавычки', value=self.params.need_quot, on_change=partial(self.checkbox_click, 'need_quot'))
            ui.checkbox('Удалить пустые строки', value=self.params.del_empty, on_change=partial(self.checkbox_click, 'del_empty'))
            DropDownBtn('order', 'Без сортировки', 'По возрастанию', 'По убыванию', value=self.params.order, callback=self.events.dd_event)
            DropDownBtn('type', 'Строки', 'Числа', value=self.params.type, callback=self.events.dd_event)
            with ui.row():
                ui.checkbox('Оставить только числа', value=self.params.only_digits, on_change=partial(self.checkbox_click, 'only_digits'))
                ui.checkbox('Удалить все числа', value=self.params.del_digits, on_change=partial(self.checkbox_click, 'del_digits'))
            with ui.row().classes('w-full no-wrap').style('align-items: baseline;'):
                ui.input('Вырезать подстроку', value=self.params.delete_substring, on_change=partial(self.input_change, 'delete_substring')).classes('w-full')
                DropDownBtn('del_substr_mode', 'Строго', 'Регулярка', value=self.params.del_substr_mode, callback=self.events.dd_event)
            with ui.row().classes('w-full no-wrap'):
                ui.input('Разделитель, по умолчанию - перенос строки', value=self.params.splitter, on_change=partial(self.input_change, 'splitter')).classes('w-full')
                ui.input('Соединитель, по умолчанию - запятая', value=self.params.joiner, on_change=partial(self.input_change, 'joiner')).classes('w-full')
            with ui.row().classes('w-full no-wrap h-full'):
                ui.textarea(label='Необработанный текст', value=self.params.text, on_change=partial(self.input_change, 'text')).classes('w-full h-full').props('autogrow')
                self.result_field = ui.textarea(label='Результат').classes('w-full h-full').props('autogrow')
                self.result_field.on('click', self.copy_result)

def load():
    return StringToolUI