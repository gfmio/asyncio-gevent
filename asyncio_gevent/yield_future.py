import asyncio
import threading
from typing import Optional

import gevent


def yield_future(
    future: asyncio.Future, loop: Optional[asyncio.AbstractEventLoop] = None
) -> gevent.Greenlet:
    """Wait for a future, a task, or a coroutine object from a greenlet.

    Yield control other eligible greenlet until the future is done (finished
    successfully or failed with an exception).

    Return the result or raise the exception of the future.

    The function must not be called from the greenlet running the aiogreen
    event loop.
    """
    loop = loop or asyncio.get_event_loop()

    future = asyncio.ensure_future(future, loop=loop)

    if future._loop._greenlet == gevent.getcurrent():
        raise RuntimeError(
            "yield_future() must not be called from "
            "the greenlet of the aiogreen event loop"
        )

    event = gevent.event.Event()

    def wakeup_event(fut):
        event.set()

    future.add_done_callback(wakeup_event)
    event.wait()

    return future.result()
