from .watcher import Watcher

__all__ = ["ChildWatcher"]


class ChildWatcher(Watcher):
    def __init__(self, loop, pid, ref=True):
        super().__init__(loop, ref=ref)
        self.pid = pid
        self.rcode = None
        self.rpid = None

    def _start(self, **kwargs):
        try:
            import asyncio

            policy = asyncio.get_event_loop_policy()
            watcher = policy.get_child_watcher()
            watcher.add_child_handler(self.pid, self._invoke_wrapper)
            self._watcher = watcher
            return None
        except Exception as e:
            print(f"Error starting IoWatcher for pid {self.pid}: {e}")
            raise e

    def _stop(self):
        if hasattr(self, "_watcher"):
            self._watcher.remove_child_handler(self.pid)

    def _invoke_wrapper(self, pid, retcode):
        self.rpid = pid
        self.rcode = retcode
        self._invoke()
