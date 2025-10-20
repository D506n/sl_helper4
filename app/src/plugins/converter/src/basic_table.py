from typing import Generator, AsyncGenerator

class TableIter():
    def __init__(self, rows:Generator[str, None, None]|list[str]):
        self.rows = rows

    async def __async_iterable_from_rows(self) -> AsyncGenerator[str, None]:
        for row in self.rows:
            yield row

    async def __aiter__(self):
        async for row in self.__async_iterable_from_rows():
            yield row