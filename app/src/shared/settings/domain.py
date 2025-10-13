from .model import Settings, PluginItemSettings
from pathlib import Path
from aiofiles import open
from contextlib import contextmanager
import asyncio, atexit
from logging import getLogger
from datetime import datetime
from typing import Callable, List, Awaitable
import importlib
from ...utils.singleton import singleton
from nicegui import ui

logger = getLogger('SettingsProvider')

class AbstractPlugin:
    class Settings(PluginItemSettings):pass

@singleton
class SettingsProvider:
    def __init__(self, path: Path=None):
        self.path = path or Path(__file__).parent / 'settings.json'
        self._settings:Settings = self._sync_load()
        self.writer:asyncio.Task = None
        self.io_queue = asyncio.Queue()
        self.bg_task:asyncio.Task = None
        self.page_elements: dict[str, ui.element] = {}
        self._sync_save_callbacks: List[Callable] = []
        self._async_save_callbacks: List[Awaitable] = []
        atexit.register(self.cleanup)

    def add_save_callback(self, callback: Callable|Awaitable):
        """Добавить коллбэк, который будет вызван после сохранения настроек"""
        if asyncio.iscoroutinefunction(callback):
            self._async_save_callbacks.append(callback)
        elif callable(callback):
            self._sync_save_callbacks.append(callback)
        else:
            raise TypeError('Callback must be callable or awaitable')

    async def _writer_task(self):
        logger.debug('Writer task started')
        while True:
            try:
                settings:Settings = await self.io_queue.get()
                await asyncio.sleep(0.1)
                while not self.io_queue.empty():
                    try:
                        settings = self.io_queue.get_nowait()
                    except asyncio.QueueEmpty:
                        logger.error('try get from empty queue') # маловероятно, но вдруг
                async with open(self.path, 'w', encoding='utf-8') as f:
                    await f.write(settings.model_dump_json())
                logger.debug('Settings saved to file')
                for callback in self._sync_save_callbacks:
                    try:
                        callback()
                    except Exception as e:
                        logger.error('Error in save callback: %s', e)
                await asyncio.gather(*[cb() for cb in self._async_save_callbacks])
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error('Error in writer task: %s', e)

    def _sync_load(self) -> Settings:
        if not self.path.exists():
            result = Settings()
            self.path.write_text(result.model_dump_json(), encoding='utf-8')
            logger.debug('Created new settings file')
            return result
        logger.debug('Loaded settings from file')
        try:
            result = Settings.model_validate_json(self.path.read_text(encoding='utf-8'))
        except UnicodeDecodeError:
            logger.error('Error decoding settings file')
            result = Settings()
            self.path.write_text(result.model_dump_json())
            logger.debug('Created new settings file')
        return result

    def save(self):
        self.io_queue.put_nowait(self._settings.model_copy())
        if not self.writer:
            self.writer = asyncio.create_task(self._writer_task())
        logger.debug('Saved settings to file enqueued')

    def read(self) -> Settings:
        return self._settings.model_copy()

    @contextmanager
    def edit(self):
        settings_hash = self._settings.hash()
        stable_settings = self._settings.model_copy()
        try:
            yield self._settings
        except Exception as e:
            self._settings = stable_settings
            raise e
        else:
            if self._settings.hash() != settings_hash:
                self._settings.last_updated = datetime.now()
                self.save()

    async def __cleanup(self):
        self.path.write_text(self._settings.model_dump_json(), encoding='utf-8')
        if self.writer:
            self.writer.cancel()
            try:
                await asyncio.wait_for(self.writer, timeout=5)
            except asyncio.TimeoutError:
                pass

    def cleanup(self):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.__cleanup())
            else:
                asyncio.run(self.__cleanup())
        except RuntimeError:
            asyncio.run(self.__cleanup())
        except Exception:
            pass

    def register_plugin(self, name: str):
        module: AbstractPlugin = importlib.import_module(f'src.plugins.{name}.models')
        if hasattr(module, 'Settings'):
            self._settings.plugins.items.append(module.Settings())
            logger.debug('Registered plugin settings for %s', name)
        else:
            logger.debug('Plugin %s has no settings', name)