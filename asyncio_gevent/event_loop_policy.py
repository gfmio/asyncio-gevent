import asyncio
import threading

from .event_loop import EventLoop


class EventLoopPolicy(asyncio.AbstractEventLoopPolicy):
    _loop_factory = EventLoop

    def __init__(self):
        # gevent does not support threads, an attribute is enough
        self._loop = None

    def get_event_loop(self):
        # if not isinstance(threading.current_thread(), threading._MainThread):
        #     raise RuntimeError("aiogevent event loop must run in the main thread")
        if self._loop is None:
            self._loop = self.new_event_loop()
        return self._loop

    def set_event_loop(self, loop):
        self._loop = loop

    def new_event_loop(self):
        return self._loop_factory()
