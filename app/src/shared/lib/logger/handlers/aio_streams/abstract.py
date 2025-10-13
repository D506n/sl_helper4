from io import StringIO

class AIOStream(StringIO):
    async def write(self, s):
        return super().write(s)

    async def flush(self):
        return super().flush()