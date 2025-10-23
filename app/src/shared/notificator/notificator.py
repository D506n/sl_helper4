from nicegui import ui
from nicegui import Event
from logging import getLogger
from typing import TypedDict

class NotificatorsStorage:
    storage: dict[str, 'Notificator'] = {}

    @classmethod
    def add(cls, id:str, notificator: 'Notificator'):
        cls.storage[id] = notificator

    @classmethod
    def get(cls, id:str):
        return cls.storage.get(id)

logger = getLogger(__name__)

class NotifyEventArgsDict(TypedDict):
    message: str
    close_button: str
    position: str
    multi_line: bool
    progress: bool
    classes: str
    timeout: int

    @classmethod
    def default(cls):
        return cls(
            message = 'Hello world!',
            close_button = 'X',
            position = 'bottom-right',
            multi_line = True,
            progress = True,
            classes = 'multi-line-notification',
            timeout = None
        )

NotifyEvent = Event[NotifyEventArgsDict]

class Notificator:
    def __init__(self, id:str):
        ui.html('<style>.multi-line-notification { white-space: pre-line; }</style>', sanitize=False) # без этого многострочные уведомления не работают
        self.layout = ui.row() # костыль чтобы нотификатор привязывался к странице
        self.event = NotifyEvent()
        self.event.subscribe(self.sub)
        NotificatorsStorage.add(id, self)

    async def sub(self, e: NotifyEventArgsDict):
        event = NotifyEventArgsDict.default()
        event.update(e)
        with self.layout:
            ui.notify(**event)