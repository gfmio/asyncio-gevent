from .watcher import Watcher

__all__ = ["IoWatcher"]

READ = 1
WRITE = 2


class IoWatcher(Watcher):
    def __init__(self, loop, fd, events, ref=True, priority=None):
        super().__init__(loop, ref=ref)
        self.fd = fd
        self.events = events
        self._reader = events & READ
        self._writer = events & WRITE

    def _start(self, pass_events=False, **kwargs):
        try:
            if self._reader:
                self.loop.aio.add_reader(self.fd, self._invoke)
            if self._writer:
                self.loop.aio.add_writer(self.fd, self._invoke)
            return None
        except Exception as e:
            print(f"Error starting IoWatcher for fd {self.fd}: {e}")
            raise e

    def _stop(self):
        if self._reader:
            self.loop.aio.remove_reader(self.fd)
        if self._writer:
            self.loop.aio.remove_writer(self.fd)
