from .main import PluginUI
from nicegui import ui

class AbstractPlugin:
    URL:str

    class AbstractPluginUI(PluginUI):
        pass

    def load()-> AbstractPluginUI:
        return AbstractPlugin.AbstractPluginUI

    def sidebar_btn()-> ui.item:
        pass