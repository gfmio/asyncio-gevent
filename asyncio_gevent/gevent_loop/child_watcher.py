from .watcher import Watcher

__all__ = ["ChildWatcher"]


class ChildWatcher(Watcher):
    def __init__(self, loop, pid, ref=True):
        super().__init__(loop, ref=ref)
        self.pid = pid
        self.watcher = self.loop.policy.get_child_watcher()
        self.rcode = None
        self.rpid = None

    def _start(self):
        self.watcher.add_child_handler(self.pid, self._invoke_wrapper)
        return True

    def _stop(self):
        self.watcher.remove_child_handler(self.pid)

    def _invoke_wrapper(self, pid, retcode):
        self.rpid = pid
        self.rcode = retcode
        self._invoke()
