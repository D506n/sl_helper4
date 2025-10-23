from nicegui import ui
from ..pages import main_page, settings_page
from ...shared.settings import SettingsProvider
from ...events import PubSub
from ...shared.plug_lib import PluginUI

def build_workspace(pages: dict[str, PluginUI], pubsub: PubSub):
    settings = SettingsProvider.get()
    with ui.row().classes('w-full h-full'):
        ui.space()
        pages.update({'/': main_page, '/settings': settings_page(pubsub)})
        ui.sub_pages(pages).classes('w-2/3')
        ui.space()