import aiofiles
from .abstract import AIOStream

class AIOFileStream(AIOStream):
    async def write(self, s):
        async with aiofiles.open(self.name, 'a') as f:
            res = await f.write(s)
            await f.flush()
            return res