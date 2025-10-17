from pathlib import Path
from importlib import import_module
from logging import getLogger, Logger
from .shared._settings import SettingsProvider
from .utils.singleton import singleton
from nicegui import ui
from .events import PubSub

logger = getLogger(__name__)

class AbstractPlugin:
    logger: Logger

    @staticmethod
    def build_page(settings: SettingsProvider, pubsub: PubSub) -> tuple[str, ui.page]:
        raise NotImplementedError()

    @staticmethod
    async def build_sidebar_btn(settings: SettingsProvider):
        raise NotImplementedError()

class AbstractLibrary:
    logger: Logger

    @staticmethod
    async def main(*args, **kwargs):
        raise NotImplementedError()

@singleton
class Loader():
    def __init__(self, settings: SettingsProvider=None):
        '''Синглтон. Параметр settings нужен только при инициализации класса, при последующих вызовах не требуется.'''
        self.settings = settings
        self.plugins: dict[str, AbstractPlugin] = {}
        self.libs: dict[str, AbstractLibrary] = {}
        self.plugins_cache: set[str] = set()

    def load_plugins(self):
        plugins_dir = Path(__file__).parent / "plugins"
        if not plugins_dir.exists():
            logger.error("Plugins directory not found")
            return
        count = 0
        for plugin in plugins_dir.iterdir():
            if plugin.is_dir() and not plugin.name.startswith("_"):
                try:
                    self.register_plugin(plugin)
                except Exception as e:
                    logger.error("Error loading plugin %s: %s", plugin.name, e)
                    continue
                count += 1
        logger.info("Loaded %s plugins", count)

    def register_plugin(self, plugin_path: Path):
        if plugin_path.name in self.plugins_cache:
            logger.debug("Plugin %s is already registered", plugin_path.name)
            return
        main_path = plugin_path / "main.py"
        if not main_path.exists():
            logger.error("Plugin %s has no main.py file", plugin_path.name)
            return
        logger.debug("Registering plugin %s", plugin_path)
        module: AbstractPlugin = import_module(f"src.plugins.{plugin_path.name}.main")
        if not hasattr(module, "build_page") and hasattr(module, "main"):
            logger.info("Registering library %s", plugin_path.name)
            self.libs[plugin_path.name] = module
            self.plugins_cache.add(plugin_path.name)
        elif hasattr(module, "build_page") and hasattr(module, "build_sidebar_btn"):
            logger.info("Registering plugin %s", plugin_path.name)
            self.plugins[plugin_path.name] = module
            self.plugins_cache.add(plugin_path.name)
        else:
            logger.error("Plugin %s has no build_page and build_sidebar_btn methods or main method", plugin_path.name)
            raise Exception(f"Plugin {plugin_path.name} has no build_page and build_sidebar_btn methods or main method")
        self.settings.register_plugin(plugin_path.name)