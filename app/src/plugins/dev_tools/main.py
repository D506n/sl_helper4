from ...shared.plug_lib import PluginUI
from nicegui import ui, Event
from functools import partial
from ...shared.notificator import NotifyEvent
from .models import NewPluginParams
import asyncio
from pathlib import Path
from ...utils.data_finder import find_data_path
import shutil
import orjson

class EventsStore():
    def __init__(self):
        self.params_changed = Event[str]()
        self.result = Event[str]()

class NewPluginTabUI(ui.tab_panel):
    def __init__(self, name: str, notify: NotifyEvent):
        super().__init__(name)
        self.params = NewPluginParams()
        self.notify = notify
        with self:
            with ui.row().classes("w-full justify-center"):
                ui.input('Имя плагина', value=self.params.plugin_name, on_change=lambda e: setattr(self.params, 'plugin_name', e.value)).classes('w-2/3')
            with ui.row().classes('w-full justify-center'):
                ui.input('Иконка в боковой панели', value=self.params.sidebar_icon, on_change=lambda e: setattr(self.params, 'sidebar_icon', e.value)).classes('w-2/3')
            with ui.row().classes('w-full justify-center'):
                ui.input('Название в боковой панели', value=self.params.sidebar_label, on_change=lambda e: setattr(self.params, 'sidebar_label', e.value)).classes('w-2/3')
            with ui.row().classes('w-full justify-center'):
                ui.button('Создать плагин', on_click=self.create_plugin)

    def get_class_name(self):
        return self.params.plugin_name.title().replace(' ', '')+'UI'

    def get_path(self):
        return Path(__file__).parent.parent/self.params.plugin_name.lower().replace(' ', '_')

    async def create_plugin(self, *args, **kwargs):
        tagret_path = self.get_path()
        if tagret_path.exists():
            self.notify.emit({'message': 'Плагин с таким названием уже существует', 'timeout': 5000, 'close_button': True})
            return
        shutil.copytree(Path(__file__).parent/'src/template_plugin', tagret_path)
        main_path = tagret_path/'main.py'
        with open(main_path, 'r', encoding='utf-8') as f:
            main_content = f.read()
        main_content = main_content.format(plugin_class_name=self.get_class_name())
        with open(main_path, 'w', encoding='utf-8') as f:
            f.write(main_content)
        settings_path = tagret_path/'settings.json'
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings_data = orjson.loads(f.read())
        settings_data['icon'] = self.params.sidebar_icon
        settings_data['label'] = self.params.sidebar_label
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(orjson.dumps(settings_data, option=orjson.OPT_INDENT_2).decode('utf-8'))
        self.notify.emit({'message': 'Плагин создан. Для отображения в меню, пожалуйста, перезагрузите программу.', 'timeout': 5000, 'close_button': True})

class CheckSumCalculatorTabUI(ui.tab_panel):
    def __init__(self, name: str, notify: NotifyEvent):
        super().__init__(name)
        self.notify = notify
        self.result_path = find_data_path(Path(__file__))
        with self:
            with ui.row().classes("w-full justify-center"):
                ui.input('Путь к файлу', value=str(self.result_path)).on('change', print).classes('w-2/3')
            with ui.row().classes('w-full justify-center'):
                ui.button('Записать суммы в файл', on_click=print)

class DeveloperToolsUI(PluginUI):
    def __init__(self, url: str, notify: NotifyEvent):
        super().__init__(url, notify)
        self.events = EventsStore()

    def layout(self):
        with ui.tabs().classes("w-full") as tabs:
            new_plugin_tab = ui.tab('Новый плагин')
            checksum_calculator_tab = ui.tab('Калькулятор контрольной суммы')
        with ui.tab_panels(tabs, value=new_plugin_tab).classes("w-full"):
            NewPluginTabUI(new_plugin_tab, self.notify)
            CheckSumCalculatorTabUI(checksum_calculator_tab, self.notify)

def load():
    return DeveloperToolsUI