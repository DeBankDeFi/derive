import asyncio
from functools import wraps


def async_test(func):
    @wraps(func)
    def wrapped(self):
        async def _():
            await func(self)

        asyncio.run(_())

    return wrapped
