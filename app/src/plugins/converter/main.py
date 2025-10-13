from nicegui import ui
from .models import ConverterParams
from functools import partial
from ...ui.components.filepicker import FilepickField
from pathlib import Path
from logging import getLogger
from ...shared.plug_lib import PluginUI
from nicegui import Event
from ...ui.components.dropdown import DropDownBtn
from ...ui.components.progress import LinearProgress
from .params_validator import validate_params, Errors
from .src.script import main
import os
import asyncio
import platform

logger = getLogger(__name__)

class EventsStorage:
    def __init__(self):
        self.done = Event()
        self.res_btn_show = Event[bool]()
        self.param_changed = Event[str, str]()
        self.file_event = Event[str, str]()
        self.fmt_change = Event[str, str]()

class ConverterUI(PluginUI):
    def __init__(self, url, notify):
        super().__init__(url, notify)
        self.events = EventsStorage()
        self.params = ConverterParams()
        self.source_file_filed:FilepickField = None
        self.target_file_filed:FilepickField = None
        self.open_result_btn:ui.button = None
        self.progress_bar:LinearProgress = None

        self.events.file_event.subscribe(self.pick_file)
        self.events.param_changed.subscribe(self.param_changed_handler)
        self.events.fmt_change.subscribe(self.change_fmt)
        self.events.res_btn_show.subscribe(self.result_dir_toggle)
        self.events.done.subscribe(self.done_handler)

    def done_handler(self):
        if self.target_file_filed.value:
            self.events.res_btn_show.emit(True)
        self.progress_bar.clear()
        self.progress_bar.set_visibility(False)
        self.notify.emit({'message': 'Конвертация завершена.'})

    def param_changed_handler(self, key, value):
        setattr(self.params, key, value)
        self.events.res_btn_show.emit(False)

    def pick_file(self, field:str, value:str):
        setattr(self.params, field, value)
        if field == 'source_path':
            self.params.target_path = Path(self.params.source_path).with_suffix(f'.{self.params.target_type}')
            self.target_file_filed.set_value(self.params.target_path, skip=True)
        self.events.res_btn_show.emit(False)

    def change_fmt(self, field:str, value:str):
        setattr(self.params, field, value)
        try:
            self.params.source_path = self.params.source_path.with_suffix(f'.{self.params.source_type}')
            self.params.target_path = self.params.source_path.with_suffix(f'.{self.params.target_type}')
        except Exception as e:
            pass
        self.source_file_filed.formats = [self.params.source_type]
        self.target_file_filed.formats = [self.params.target_type]
        self.source_file_filed.set_value(self.params.source_path, skip=True)
        self.target_file_filed.set_value(self.params.target_path, skip=True)
        self.events.res_btn_show.emit(False)

    async def run(self, *args, **kwargs):
        try:
            validate_params(self.params)
        except Errors.ValidationError as e:
            return await self.handle_validate_errors(e)
        self.progress_bar.clear()
        self.progress_bar.set_visibility(True)
        try:
            await asyncio.to_thread(main, 
                                    self.params, 
                                    lambda e: self.notify.emit({'message': e}), 
                                    self.events.done.emit, 
                                    self.progress_bar.change_event.emit)
        except Exception as e:
            self.notify.emit({'message': str(e)})
            self.progress_bar.clear()
            self.progress_bar.set_visibility(False)

    async def handle_validate_errors(self, e: Errors.ValidationError):
        self.notify.emit({'message': e.msg})

    def open_result_dir(self):
        if self.params.target_path.exists():
            os.system(f'explorer /select,"{self.params.target_path}"')
        else:
            self.notify.emit({'message': f'Файл не найден: {self.params.target_path}'})

    def result_dir_toggle(self, show:bool):
        if platform.system() == 'Windows':
            self.open_result_btn.set_visibility(show)

    def layout(self):
        with ui.row().classes('w-full').style('align-items: baseline;'):
            ui.space()
            ui.label('Тип конвертации')
            with ui.label('?'):
                ui.tooltip('Оптимизированный режим потребляет меньше памяти, но занимает больше времени.\n\nВ быстром режиме потребление памяти будет пропорционально размеру файла(Примерно в 2 раза больше размера файла), т.к. файл целиком загружается в память.')
            ui.space()
        with ui.row(wrap=False).classes('w-full justify-center'):
            DropDownBtn('type', 'Быстрый', 'Оптимизированный', value=self.params.type, callback=self.events.param_changed)
        with ui.row(wrap=False).classes('w-full'):
            with ui.column().style('align-items: center;').classes('w-1/2'):
                with ui.row():
                    ui.label('Источник')
                with ui.row():
                    DropDownBtn('source_type', 'json', 'xlsx', 'csv', value=self.params.source_type, callback=self.events.fmt_change)
                with ui.row().classes('w-full no-wrap items-baseline'):
                    self.source_file_filed = FilepickField('Путь к файлу', 'source_path', value=self.params.source_path, callback=self.events.file_event)
                    self.source_file_filed.formats = [self.params.source_type]
                ui.textarea('Текст для конвертации', 
                            on_change=lambda e: partial(self.events.param_changed.emit, 'source_text')(e.value)
                            ).classes('w-full').props('autogrow')
            with ui.column().style('align-items: center;').classes('w-1/2'):
                with ui.row():
                    ui.label('Результат')
                with ui.row():
                    DropDownBtn('target_type', 'json', 'xlsx', 'csv', value=self.params.target_type, callback=self.events.fmt_change)
                with ui.row().classes('w-full no-wrap items-baseline'):
                    self.target_file_filed = FilepickField('Путь к файлу', 'target_path', value=self.params.target_path, callback=self.events.file_event)
                    self.target_file_filed.formats = [self.params.target_type]
                ui.textarea('Результат конвертации будет тут', 
                            on_change=lambda e: partial(self.events.param_changed.emit, 'target_text')(e.value)
                            ).classes('w-full').props('autogrow')
        with ui.row().classes('w-full justify-center'):
            ui.button('Конвертировать', on_click=self.run)
            self.open_result_btn = ui.button('Показать в проводнике', on_click=self.open_result_dir)
            self.open_result_btn.set_visibility(False)
        with ui.row().classes('w-full justify-center'):
            self.progress_bar = LinearProgress(size='25px')
            self.progress_bar.set_visibility(False)


# def build_run_converter_handler(params: ConverterParams, pubsub: PubSub, *args, **kwargs):
#     async def run_converter(progress, *args, **kwargs):
#         try:
#             validate_params(params)
#         except Exception as e:
#             return await handle_validate_errors(e, pubsub)
#         msg_cb = partial(pubsub.publish, 'notify')
#         done_cb = partial(pubsub.publish, 'converter_done', 'event')
#         try:
#             await asyncio.to_thread(main, params, msg_cb, done_cb, progress)
#         except Exception as e:
#             logger.error('Error occured in convertation process: %s', e)
#         print('done')
#     return run_converter

# def build_converter_done_handler(params: ConverterParams, pubsub: PubSub, *args, **kwargs):
#     async def converter_done(*args, **kwargs):
#         params.done = True
#         if platform.system() == 'Windows':
#             pubsub.publish('converter_params_changed', 'event', {'changes': [{'field': 'open_result_btn', 'value': True}]})
#         pubsub.publish('Конвертер завершил работу.')
#     return converter_done

# async def pick_file(e: events.ClickEventArguments, params: ConverterParams, field: str, pubsub: PubSub):
#     event = {'changes': []}
#     if field == 'source_path':
#         fmt = params.source_type
#     else:
#         fmt = params.target_type
#     fmt = f'.{fmt}'
#     path = Path.cwd()/'data/shared'
#     if not path.exists():
#         path.mkdir(parents=True, exist_ok=True) 
#     if platform.system() == 'Windows':
#         upper_limit = None
#     else:
#         upper_limit = path
#     result = await LocalFilePicker(path, upper_limit=upper_limit, allowed_fmts=[fmt])
#     result = Path(result[0])
#     setattr(params, field, result)
#     if field == 'target_path':
#         result = params.target_path_view
#     event['changes'].append({'field': field, 'value': result})
#     if field == 'source_path':
#         event['changes'][0] = {'field': field, 'value': params.source_path_view}
#         params.target_path = Path(params.source_path).with_suffix(f'.{params.target_type}')
#         event['changes'].append({'field': 'target_path', 'value': params.target_path_view})
#         event['changes'].append({'field': 'open_result_btn', 'value': False})
#     pubsub.publish('converter_params_changed', 'event', event)

# def build_change_handler(params: ConverterParams, pubsub: PubSub, *args, **kwargs):
#     async def change_handler(field:str, e:events.ValueChangeEventArguments|Any):
#         event = {'changes': [{'field': field, 'value': e}, {'field': 'open_result_btn', 'value': False}]}
#         if isinstance(e, events.ValueChangeEventArguments):
#             e = e.value
#         if e == getattr(params, field):
#             return
#         if field in ['source_path', 'target_path']:
#             if e == getattr(params, f'{field}_view'):
#                 return
#             e = Path(e)
#         setattr(params, field, e)
#         if field == 'source_type' and params.source_path:
#             params.source_path = params.source_path.with_suffix(f'.{params.source_type}')
#             params.target_path = params.source_path.with_suffix(f'.{params.target_type}')
#             event['changes'].append({'field': 'source_path', 'value': params.source_path_view})
#             event['changes'].append({'field': 'target_path', 'value': params.target_path_view})
#         if field == 'target_type' and params.target_path:
#             params.target_path = params.source_path.with_suffix(f'.{params.target_type}')
#             event['changes'].append({'field': 'target_path', 'value': params.target_path_view})
#         if field == 'source_path':
#             e = params.source_path_view
#             event['changes'].append({'field': 'source_path', 'value': e})
#         elif field == 'target_path':
#             e = params.target_path_view
#             event['changes'].append({'field': 'target_path', 'value': e})
#         pubsub.publish('converter_params_changed', 'event', event)
#     return change_handler

# async def converter_ui_refresh(e: Event, fields:dict[str, ui.dropdown_button|ui.input|ui.textarea|ui.button]):
#     changes = e.ctx['payload']['changes']
#     for change in changes:
#         field_name = change['field']
#         new_value = change['value']
#         field_ui = fields.get(field_name)
#         if not field_ui:
#             logger.error('Can\'t update field: %s. Field don\'t exist', field_name)
#         if isinstance(field_ui, ui.button) and field_ui.visible != new_value:
#             field_ui.set_visibility(new_value)
#         if field_name in ['source_path', 'target_path'] and new_value and new_value == field_ui.value:
#             continue
#         if not isinstance(new_value, (str, int, float, dict, list, bool,)) or new_value is not None:
#                 new_value = str(new_value)
#         if isinstance(field_ui, ui.dropdown_button):
#             field_ui.set_text(new_value)
#         elif not isinstance(field_ui, ui.button):
#             field_ui.set_value(new_value)
#         logger.debug('Set %s to %s', field_name, new_value)

# def build_page(pubsub: PubSub):
#     params = ConverterParams()
#     change_handler = build_change_handler(params, pubsub)
#     fields:dict[str, ui.dropdown_button|ui.input|ui.textarea] = {}
#     runner = build_run_converter_handler(params, pubsub)
#     done_handler = build_converter_done_handler(params, pubsub)
#     eta = ETATracker()
#     perc = set()

#     def open_result_dir():
#         if params.target_path.exists():
#             os.system(f'explorer /select,"{params.target_path}"')
#         else:
#             pubsub.publish(f'Файл не найден: {params.target_path}')

#     def dropdown_with_types(*types, source_target, change_handler=change_handler):
#         with ui.dropdown_button('json', value='json', auto_close=True) as field:
#             for t in types:
#                 ui.item(t, on_click=partial(change_handler, source_target, t))
#             return field

#     def pbar_sender(max, value):
#         percent = round(value / max, 2) * 100
#         if percent not in perc:
#             pubsub.publish('converter_pbar_update', 'event', {'max': max, 'value': value})
#             perc.add(percent)

#     async def pbar_handler(pbar: ui.linear_progress, e: Event):
#         return update_pbar(pbar, e.ctx['payload']['max'], e.ctx['payload']['value'])

#     def update_pbar(pbar: ui.linear_progress, max:int, value:int):
#         if not pbar.visible:
#             pbar.set_visibility(True)
#         v = round(value / max, 2)
#         if v == pbar.value:
#             return
#         pbar.set_value(v)

#     def pbar_text(num:float) -> str:
#         percent = int(round(num*100, 0))
#         eta.set_value(percent)
#         time = eta.get_eta_formatted()
#         if time is None:
#             return f'{percent}%'
#         return f'eta: {time} ({percent}%)'

#     async def pbar_clear(pbar: ui.linear_progress, e: Event):
#         eta.reset()
#         perc.clear()
#         pbar.set_value(0)
#         pbar.set_visibility(False)

#     @ui.page(URL)
#     async def plugin_page():
#         with ui.column().classes('w-full h-full items-center') rounded-lg').style('background-color: rgba(100, 100, 100, 0.1); padding: 10px;'):
#             with ui.row().classes('w-full').style('align-items: baseline;'):
#                 ui.space()
#                 ui.label('Тип конвертации')
#                 with ui.label('?'):
#                     ui.tooltip('Оптимизированный режим потребляет меньше памяти, но занимает больше времени.\n\nВ быстром режиме потребление памяти будет пропорционально размеру файла(Примерно в 2 раза больше размера файла), т.к. файл целиком загружается в память.')
#                 ui.space()
#             with ui.dropdown_button('Быстрый', value='Быстрый', auto_close=True) as field:
#                 ui.item('Быстрый', on_click=partial(change_handler, 'type', 'Быстрый'))
#                 ui.item('Оптимизированный', on_click=partial(change_handler, 'type', 'Оптимизированный'))
#                 fields['type'] = field
#             with ui.row(wrap=False).classes('w-full'):
#                 with ui.column().style('align-items: center;').classes('w-1/2'):
#                     with ui.row():
#                         ui.label('Источник')
#                     with ui.row():
#                         fields['source_type'] = dropdown_with_types('json', 'xlsx', 'csv', source_target='source_type')
#                     with ui.row().classes('w-full no-wrap items-baseline'):
#                         fields['source_path'] = ui.input('Путь к файлу', on_change=partial(change_handler, 'source_path')).classes('w-full items-baseline')
#                         ui.button('...', on_click=partial(pick_file, params=params, field='source_path', pubsub=pubsub))
#                     fields['source_text'] = ui.textarea('Текст для конвертации', on_change=partial(change_handler, 'source_text')).classes('w-full').props('autogrow')
#                 with ui.column().style('align-items: center;').classes('w-1/2'):
#                     with ui.row():
#                         ui.label('Результат')
#                     with ui.row():
#                         fields['target_type'] = dropdown_with_types('json', 'xlsx', 'csv', 'startrek', source_target='target_type')
#                     with ui.row().classes('w-full no-wrap items-baseline'):
#                         fields['target_path'] = ui.input('Путь к файлу', on_change=partial(change_handler, 'target_path')).classes('w-full items-baseline')
#                         ui.button('...', on_click=partial(pick_file, params=params, field='target_path', pubsub=pubsub))
#                     fields['target_text'] = ui.textarea('Результат конвертации будет тут', on_change=partial(change_handler, 'target_text')).classes('w-full').props('autogrow')
#             with ui.row().classes('w-full justify-center'):
#                 ui.button('Конвертировать', on_click=partial(runner, pbar_sender))
#                 fields['open_result_btn'] = ui.button('Показать в проводнике', on_click=open_result_dir)
#                 fields['open_result_btn'].set_visibility(False)
#             with ui.row().classes('w-full justify-center'):
#                 with ui.linear_progress(size='25px',show_value=False).on_value_change(lambda: p_badge.set_text(pbar_text(p_bar.value))) as p_bar:
#                         p_badge = ui.badge('0%', color='primary').classes('absolute-center')
#                 p_bar.set_visibility(False)
#             pb_clear = partial(pbar_clear, p_bar)
#             pubsub.subscribe('converter_params_changed', partial(converter_ui_refresh, fields=fields))
#             pubsub.subscribe('converter_done', done_handler)
#             pubsub.subscribe('converter_done', pb_clear)
#             pubsub.subscribe('converter_pbar_update', partial(pbar_handler, p_bar))
#     return (URL, plugin_page,)


# def _sb():
#     with ui.item(on_click=lambda e: ui.navigate.to(URL)) as i:
#         with ui.item_section().props('avatar'):
#             ui.icon('transgender')
#         with ui.item_section():
#             ui.item_label('Конвертер')
#         return i

# def build_sidebar_btn():
#     return lambda: _sb()

def load():
    return ConverterUI
