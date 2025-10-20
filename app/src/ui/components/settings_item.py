from nicegui import ui
from ...shared.settings import SettingsProvider
from ...events.main import PubSub

class SettingsItem(ui.card):
    def __init__(self, pubsub:PubSub, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = SettingsProvider.get()
        self.pubsub = pubsub

    def build(self):
        return self