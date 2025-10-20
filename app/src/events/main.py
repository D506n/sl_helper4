import asyncio
from .topics import Topic
from .events import Event
from typing import Coroutine

from logging import getLogger

logger = getLogger(__name__)

class PubSub:
    def __init__(self):
        self.topics:dict[str, Topic] = {}
        self.event_queue = asyncio.Queue()
        self.bg_task:asyncio.Task = None

    def subscribe(self, topic:str, callback:Coroutine):
        if topic not in self.topics.keys():
            self.topics[topic] = Topic.new(topic)
        self.topics[topic].subscribe(callback)
        logger.debug('Subscribed to topic %s', topic)

    async def send_and_wait(self, topic:str, event:Event):
        if topic == '*':
            await asyncio.gather(*[topic.publish(event) for topic in self.topics.values()])
        elif topic in self.topics.keys():
            await self.topics[topic].publish(event)
        else:
            raise ValueError('Topic not found')
        logger.debug('Published event to topic %s', topic)

    async def pulish_worker(self):
        while True:
            try:
                topic, event = await self.event_queue.get()
                await self.send_and_wait(topic, event)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error('Error in publish worker: %s', e)

    def publish(self, topic:str, msg:str, payload:dict=None):
        if not payload:
            payload = {}
        e = Event.new(msg, topic=topic, payload=payload)
        self._publish(topic, e)

    def _publish(self, topic:str, event:Event):
        if self.bg_task is None:
            self.bg_task = asyncio.create_task(self.pulish_worker())
        self.event_queue.put_nowait((topic, event,))

    @classmethod
    def cleanup(cls):
        if cls.__instance is not None:
            cls.__instance.bg_task.cancel()