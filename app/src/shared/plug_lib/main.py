from nicegui import ui
from functools import wraps
from ..notificator import NotifyEvent

def crosstab(cls):
    cache: dict[str, PluginUI] = {}
    @wraps(cls)
    def wrap(*args, **kwargs):
        if cls in cache.keys():
            return cache[cls]
        cache[cls] = cls(*args, **kwargs)
        return cache[cls]
    return wrap

class PluginUI():
    def __init__(self, url:str, notify: NotifyEvent, classes:str='w-full'):
        self.url = url
        self.notify = notify
        self.build_now = False
        self.classes = classes

    def layout(self):
        ui.label('example')

    def build(self, align_items=None):
        self.build_now = True
        with ui.card(align_items=align_items).classes(self.classes):
            return self.layout()
        self.build_now = False

def sidebar_btn(url:str, icon:str, label:str):
    with ui.item(on_click=lambda e: ui.navigate.to(url)) as i:
        with ui.item_section().props('avatar'):
            ui.icon(icon)
        with ui.item_section():
            ui.item_label(label)
        return i