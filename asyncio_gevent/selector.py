import asyncio
import selectors
import socket
import sys

import gevent.core
import gevent.event
import gevent.hub
import greenlet

if sys.platform == "win32":
    from asyncio.windows_utils import socketpair
else:
    socketpair = socket.socketpair

_PY3 = sys.version_info >= (3,)

_EVENT_READ = selectors.EVENT_READ
_EVENT_WRITE = selectors.EVENT_WRITE
_BaseSelectorImpl = selectors._BaseSelectorImpl


class _Selector(_BaseSelectorImpl):
    def __init__(self, loop):
        super(_Selector, self).__init__()
        # fd => events
        self._notified = {}
        self._loop = loop
        # gevent.event.Event() used by FD notifiers to wake up select()
        self._event = None
        self._gevent_events = {}
        self._gevent_loop = gevent.hub.get_hub().loop

    def close(self):
        keys = list(self.get_map().values())
        for key in keys:
            self.unregister(key.fd)
        super(_Selector, self).close()

    def _notify(self, fd, event):
        if fd in self._notified:
            self._notified[fd] |= event
        else:
            self._notified[fd] = event
        if self._event is not None:
            # wakeup the select() method
            self._event.set()

    # FIXME: what is x?
    def _notify_read(self, event, x):
        self._notify(event.fd, _EVENT_READ)

    def _notify_write(self, event, x):
        self._notify(event.fd, _EVENT_WRITE)

    def _read_events(self):
        notified = self._notified
        self._notified = {}
        ready = []
        for fd, events in notified.items():
            key = self.get_key(fd)
            ready.append((key, events & key.events))

            for event in (_EVENT_READ, _EVENT_WRITE):
                if key.events & event:
                    self._register(key.fd, event)
        return ready

    def _register(self, fd, event):
        if fd in self._gevent_events:
            event_dict = self._gevent_events[fd]
        else:
            event_dict = {}
            self._gevent_events[fd] = event_dict

        try:
            watcher = event_dict[event]
        except KeyError:
            pass
        else:
            watcher.stop()

        if event == _EVENT_READ:

            def func():
                self._notify(fd, _EVENT_READ)

            watcher = self._gevent_loop.io(fd, 1)
            watcher.start(func)
        else:

            def func():
                self._notify(fd, _EVENT_WRITE)

            watcher = self._gevent_loop.io(fd, 2)
            watcher.start(func)
        event_dict[event] = watcher

    def register(self, fileobj, events, data=None):
        key = super(_Selector, self).register(fileobj, events, data)
        for event in (_EVENT_READ, _EVENT_WRITE):
            if events & event:
                self._register(key.fd, event)
        return key

    def unregister(self, fileobj):
        key = super(_Selector, self).unregister(fileobj)
        event_dict = self._gevent_events.pop(key.fd, {})
        for event in (_EVENT_READ, _EVENT_WRITE):
            try:
                watcher = event_dict[event]
            except KeyError:
                continue
            watcher.stop()
        return key

    def select(self, timeout):
        events = self._read_events()
        if events:
            return events
        self._event = gevent.event.Event()
        try:
            if timeout is not None:
                if not self._event.wait(timeout):
                    self._event.set()
            else:
                # blocking call
                self._event.wait(0)
            return self._read_events()
        finally:
            self._event = None
