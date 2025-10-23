from .settings_item import SettingsItem
from nicegui import ui
from nicegui.events import ValueChangeEventArguments
from ...shared.settings import SettingsProvider
from ...events.main import PubSub
from functools import partial

class CommonSettings(SettingsItem):
    def __init__(self, pubsub:PubSub, *args, **kwargs):
        super().__init__(pubsub, *args, **kwargs)
        self.settings = SettingsProvider.get()

    def dd_from_text_to_val(self, v):
        match v:
            case 'Светлая':
                return False
            case 'Темная':
                return True
            case 'Системная':
                return None

    def dd_from_val_to_text(self, v):
        match v:
            case False:
                return 'Светлая'
            case True:
                return 'Темная'
            case None:
                return 'Системная'

    def dd_change(self, ui:ui.dropdown_button, e:str):
        self.settings.ui.dark_mode = self.dd_from_text_to_val(e)
        ui.set_text(e)

    def build(self):
        with self:
            ui.label('Общие настройки').classes('text-h5')
            ui.splitter(horizontal=True)
            ui.label('Тема').classes('text-h6')
            ui.input('Основной цвет', value=self.settings.ui.seed_color, on_change=self.dd_change)
            with ui.row():
                ui.label('Режим темы')
                with ui.dropdown_button(self.dd_from_val_to_text(self.settings.ui.dark_mode)) as dropdown:
                    ui.item('Светлая', on_click=partial(self.dd_change, dropdown, 'Светлая'))
                    ui.item('Темная', on_click=partial(self.dd_change, dropdown, 'Темная'))
                    ui.item('Системная', on_click=partial(self.dd_change, dropdown, 'Системная'))
            ui.label('Уведомления').classes('text-h6')
            ui.input('Минимальная длительность уведомления', 
                     value=self.settings.notifications.min_duration, 
                     on_change=lambda e: setattr(self.settings.notifications, 'min_duration', e.value))
            ui.input('Максимальная длительность уведомления', 
                     value=self.settings.notifications.max_duration, 
                     on_change=lambda e: setattr(self.settings.notifications, 'max_duration', e.value))
        return self