from typing import Callable

import gevent

from .greenlet_to_future import greenlet_to_future


def sync_to_async(
    fn: Callable,
    autocancel_future: bool = True,
    autostart_greenlet: bool = True,
    autokill_greenlet: bool = True,
):
    """
    Wrap the blocking function `fn` (that may spawn greenlets) in a coroutine function that spawns a greenlet to execute `fn` and returns when the greenlet is dead
    """

    async def coroutine(*args, **kwargs):
        return await greenlet_to_future(
            gevent.Greenlet(fn, *args, **kwargs),
            autocancel_future=autocancel_future,
            autostart_greenlet=autostart_greenlet,
            autokill_greenlet=autokill_greenlet,
        )

    return coroutine
