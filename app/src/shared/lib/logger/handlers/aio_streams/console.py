from aioconsole import aprint
from .abstract import AIOStream

class AIOConsoleStream(AIOStream):
    async def write(self, s):
        await aprint(s)