from pathlib import Path
from .models import SettingsModel
import time
from threading import Thread

class SettingsProvider:
    __instance:'SettingsProvider' = None
    def __init__(self, settings_path: Path, plugins_dir: Path):
        self.path = settings_path
        self.plugins_dir = plugins_dir
        self.data: SettingsModel = self.load()
        self.th = Thread(target=self.settings_observer, name='settings_observer', daemon=True)
        self.th.start()
        self.__class__.__instance = self

    def load(self):
        result = SettingsModel.load_from_file(self.path)
        result.load_plugins(self.plugins_dir)
        return result

    @classmethod
    def get(cls) -> SettingsModel:
        return cls.__instance.data

    def fields_compare(self, old_data: SettingsModel, new_data: SettingsModel):
        return old_data.model_dump_json() == new_data.model_dump_json()

    def settings_observer(self):
        last_data = self.data.model_copy(deep=True)
        while True:
            time.sleep(1)
            if self.fields_compare(last_data, self.data):
                continue
            last_data = self.data.model_copy(deep=True)
            with open(self.path, 'w') as f:
                f.write(self.data.model_dump_json())