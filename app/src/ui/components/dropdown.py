from nicegui import ui, Event
from functools import partial

class DropDownBtn(ui.dropdown_button):
    def __init__(self, key, *items:str, callback:Event[str, str]=None, value = False, color = 'primary', icon = None, auto_close = True, split = False):
        if not value:
            value = items[0]
        text = str(value)
        super().__init__(text, value=value, color=color, icon=icon, auto_close=auto_close, split=split)
        self.key = key
        self.item_callback = callback
        with self:
            for item in items:
                ui.item(item, on_click=partial(self.item_click_handler, item))

    def item_click_handler(self, item:str, *args, **kwargs):
        self.set_text(item)
        if self.item_callback:
            self.item_callback.emit(self.key, item)