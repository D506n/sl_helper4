from ...shared.plug_lib import PluginUI
from nicegui import ui, Event
from functools import partial
from ...shared.notificator import NotifyEvent
from .models import NewPluginParams
import asyncio
from pathlib import Path
from ...utils.data_finder import find_data_path

class EventsStore():
    def __init__(self):
        self.params_changed = Event[str]()
        self.result = Event[str]()

class NewPluginTabUI(ui.tab_panel):
    def __init__(self, name: str):
        super().__init__(name)
        self.params = NewPluginParams()
        with self:
            with ui.row().classes("w-full justify-center"):
                ui.input('Имя класса плагина', value=self.params.plugin_class_name, on_change=lambda e: print(e)).classes('w-2/3')
            with ui.row().classes('w-full justify-center'):
                ui.input('Иконка в боковой панели', value=self.params.sidebar_icon, on_change=print).classes('w-2/3')
            with ui.row().classes('w-full justify-center'):
                ui.input('Название в боковой панели', value=self.params.sidebar_label, on_change=print).classes('w-2/3')
            with ui.row().classes('w-full justify-center'):
                ui.button('Создать плагин', on_click=self.create_plugin)

    async def create_plugin(self, *args, **kwargs):
        print(args, kwargs)

class CheckSumCalculatorTabUI(ui.tab_panel):
    def __init__(self, name: str):
        super().__init__(name)
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
            NewPluginTabUI(new_plugin_tab)
            CheckSumCalculatorTabUI(checksum_calculator_tab)

def load():
    return DeveloperToolsUI