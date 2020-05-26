import asyncio
import time

class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())
        self._start_time = time.time()

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback()

    @property
    def remaining(self):
        """
        How much time is left on this timer.
        """
        return self._timeout - (time.time() - self._start_time)

    def cancel(self):
        self._task.cancel()
