from .watcher import Watcher

__all__ = ["AsyncWatcher"]


class AsyncWatcher(Watcher):
    def __init__(self, loop, ref=True):
        super().__init__(loop, ref=ref)
        self._handle = None

    def _start(self):
        return True

    def _stop(self):
        if self._handle is not None:
            self._handle.cancel()

    def send(self):
        self.pending = True
        self._handle = self.loop.aio.call_soon_threadsafe(self._invoke)
