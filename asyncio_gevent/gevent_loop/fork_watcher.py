from .watcher import Watcher

__all__ = ["ForkWatcher"]


class ForkWatcher(Watcher):
    def _start(self, **kwargs):
        self.loop.fork_watchers.add(self)
        return None
        # return True

    def _stop(self):
        self.loop.fork_watchers.discard(self)
