import sys

from gevent._interfaces import ICallback
from zope.interface import implementer

from .ref_mixin import RefMixin

__all__ = ["Callback"]


@implementer(ICallback)
class Callback(RefMixin):
    def __init__(self, loop, callback, args, thread_safe=False):
        super().__init__(loop)
        self.callback = callback
        self.args = args
        self._handle = (
            self.loop.aio.call_soon_threadsafe(self.run) if thread_safe else self.loop.aio.call_soon(self.run)
        )
        self._increase_ref()

    def stop(self):
        self.callback = None
        self.args = None
        self._handle.cancel()
        self._decrease_ref()

    def run(self):
        try:
            callback, args = self.callback, self.args
            self.callback = None
            self.args = None
            if callback is None or args is None:
                raise RuntimeError("Callback is already stopped")
            callback(*args)
        except Exception:
            raise
        except:  # noqa: E722
            self.loop.handle_error(self, *sys.exc_info())
        finally:
            self._decrease_ref()

    def __bool__(self):
        return self.args is not None

    @property
    def pending(self):
        return self.callback is not None

    def close(self):
        pass
