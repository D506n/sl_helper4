from ...shared.plug_lib import PluginUI
from nicegui import ui
from functools import partial
from ...shared.notificator import NotifyEvent

class ExamplePlugin(PluginUI):
    def __init__(self, url:str, notify: NotifyEvent):
        super().__init__(url, notify)
        self.count = 0
        self.counter:ui.label = None

    def change_count(self, new_count):
        self.count += new_count
        self.counter.set_text(f'Count: {self.count}')

    def layout(self):
        inc = partial(self.change_count, 1)
        dec = partial(self.change_count, -1)
        ui.label('Example Plugin')
        self.counter = ui.label(f'Count: {self.count}')
        ui.button('Increment', on_click=lambda e: inc())
        ui.button('Decrement', on_click=lambda e: dec())

def load():
    return ExamplePlugin