from pathlib import Path
from importlib import import_module
from logging import getLogger
from .shared.settings import SettingsProvider
from .utils.singleton import singleton
from .shared.plug_lib import AbstractPlugin, PluginUI

logger = getLogger(__name__)

class AbstractLibrary(AbstractPlugin):
    IS_LIB = True

@singleton
class Loader():
    def __init__(self):
        self.settings = SettingsProvider.get()
        self.plugins: dict[str, PluginUI] = {}
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
        module: AbstractPlugin|AbstractLibrary = import_module(f"src.plugins.{plugin_path.name}.main")
        if hasattr(module, "IS_LIB") and module.IS_LIB:
            logger.info("Registering library %s", plugin_path.name)
            self.libs[plugin_path.name] = module
            self.plugins_cache.add(plugin_path.name)
        elif hasattr(module, "load"):
            logger.info("Registering plugin %s", plugin_path.name)
            self.plugins[f'/{plugin_path.name}'] = module.load()
            self.plugins_cache.add(plugin_path.name)
        else:
            logger.error("Plugin %s has no IS_LIB arg or load method", plugin_path.name)