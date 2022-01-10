import asyncio

from .event_loop import EventLoop

__all__ = ["EventLoopPolicy"]


class EventLoopPolicy(asyncio.DefaultEventLoopPolicy):  # type: ignore
    """
    An asyncio event loop policy with the all the default behaviours except
    that it uses the `asyncio_gevent.EventLoop` which uses gevent for
    scheduling
    """

    _loop_factory = EventLoop
