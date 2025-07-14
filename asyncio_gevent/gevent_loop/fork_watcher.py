from .watcher import Watcher

__all__ = ["ForkWatcher"]


class ForkWatcher(Watcher):
    def _start(self, **kwargs):
        try:
            self.loop.fork_watchers.add(self)
            return None
        except Exception as e:
            print(f"Error starting ForkWatcher: {e}")
            raise e

    def _stop(self):
        self.loop.fork_watchers.discard(self)
