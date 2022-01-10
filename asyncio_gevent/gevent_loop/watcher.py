import abc
import sys

from gevent._interfaces import IWatcher
from zope.interface import implementer

from .ref_mixin import RefMixin

__all__ = ["Watcher"]


@implementer(IWatcher)
class Watcher(RefMixin, metaclass=abc.ABCMeta):
    def __init__(self, loop, ref=True):
        super().__init__(loop, ref)
        self._callback = None
        self.args = ()
        self.pending = False
        self.active = False

    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self, callback):
        if not callable(callback) and callback is not None:
            raise TypeError("Expected callable, not %r" % (callback,))
        self._callback = callback

    def start(self, callback, *args, **kwargs):
        if self.active:
            return
        if callback is None:
            raise TypeError("callback must be callable, not None")
        self.callback = callback
        self.args = args
        self.active = self._start(**kwargs)
        if self.active:
            self._increase_ref()

    @abc.abstractmethod
    def _start(self, **kwargs):
        pass

    def stop(self):
        self._decrease_ref()
        self._callback = None
        self.args = None
        self.active = False
        self.pending = False
        self._stop()

    def _stop(self):
        pass

    def _invoke(self):
        self.pending = False
        # noinspection PyBroadException
        try:
            # noinspection PyCallingNonCallable
            self.callback(*self.args)
        except Exception:
            raise
        except:  # noqa: E722
            self.loop.handle_error(self, *sys.exc_info())
