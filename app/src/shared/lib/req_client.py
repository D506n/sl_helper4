from httpx import AsyncClient
from orjson import dumps

class HTTPClient():
    __client = None
    @classmethod
    def run(cls, base_url: str):
        cls.__client = AsyncClient(base_url=base_url)

    @classmethod
    def get_client(cls) -> AsyncClient:
        return cls.__client

    @classmethod
    async def send_request(cls, method: str, url: str, **kwargs):
        return await cls.get_client().request(method, url, **kwargs)

    @classmethod
    async def send_notification(cls, title: str=None, subtitle: str=None, level: str='info', duration: int=-1):
        return await cls.send_request(
            'POST', 
            '/core/notify', 
            data=dumps({
                'title': title, 
                'subtitle': subtitle, 
                'level': level, 
                'duration': duration
            })
        )