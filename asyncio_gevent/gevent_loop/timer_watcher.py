from .watcher import Watcher

__all__ = ["TimerWatcher"]


class TimerWatcher(Watcher):
    def __init__(self, loop, after, ref=True):
        super().__init__(loop, ref=ref)
        self.after = after
        self._handle = None

    def _start(self, update=True, **kwargs):
        try:
            self._handle = self.loop.aio.call_later(self.after, self._invoke)
            return None
        except Exception as e:
            print(f"Error starting TimerWatcher for after {self.after}: {e}")
            raise e

    def _stop(self):
        if self._handle is not None:
            self._handle.cancel()

    def _invoke(self):
        self.active = False
        super()._invoke()

    def close(self):
        """Close the timer and clean up resources."""
        self.stop()

    def __enter__(self):
        self._start()
        return self

    def __exit__(self, *args):
        self._stop()
