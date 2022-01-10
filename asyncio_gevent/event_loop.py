import asyncio

import gevent.selectors

__all__ = ["EventLoop"]


class EventLoop(asyncio.SelectorEventLoop):
    """
    An asyncio event loop that uses gevent for scheduling and runs in a spawned
    greenlet
    """

    def __init__(self, selector=None):
        super().__init__(selector or gevent.selectors.DefaultSelector())

    def run_forever(self):
        greenlet = gevent.spawn(super(EventLoop, self).run_forever)
        greenlet.join()
