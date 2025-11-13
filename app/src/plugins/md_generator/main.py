from ...shared.plug_lib import PluginUI
from ...shared.notificator import NotifyEvent
from nicegui import ui
from .models import Settings, TemplateModel, TemplatesListModel
from pathlib import Path

class MDServiceUI():
    def __init__(self, templates: TemplatesListModel, notify: NotifyEvent):
        self.templates = templates

    def layout(self):
        with ui.expansion('Cоздать новый шаблон'):
            with ui.column().classes('w-full items-stretch'):
                ui.input('Название шаблона')
                with ui.row(wrap=False).classes('w-full'):
                    with ui.textarea('Шаблон').classes('w-1/2').props('autogrow'):
                        ui.tooltip('Для создания переменной в шаблоне используйте фигурные скобки. Пример: {name}')
                    ui.markdown('##### Предпросмотр:\n\nтест').classes('w-1/2')
                ui.input('Описание')
                with ui.input('Разделитель'):
                    ui.tooltip('Разделитель используется для разделения строк в переменных шаблона. Пример: \\n')
                with ui.input('Соединитель'):
                    ui.tooltip('Соединитель используется для соединения строк при генерации ответа. Пример: \\n')
                ui.button('Создать')

class MDFormBuilder():
    def __init__(self, template: TemplateModel, notify: NotifyEvent):
        self.template = template
        self.notify = notify

    def layout(self):
        with ui.row().classes('w-full'):
            with ui.column().classes('w-full'):
                ui.label(self.template.name).classes('text-h5')
                for row in self.template.words:
                    if row.startswith('{') and row.endswith('}'):
                        name = row[1:-1]
                        ui.textarea(name).classes('w-full').props('autogrow')

class MdGeneratorUI(PluginUI):
    def __init__(self, url: str, notify: NotifyEvent):
        super().__init__(url, notify)
        self.splitter: ui.splitter = None
        self.tabs: ui.tabs = None
        self.tab_panels: ui.tab_panels = None
        self.settings = Settings.from_file(Path(__file__).parent/'settings.json')
        self.templates = TemplatesListModel.from_file(self.settings.templates_path)
        self.template_uis = [MDFormBuilder(template, self.notify)\
                          for template in self.templates.templates]
        self.tabs_list: list[ui.tab] = []
        self.tab_panels_list: list[ui.tab_panel] = []
        self.service_ui = MDServiceUI(self.templates, self.notify)

    def layout(self):
        with ui.splitter(value=None).classes('w-full h-full') as splitter:
            self.splitter = splitter
            with self.splitter.before:
                with ui.tabs().props('vertical').classes('w-full') as tabs:
                    self.tabs = tabs
                    service = ui.tab('Создание/Редактирование').classes('text-justify')
                    ui.splitter(horizontal=True)
                    for t in self.template_uis:
                        self.tabs_list.append(ui.tab(t.template.name))
            with splitter.after:
                if self.tabs_list:
                    first = self.tabs_list[0]
                else:
                    first = service
                with ui.tab_panels(tabs, value=first).props('vertical').classes('w-full h-full'):
                    with ui.tab_panel(service).classes('w-full h-full items-stretch'):
                        self.service_ui.layout()
                    for i, tab in enumerate(self.tabs_list):
                        with ui.tab_panel(tab).classes('w-full h-full items-stretch') as tab_panel:
                            self.tab_panels_list.append(tab_panel)
                            self.template_uis[i].layout()

def load():
    return MdGeneratorUI
