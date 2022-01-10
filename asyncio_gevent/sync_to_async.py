from typing import Callable
from typing import Optional

import gevent

from .greenlet_to_future import greenlet_to_future


def sync_to_async(
    fn: Optional[Callable] = None,
    autocancel_future: bool = True,
    autostart_greenlet: bool = True,
    autokill_greenlet: bool = True,
) -> Callable:
    """
    Convert a synchronous/blocking function to an asynchronous one.

    This wraps the blocking function `fn` (that may spawn greenlets) in a coroutine function that spawns a greenlet to
    execute `fn` and returns when the greenlet is dead.
    """
    if fn is None:

        def decorator(fn: Callable):
            return sync_to_async(
                fn=fn,
                autocancel_future=autocancel_future,
                autostart_greenlet=autostart_greenlet,
                autokill_greenlet=autokill_greenlet,
            )

        return decorator

    async def coroutine(*args, **kwargs):
        return await greenlet_to_future(
            gevent.Greenlet(fn, *args, **kwargs),
            autocancel_future=autocancel_future,
            autostart_greenlet=autostart_greenlet,
            autokill_greenlet=autokill_greenlet,
        )

    return coroutine
