from ...shared.settings import SettingsProvider
from nicegui import ui
from logging import getLogger
from ..components.common_settings import CommonSettings
from ..components.settings_item import SettingsItem
from ...events.main import PubSub

logger = getLogger(__name__)

VISUALISATION_LABELS:dict[str, ui.label] = {}

def settings_page(pubsub: PubSub):
    @ui.page('/settings')
    async def settings_page():
        settings = SettingsProvider.get()
        with ui.row().classes('items-baseline w-full'):
            with ui.column().classes('w-full items-center'):
                CommonSettings(pubsub).build().classes('items-stretch w-full')
                with ui.card().classes('w-full') as plugins_header:
                    ui.label('Настройки плагинов').classes('text-h5')
                rendered_plugins = 0
                for plugin in settings.plugins.values():
                    pui = plugin.build_ui()
                    if not pui.is_deleted:
                        pui.classes('items-stretch w-full')
                        rendered_plugins += 1
                if rendered_plugins == 0:
                    plugins_header.delete()
    return settings_page