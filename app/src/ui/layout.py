from logging import getLogger
from nicegui import ui
from ..shared.settings import SettingsProvider
from .components import build_header, build_sidebar, build_workspace
from ..load_plugins import Loader
from ..shared.notificator import Notificator
from ..events import PubSub
from ..shared.plug_lib import sidebar_btn
from functools import partial

logger = getLogger(__name__)

def app_layout(loader: Loader) -> None:
    @ui.page('/')
    @ui.page('/{_:path}')
    async def main_layout():
        settings = SettingsProvider.get()
        dm = ui.dark_mode(settings.ui.dark_mode)
        notif = Notificator()
        btns = [partial(sidebar_btn, p.url, p.icon, p.label) for p in settings.plugins.values() if p.url in loader.plugins.keys()]
        pages = {}
        for k, v in loader.plugins.items():
            try:
                pages[k] = v(k, notif.event).build
            except Exception as e:
                logger.error(f'Error registering plugin ui builder {k}: {e}')
        build_header()
        build_sidebar(*btns)
        build_workspace(pages, notif.event)

    return main_layout