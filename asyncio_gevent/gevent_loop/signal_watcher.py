from .watcher import Watcher

__all__ = ["SignalWatcher"]


class SignalWatcher(Watcher):
    def __init__(self, loop, signum, ref=True):
        super().__init__(loop, ref=ref)
        self.signum = signum

    def _start(self, **kwargs):
        self.loop.aio.add_signal_handler(self.signum, self._invoke)
        # return True
        return None

    def _stop(self):
        self.loop.aio.remove_signal_handler(self.signum)
