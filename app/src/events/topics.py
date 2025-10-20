from dataclasses import dataclass
from typing import Callable, Coroutine
import asyncio
from .events import Event

class Topic:
    def __init__(self, name: str, subscribers: list[Coroutine]):
        self.name = name
        self.subscribers = subscribers

    @classmethod
    def new(cls, name: str):
        return cls(name, [])

    def subscribe(self, subscriber: Coroutine):
        if asyncio.iscoroutinefunction(subscriber):
            self.subscribers.append(subscriber)
        else:
            raise TypeError('Subscriber must be a coroutine')

    def unsubscribe(self, subscriber: Coroutine):
        try:
            self.subscribers.remove(subscriber)
        except ValueError:
            raise ValueError('Subscriber not found')

    async def publish(self, event: Event):
        await asyncio.gather(*[subscriber(event) for subscriber in self.subscribers])