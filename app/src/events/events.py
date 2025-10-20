from dataclasses import dataclass
from typing import Any

@dataclass
class Event:
    msg: Any
    topic: str|None
    ctx: dict[str, Any]|None = None

    @classmethod
    def new(cls, msg: Any, topic: str|None = None, **ctx):
        return cls(msg, topic, ctx)