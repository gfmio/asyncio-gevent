import abc
import sys

from gevent._interfaces import ILoop
from zope.interface import implementer

# @implementer(ILoop)
# class GeventLoop:
#     """

#     The methods that create event loop watchers are `io`, `timer`,
#     `signal`, `idle`, `prepare`, `check`, `fork`, `async_`, `child`,
#     `stat`. These all return various types of :class:`IWatcher`.

#     All of those methods have one or two common arguments. *ref* is a
#     boolean saying whether the event loop is allowed to exit even if
#     this watcher is still started. *priority* is event loop specific.
#     """
#     def __init__(self):
#         self.default = False
#         self.approx_timer_resolution = 0.001

#     def run(nowait=False, once=False):
#         """
#         Run the event loop.

#         This is usually called automatically by the hub greenlet, but
#         in special cases (when the hub is *not* running) you can use
#         this to control how the event loop runs (for example, to integrate
#         it with another event loop).
#         """
#         pass

#     def now():
#         """
#         now() -> float

#         Return the loop's notion of the current time.

#         This may not necessarily be related to :func:`time.time` (it
#         may have a different starting point), but it must be expressed
#         in fractional seconds (the same *units* used by :func:`time.time`).
#         """
#         return time.time()

#     def update_now():
#         """
#         Update the loop's notion of the current time.

#         .. versionadded:: 1.3
#            In the past, this available as ``update``. This is still available as
#            an alias but will be removed in the future.
#         """
#         pass

#     def destroy():
#         """
#         Clean up resources used by this loop.

#         If you create loops
#         (especially loops that are not the default) you *should* call
#         this method when you are done with the loop.

#         .. caution::

#             As an implementation note, the libev C loop implementation has a
#             finalizer (``__del__``) that destroys the object, but the libuv
#             and libev CFFI implementations do not. The C implementation may change.

#         """

#     def io(fd, events, ref=True, priority=None):
#         """
#         Create and return a new IO watcher for the given *fd*.

#         *events* is a bitmask specifying which events to watch
#         for. 1 means read, and 2 means write.
#         """
#         asyncio

#     def closing_fd(fd):
#         """
#         Inform the loop that the file descriptor *fd* is about to be closed.

#         The loop may choose to schedule events to be delivered to any active
#         IO watchers for the fd. libev does this so that the active watchers
#         can be closed.

#         :return: A boolean value that's true if active IO watchers were
#            queued to run. Closing the FD should be deferred until the next
#            run of the eventloop with a callback.
#         """

#     def timer(after, repeat=0.0, ref=True, priority=None):
#         """
#         Create and return a timer watcher that will fire after *after* seconds.

#         If *repeat* is given, the timer will continue to fire every *repeat* seconds.
#         """

#     def signal(signum, ref=True, priority=None):
#         """
#         Create and return a signal watcher for the signal *signum*,
#         one of the constants defined in :mod:`signal`.

#         This is platform and event loop specific.
#         """

#     def idle(ref=True, priority=None):
#         """
#         Create and return a watcher that fires when the event loop is idle.
#         """

#     def prepare(ref=True, priority=None):
#         """
#         Create and return a watcher that fires before the event loop
#         polls for IO.

#         .. caution:: This method is not supported by libuv.
#         """

#     def check(ref=True, priority=None):
#         """
#         Create and return a watcher that fires after the event loop
#         polls for IO.
#         """

#     def fork(ref=True, priority=None):
#         """
#         Create a watcher that fires when the process forks.

#         Availability: Unix.
#         """

#     def async_(ref=True, priority=None):
#         """
#         Create a watcher that fires when triggered, possibly
#         from another thread.

#         .. versionchanged:: 1.3
#            This was previously just named ``async``; for compatibility
#            with Python 3.7 where ``async`` is a keyword it was renamed.
#            On older versions of Python the old name is still around, but
#            it will be removed in the future.
#         """

#     if sys.platform != "win32":

#         def child(pid, trace=0, ref=True):
#             """
#             Create a watcher that fires for events on the child with process ID *pid*.

#             This is platform specific and not available on Windows.

#             Availability: Unix.
#             """

#     def stat(path, interval=0.0, ref=True, priority=None):
#         """
#         Create a watcher that monitors the filesystem item at *path*.

#         If the operating system doesn't support event notifications
#         from the filesystem, poll for changes every *interval* seconds.
#         """

#     def run_callback(func, *args):
#         """
#         Run the *func* passing it *args* at the next opportune moment.

#         The next opportune moment may be the next iteration of the event loop,
#         the current iteration, or some other time in the future.

#         Returns a :class:`ICallback` object. See that documentation for
#         important caveats.

#         .. seealso:: :meth:`asyncio.loop.call_soon`
#            The :mod:`asyncio` equivalent.
#         """

#     def run_callback_threadsafe(func, *args):
#         """
#         Like :meth:`run_callback`, but for use from *outside* the
#         thread that is running this loop.

#         This not only schedules the *func* to run, it also causes the
#         loop to notice that the *func* has been scheduled (e.g., it causes
#         the loop to wake up).

#         .. versionadded:: 21.1.0

#         .. seealso:: :meth:`asyncio.loop.call_soon_threadsafe`
#            The :mod:`asyncio` equivalent.
#         """


READ = 1
WRITE = 2
_sys_modules = {}


class MonkeyJail:
    def __init__(self):
        self.saved = {}

    def __enter__(self):
        from gevent import monkey

        for key in list(monkey.saved) + ["selectors"]:
            if key in sys.modules:
                self.saved[key] = sys.modules.pop(key)
        sys.modules.update(_sys_modules)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key in list(self.saved) + ["selectors"]:
            if key in sys.modules:
                _sys_modules[key] = sys.modules[key]
        sys.modules.update(self.saved)


class RefMixin:
    def __init__(self, loop, ref=True):
        self.loop = loop
        self.ref = ref
        self._ref_increased = False

    def _increase_ref(self):
        if self.ref:
            self._ref_increased = True
            self.loop.increase_ref()

    def _decrease_ref(self):
        if self._ref_increased:
            self._ref_increased = False
            self.loop.decrease_ref()

    def __del__(self):
        self._decrease_ref()


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
        except:
            self.loop.handle_error(self, *sys.exc_info())


class TimerWatcher(Watcher):
    def __init__(self, loop, after, ref=True):
        super().__init__(loop, ref=ref)
        self.after = after
        self._handle = None

    def _start(self, update=True):
        self._handle = self.loop.aio.call_later(self.after, self._invoke)
        return True

    def _stop(self):
        if self._handle is not None:
            self._handle.cancel()

    def _invoke(self):
        self.active = False
        super()._invoke()


class IoWatcher(Watcher):
    def __init__(self, loop, fd, events, ref=True, priority=None):
        super().__init__(loop, ref=ref)
        self.fd = fd
        self.events = events
        self._reader = events & READ
        self._writer = events & WRITE

    def _start(self, pass_events=False):
        if self._reader:
            self.loop.aio.add_reader(self.fd, self._invoke)
        if self._writer:
            self.loop.aio.add_writer(self.fd, self._invoke)
        return True

    def _stop(self):
        if self._reader:
            self.loop.aio.remove_reader(self.fd)
        if self._writer:
            self.loop.aio.remove_writer(self.fd)


class ForkWatcher(Watcher):
    def _start(self):
        self.loop.fork_watchers.add(self)
        return True

    def _stop(self):
        self.loop.fork_watchers.discard(self)


class AsyncWatcher(Watcher):
    def __init__(self, loop, ref=True):
        super().__init__(loop, ref=ref)
        self._handle = None

    def _start(self):
        return True

    def _stop(self):
        if self._handle is not None:
            self._handle.cancel()

    def send(self):
        self.pending = True
        self._handle = self.loop.aio.call_soon_threadsafe(self._invoke)


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


class SignalWatcher(Watcher):
    def __init__(self, loop, signum, ref=True):
        super().__init__(loop, ref=ref)
        self.signum = signum

    def _start(self):
        self.loop.aio.add_signal_handler(self.signum, self._invoke)
        return True

    def _stop(self):
        self.loop.aio.remove_signal_handler(self.signum)


class Callback(RefMixin):
    def __init__(self, loop, callback, args):
        super().__init__(loop)
        self.callback = callback
        self.args = args
        self._handle = self.loop.aio.call_soon(self.run)
        self._increase_ref()

    def stop(self):
        self.callback = None
        self.args = None
        self._handle.cancel()
        self._decrease_ref()

    def run(self):
        try:
            callback, args = self.callback, self.args
            self.callback = self.args = None
            # noinspection PyCallingNonCallable,PyArgumentList
            callback(*args)
        except Exception:
            raise
        except:
            self.loop.handle_error(self, *sys.exc_info())
        finally:
            self._decrease_ref()

    def __bool__(self):
        return self.args is not None

    @property
    def pending(self):
        return self.callback is not None


__all__ = ["GeventLoop"]


@implementer(ILoop)
class GeventLoop:
    MAXPRI = 0

    def __init__(self, flags=None, default=None):
        with MonkeyJail():
            import asyncio

            self.policy = asyncio.get_event_loop_policy()
            self.aio = self.policy.get_event_loop()
        self.error_handler = None
        self.fork_watchers = set()
        self._ref_count = 0
        self._stop_handle = None
        self.aio.set_exception_handler(self._handle_aio_error)

    def timer(self, after, repeat=0.0, ref=True, priority=None):
        return TimerWatcher(self, after, ref)

    def io(self, fd, events, ref=True, priority=None):
        return IoWatcher(self, fd, events, ref, priority)

    def fork(self, ref=True, priority=None):
        return ForkWatcher(self, ref=ref)

    def async_(self, ref=True, priority=None):
        return AsyncWatcher(self, ref=ref)

    def child(self, pid, trace=0, ref=True):
        return ChildWatcher(self, pid, ref=ref)

    def signal(self, signum, ref=True, priority=None):
        return SignalWatcher(self, signum, ref=ref)

    def run_callback(self, func, *args):
        return Callback(self, func, args)

    def run(self, nowait=False, once=False):
        self.aio.run_forever()

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
        except:
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
