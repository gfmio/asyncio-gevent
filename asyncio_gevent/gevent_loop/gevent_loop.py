import sys
import time

from gevent._interfaces import ILoop
from zope.interface import implementer

from .async_watcher import AsyncWatcher
from .callback import Callback
from .child_watcher import ChildWatcher
from .fork_watcher import ForkWatcher
from .io_watcher import IoWatcher
from .monkey_jail import MonkeyJail
from .signal_watcher import SignalWatcher
from .timer_watcher import TimerWatcher

__all__ = ["GeventLoop"]


@implementer(ILoop)
class GeventLoop:
    """

    The methods that create event loop watchers are `io`, `timer`,
    `signal`, `idle`, `prepare`, `check`, `fork`, `async_`, `child`,
    `stat`. These all return various types of :class:`IWatcher`.

    All of those methods have one or two common arguments. *ref* is a
    boolean saying whether the event loop is allowed to exit even if
    this watcher is still started. *priority* is event loop specific.
    """

    MAXPRI = 0

    def __init__(self, flags=None, default=None):
        self._aio = None
        self.error_handler = None
        self.fork_watchers = set()
        self._ref_count = 0
        self._stop_handle = None
        self.aio.set_exception_handler(self._handle_aio_error)

    def run(self, nowait=False, once=False):
        """
        Run the event loop.

        This is usually called automatically by the hub greenlet, but
        in special cases (when the hub is *not* running) you can use
        this to control how the event loop runs (for example, to integrate
        it with another event loop).
        """
        if self.aio.is_running:
            return
        self.aio.run_forever()

    def now(self):
        """
        now() -> float

        Return the loop's notion of the current time.

        This may not necessarily be related to :func:`time.time` (it
        may have a different starting point), but it must be expressed
        in fractional seconds (the same *units* used by :func:`time.time`).
        """
        return time.time()

    def update_now(self):
        """
        Update the loop's notion of the current time.

        .. versionadded:: 1.3
           In the past, this available as ``update``. This is still available as
           an alias but will be removed in the future.
        """
        pass

    def destroy(self):
        """
        Clean up resources used by this loop.

        If you create loops
        (especially loops that are not the default) you *should* call
        this method when you are done with the loop.

        .. caution::

            As an implementation note, the libev C loop implementation has a
            finalizer (``__del__``) that destroys the object, but the libuv
            and libev CFFI implementations do not. The C implementation may change.

        """
        pass

    def io(self, fd, events, ref=True, priority=None):
        """
        Create and return a new IO watcher for the given *fd*.

        *events* is a bitmask specifying which events to watch
        for. 1 means read, and 2 means write.
        """
        return IoWatcher(self, fd, events, ref, priority)

    def closing_fd(self, fd):
        """
        Inform the loop that the file descriptor *fd* is about to be closed.

        The loop may choose to schedule events to be delivered to any active
        IO watchers for the fd. libev does this so that the active watchers
        can be closed.

        :return: A boolean value that's true if active IO watchers were
           queued to run. Closing the FD should be deferred until the next
           run of the eventloop with a callback.
        """
        pass

    def timer(self, after, repeat=0.0, ref=True, priority=None):
        """
        Create and return a timer watcher that will fire after *after* seconds.

        If *repeat* is given, the timer will continue to fire every *repeat* seconds.
        """
        return TimerWatcher(self, after, ref)

    def signal(self, signum, ref=True, priority=None):
        """
        Create and return a signal watcher for the signal *signum*,
        one of the constants defined in :mod:`signal`.

        This is platform and event loop specific.
        """
        return SignalWatcher(self, signum, ref=ref)

    def idle(self, ref=True, priority=None):
        """
        Create and return a watcher that fires when the event loop is idle.
        """
        pass

    def prepare(self, ref=True, priority=None):
        """
        Create and return a watcher that fires before the event loop
        polls for IO.

        .. caution:: This method is not supported by libuv.
        """
        pass

    def check(self, ref=True, priority=None):
        """
        Create and return a watcher that fires after the event loop
        polls for IO.
        """
        pass

    def fork(self, ref=True, priority=None):
        """
        Create a watcher that fires when the process forks.

        Availability: Unix.
        """
        return ForkWatcher(self, ref=ref)

    def async_(self, ref=True, priority=None):
        """
        Create a watcher that fires when triggered, possibly
        from another thread.

        .. versionchanged:: 1.3
           This was previously just named ``async``; for compatibility
           with Python 3.7 where ``async`` is a keyword it was renamed.
           On older versions of Python the old name is still around, but
           it will be removed in the future.
        """
        return AsyncWatcher(self, ref=ref)

    if sys.platform != "win32":

        def child(self, pid, trace=0, ref=True):
            """
            Create a watcher that fires for events on the child with process ID *pid*.

            This is platform specific and not available on Windows.

            Availability: Unix.
            """
            return ChildWatcher(self, pid, ref=ref)

    def stat(self, path, interval=0.0, ref=True, priority=None):
        """
        Create a watcher that monitors the filesystem item at *path*.

        If the operating system doesn't support event notifications
        from the filesystem, poll for changes every *interval* seconds.
        """

    def run_callback(self, func, *args):
        """
        Run the *func* passing it *args* at the next opportune moment.

        The next opportune moment may be the next iteration of the event loop,
        the current iteration, or some other time in the future.

        Returns a :class:`ICallback` object. See that documentation for
        important caveats.

        .. seealso:: :meth:`asyncio.loop.call_soon`
           The :mod:`asyncio` equivalent.
        """
        return Callback(self, func, args)

    def run_callback_threadsafe(self, func, *args):
        """
        Like :meth:`run_callback`, but for use from *outside* the
        thread that is running this loop.

        This not only schedules the *func* to run, it also causes the
        loop to notice that the *func* has been scheduled (e.g., it causes
        the loop to wake up).

        .. versionadded:: 21.1.0

        .. seealso:: :meth:`asyncio.loop.call_soon_threadsafe`
           The :mod:`asyncio` equivalent.
        """
        return Callback(self, func, args, thread_safe=True)

    def handle_error(self, context, _type, value, tb):
        error_handler = self.error_handler
        if error_handler is not None:
            # we do want to do getattr every time so that setting
            # Hub.handle_error property just works
            handle_error = getattr(error_handler, "handle_error", error_handler)
            handle_error(context, _type, value, tb)
        else:
            self.aio.default_exception_handler(context)

    def _handle_aio_error(self, loop, context):
        try:
            self.handle_error(context, *sys.exc_info())
        except:  # noqa: E722
            # hmm, test__pool will fail if we let the error propagate - it will
            # stop the main loop unexpectedly
            pass

    def reinit(self):
        for watcher in self.fork_watchers:
            self.run_callback(watcher.callback, *watcher.args)

    def install_sigchld(self):
        pass

    def increase_ref(self):
        self._ref_count += 1
        if self._stop_handle is not None:
            self._stop_handle.cancel()
            self._stop_handle = None

    def decrease_ref(self):
        self._ref_count -= 1
        if self._ref_count <= 0 and self._stop_handle is None:
            self._stop_handle = self.aio.call_soon_threadsafe(self._stop)

    def _stop(self):
        self._stop_handle = None
        if self._ref_count <= 0:
            self.aio.stop()

    @property
    def aio(self):
        self._get_or_create_aio()
        return self._aio

    def _get_or_create_aio(self):
        if self._aio and (self._aio.is_closed or self.aio._stopping):
            self._aio = None

        if self._aio:
            return self._aio

        with MonkeyJail():
            import asyncio

            try:
                self._aio = asyncio.get_running_loop()
            except RuntimeError:
                self._aio = asyncio.new_event_loop()
                asyncio.set_event_loop(self._aio)

        return self._aio

    def _format(self):
        return "GeventLoop"
