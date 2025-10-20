from nicegui import ui
from typing import TypedDict
from ...shared.settings import SettingsProvider
from random import randint
from ...load_plugins import Loader
from ...events import PubSub
from logging import getLogger
from typing import Callable

logger = getLogger(__name__)

SIDEBAR_ITEM_STYLE = 'w-full rounded-lg'

def build_sidebar(*elements_factory: Callable[[], ui.element]):
    with ui.left_drawer(bordered=True):
        with ui.item(on_click=lambda e: ui.navigate.to('/')).classes(SIDEBAR_ITEM_STYLE):
            with ui.item_section().props('avatar'):
                ui.icon('home')
            with ui.item_section():
                ui.item_label('Главная')
        for element in elements_factory:
            element().classes(SIDEBAR_ITEM_STYLE)
        ui.space()
        with ui.item(on_click=lambda e: ui.navigate.to('/settings')).classes(SIDEBAR_ITEM_STYLE):
            with ui.item_section().props('avatar'):
                ui.icon('settings')
            with ui.item_section():
                ui.item_label('Настройки')