from ...shared.settings import SettingsProvider
# from ...shared._settings.model import CommonMenuItem, PluginsSettings, PluginItemSettings, ListMenuItem
from nicegui import ui
from types import UnionType
from pydantic.fields import FieldInfo
from logging import getLogger
import functools
from ..components.common_settings import CommonSettings
from ..components.settings_item import SettingsItem
from ...events.main import PubSub

logger = getLogger(__name__)

VISUALISATION_LABELS:dict[str, ui.label] = {}

# def change_settings(value, field_path:str, settings: SettingsProvider):
#     with settings.edit() as s:
#         field_path_parts = field_path.split('.')
#         target_obj = s
#         for field_name in field_path_parts[:-1]:
#             target_obj = getattr(target_obj, field_name)
#         setattr(target_obj, field_path_parts[-1], value)
#     VISUALISATION_LABELS[field_path].set_text(f'Текущее значение: {value}')
#     logger.info('Changed settings %s to %s', field_path, value)

# def _make_dropdown(title: str, options: dict, field_path: str, settings: SettingsProvider, current_value):
#     with ui.row().classes('items-baseline'):
#         ui.space()
#         with ui.dropdown_button(title):
#             for k, v in options.items():
#                 ui.item(k, on_click=functools.partial(change_settings, v, field_path, settings))
#         ui.space()
#     with ui.row().classes('items-baseline'):
#         ui.space()
#         VISUALISATION_LABELS[field_path] = ui.label(f'Текущее значение: {current_value}')
#         ui.space()

# def _make_simple_field(field_path: str, settings: SettingsProvider, current_value, field_info: FieldInfo):
#     if field_info.annotation == str:
#         inp = ui.input
#     elif field_info.annotation == bool:
#         inp = ui.checkbox
#     elif field_info.annotation in {int, float}:
#         inp = ui.number
#     else:
#         raise ValueError(f'Unknown field type {field_info.annotation}')
#     inp(value=current_value, on_change=functools.partial(change_settings, field_path, settings))

# def _find_field_title(field_info: FieldInfo, field_name: str):
#     if not field_info.description:
#         field_title = field_name
#     else:
#         field_title = field_info.description
#     return field_title

# def _union_type_build(
#         field_info: FieldInfo, 
#         item: CommonMenuItem, 
#         field_name: str, 
#         settings: SettingsProvider, 
#         item_key: str, 
#         field_title: str):
#     if hasattr(field_info, 'json_schema_extra') and 'options_aliases' in field_info.json_schema_extra:
#         alias_dict = field_info.json_schema_extra['options_aliases']
#     else:
#         raise ValueError('Union type field must have options_aliases')
#     current_value = getattr(item, field_name)
#     for k, v in alias_dict.items():
#         if current_value == v:
#             current_value = k
#             break
#     field_path = f'{item_key}.{field_name}'
#     _make_dropdown(field_title, alias_dict, field_path, settings, current_value)

# def _make_simple_type_field(
#         field_info: FieldInfo, 
#         item: CommonMenuItem, 
#         field_name: str, 
#         settings: SettingsProvider, 
#         item_key: str, 
#         field_title: str):
#     current_value = getattr(item, field_name)
#     field_path = f'{item_key}.{field_name}'
#     with ui.row().classes('items-baseline'):
#         ui.space()
#         ui.label(field_title)
#         _make_simple_field(field_path, settings, current_value, field_info)
#         ui.space()

# def common_item_build(item_key, item: CommonMenuItem, settings: SettingsProvider):
#     fields = item.__class__.model_fields
#     title = item.title
#     if not item.show:
#         return
#     with ui.row().classes('w-full items-baseline'):
#         ui.space()
#         with ui.column().classes('w-full items-center').style(f'background-color: {settings.read().theme.seed(0.3)}'):
#             ui.label(title).classes('text-h5')
#             for field_name, field_info in fields.items():
#                 if field_name in {'title', 'show'}:
#                     continue
#                 anno = field_info.annotation
#                 field_title = _find_field_title(field_info, field_name)
#                 if isinstance(anno, UnionType):
#                     _union_type_build(field_info, item, field_name, settings, item_key, field_title)
#                 else:
#                     _make_simple_type_field(field_info, item, field_name, settings, item_key, field_title)
#         ui.space()

# def list_menu_item_build(item_key: str, item: ListMenuItem, settings: SettingsProvider):
#     logger.warning('List menu item is not implemented yet')

# def plugins_build(item_key: str, item: PluginsSettings, settings: PluginsSettings):
#     logger.warning('Plugins settings is not implemented yet')
#     for key, value in item.items:
#         print(key, value)

# def plugin_item_build(item_key: str, item: PluginItemSettings, settings: PluginItemSettings):
#     logger.warning('Plugin item settings is not implemented yet')

def settings_page(settings: SettingsProvider, pubsub: PubSub, *plugins: type[SettingsItem]):
    @ui.page('/settings')
    async def settings_page():
        with ui.row().classes('items-baseline w-full'):
            with ui.column().classes('w-full items-center'):
                CommonSettings(pubsub).build().classes('items-stretch w-full')
                for plugin in plugins:
                    plugin(settings, pubsub).build().classes('items-stretch w-full')
    return settings_page