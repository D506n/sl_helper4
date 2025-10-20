from nicegui import ui, Event
from ...utils.eta import ETATracker

class LinearProgress(ui.linear_progress):
    def __init__(self, value = 0, max_value = 100, *, size = None, color = 'primary', badge_classes = 'absolute-center'):
        self.real_value = value
        self.max_value = max_value
        value = round(self.real_value / max_value, 0)
        super().__init__(value, size=size, show_value=False, color=color)
        self.change_event = Event[int, int]()
        with self:
            self.badge = ui.badge('0%').classes(badge_classes)
        self.change_event.subscribe(self.change_handler)
        self.eta = ETATracker()

    def clear(self):
        self.eta.reset()
        self.set_value(0)
        self.badge.set_text('0%')

    def set_max_value(self, value:int):
        self.max_value = value

    def change_handler(self, max_value:int, value:int):
        if max_value != self.max_value:
            self.max_value = max_value
        if not self.visible:
            self.set_visibility(True)
        self.real_value = value
        value = round(self.real_value / self.max_value, 2)
        if value != self.value:
            self.set_value(value)
            value = int(round(value * 100, 0))
            self.eta.set_value(value)
            text = self.eta.get_eta_formatted()
            if not text:
                text = 'n/a'
            self.badge.set_text(f'eta: {text}({value}%)')