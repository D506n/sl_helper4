from ...shared.settings.models import PluginSettingsModel
from pydantic import BaseModel, Field

class NewPluginParams(BaseModel):
    plugin_class_name:str = Field('ExamplePlugin')
    sidebar_icon:str = Field('star')
    sidebar_label:str = Field('Example Plugin')

class Settings(PluginSettingsModel):
    pass