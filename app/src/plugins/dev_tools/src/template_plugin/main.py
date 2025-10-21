from ...shared.plug_lib import PluginUI
from ...shared.notificator import NotifyEvent
from nicegui import ui

class {plugin_class_name}(PluginUI):
    def __init__(self, url: str, notify: NotifyEvent):
        super().__init__(url, notify)

    def layout(self):
        ui.label('Hello, world!')

def load():
    return {plugin_class_name}