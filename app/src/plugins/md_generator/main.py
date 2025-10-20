from nicegui import ui
from nicegui import events
from ...events import PubSub, Event, RunDelayer
from ...shared._settings.domain import SettingsProvider
from .models import MDGenParams
from functools import partial
from typing import Any
from .script import main
import pyperclip

URL = '/md_generator'

def build_change_handler(params: MDGenParams, pubsub: PubSub, *args, **kwargs):
    async def change_handler(field:str, e:events.ValueChangeEventArguments|Any):
        if isinstance(e, events.ValueChangeEventArguments):
            e = e.value
        setattr(params, field, e)
        if field in ['del_substring', 'splitter', 'joiner', 'text']:
            pubsub.publish('string_tool_params_changed_delayed', 'event', {'params': params})
        else:
            pubsub.publish('string_tool_params_changed', 'event', {'params': params})
    return change_handler

def build_run_string_tool(pubsub: PubSub):
    async def run_string_tool(e: Event):
        params: MDGenParams = e.ctx['payload']['params']
        result = main(**params.model_dump(by_alias=True), notify_callback=partial(pubsub.publish, 'notify', payload={'timeout': 5000}))
        pubsub.publish('string_tool_result', 'event', {'result': result})
    return run_string_tool

async def set_result(e: Event, result_field: ui.textarea):
    result_field.value = e.ctx['payload']['result']

async def copy_result(e: Event, result_field: ui.textarea, pubsub: PubSub):
    if result_field.value:
        pyperclip.copy(result_field.value)
        pubsub.publish('notify', 'Результат скопирован в буфер обмена', {'timeout': 500, 'close_button': None})
    else:
        pubsub.publish('notify', 'Нечего копировать', {'timeout': 500, 'close_button': None})

def build_page(settings: SettingsProvider, pubsub: PubSub):
    params = MDGenParams(text='')
    change_handler = build_change_handler(params, pubsub)
    run_string_tool = build_run_string_tool(pubsub)
    delayer = RunDelayer(run_string_tool, delay=0.5)

    @ui.page(URL)
    async def plugin_page():
        with ui.column().classes('w-full h-full items-center rounded-lg').style('background-color: rgba(100, 100, 100, 0.1); padding: 10px;'):
            pass
            # with ui.row():
            #     ui.checkbox('Удалить дубли', on_change=partial(change_handler, 'del_dubl'))
            #     ui.checkbox('Добавлять кавычки', on_change=partial(change_handler, 'need_quot'))
            #     ui.checkbox('Удалить пустые строки', on_change=partial(change_handler, 'del_empty'))
            #     with ui.dropdown_button('Сортировка', value='Без сортировки', auto_close=True):
            #         ui.item('Без сортировки', on_click=partial(change_handler, 'order', 'Без сортировки'))
            #         ui.item('По возрастанию', on_click=partial(change_handler, 'order', 'По возрастанию'))
            #         ui.item('По убыванию', on_click=partial(change_handler, 'order', 'По убыванию'))
            #     with ui.dropdown_button('как'):#, on_value_change=partial(change_handler, 'type')):
            #         ui.item('Строки', on_click=partial(change_handler, 'type', 'Строки'))
            #         ui.item('Числа', on_click=partial(change_handler, 'type', 'Числа'))
            # with ui.row():
            #     ui.checkbox('Оставить только числа', on_change=partial(change_handler, 'only_digits'))
            #     ui.checkbox('Удалить все числа', on_change=partial(change_handler, 'del_digits'))
            # with ui.row().classes('w-full no-wrap').style('align-items: baseline;'):
            #     ui.input('Вырезать подстроку', on_change=partial(change_handler, 'delete_substring')).classes('w-full')
            #     with ui.dropdown_button('Режим'):#, on_value_change=partial(change_handler, 'del_substr_mode')):
            #         ui.item('Точное соответствие', on_click=partial(change_handler, 'del_substr_mode', 'Строго'))
            #         ui.item('Регулярное выражение', on_click=partial(change_handler, 'del_substr_mode', 'Регулярка'))
            # with ui.row().classes('w-full no-wrap'):
            #     ui.input('Разделитель, по умолчанию - перенос строки', on_change=partial(change_handler, 'splitter')).classes('w-full')
            #     ui.input('Соединитель, по умолчанию - запятая', on_change=partial(change_handler, 'joiner')).classes('w-full')
            # with ui.row().classes('w-full no-wrap h-full'):
            #     ui.textarea(label='Необработанный текст', on_change=partial(change_handler, 'text')).classes('w-full h-full').props('autogrow')
            #     result_field = ui.textarea(label='Результат').classes('w-full h-full').props('autogrow')
            #     result_field.on('click', partial(copy_result, result_field=result_field, pubsub=pubsub))
            # pubsub.subscribe('string_tool_params_changed_delayed', delayer.got_event)
            # pubsub.subscribe('string_tool_params_changed', run_string_tool)
            # pubsub.subscribe('string_tool_result', partial(set_result, result_field=result_field))
    return (URL, plugin_page,)

def _sb():
    with ui.item(on_click=lambda e: ui.navigate.to(URL)) as i:
        with ui.item_section().props('avatar'):
            ui.icon('difference')
        with ui.item_section():
            ui.item_label('Шаблонизатор')
        return i

def build_sidebar_btn():
    return lambda: _sb()