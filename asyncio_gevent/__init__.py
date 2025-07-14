from .async_to_sync import async_to_sync
from .event_loop import EventLoop
from .event_loop_policy import EventLoopPolicy
from .future_to_greenlet import future_to_greenlet
from .gevent_loop import GeventLoop
from .greenlet_to_future import greenlet_to_future
from .sync_to_async import sync_to_async

__all__ = [
    "async_to_sync",
    "EventLoop",
    "EventLoopPolicy",
    "future_to_greenlet",
    "greenlet_to_future",
    "sync_to_async",
    "GeventLoop",
]

# # GeventLoop is imported separately to avoid circular imports when used as gevent's loop
# def __getattr__(name):
#     if name == "GeventLoop":
#         from .gevent_loop.gevent_loop import GeventLoop
#         return GeventLoop
#     raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
