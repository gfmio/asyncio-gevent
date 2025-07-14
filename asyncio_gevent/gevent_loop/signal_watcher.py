from .watcher import Watcher

__all__ = ["SignalWatcher"]


class SignalWatcher(Watcher):
    def __init__(self, loop, signum, ref=True):
        super().__init__(loop, ref=ref)
        self.signum = signum

    def _start(self, **kwargs):
        try:
            self.loop.aio.add_signal_handler(self.signum, self._invoke)
            return None
        except Exception as e:
            print(f"Error starting SignalWatcher for signum {self.signum}: {e}")
            raise e

    def _stop(self):
        self.loop.aio.remove_signal_handler(self.signum)
