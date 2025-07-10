import asyncio
from typing import Callable
from typing import Optional
from typing import Coroutine
from typing import Union

import gevent.event

__all__ = ["future_to_greenlet"]


def future_to_greenlet(
    future: Union[asyncio.Future, Coroutine],
    loop: Optional[asyncio.AbstractEventLoop] = None,
    autostart_future: bool = True,
    autocancel_future: bool = True,
    autokill_greenlet: bool = True,
) -> gevent.Greenlet:
    """
    Wrap a future (or coroutine object) in a greenlet.

    The greenlet returned by this function will not start automatically, so you
    need to call `Greenlet.start()` manually.

    If `future` is a coroutine object, it will be scheduled as a task on the
    `loop` when the greenlet starts. If no `loop` argument has been passed, the
    running event loop will be used. If there is no running event loop, a new
    event loop will be started using the current event loop policy.

    If the future is not already scheduled, then it won't be scheduled for
    execution until the greenlet starts running. To prevent the future from
    being scheduled automatically, you can pass `autostart_future=False` as an
    argument to `future_to_greenlet`.

    If the greenlet gets killed, the by default the future gets cancelled. To
    prevent this from happening and having the future return the
    `GreenletExit` object instead, you can pass `autocancel_future=False` as an
    argument to `future_to_greenlet`.

    If the future gets cancelled, the greenlet gets killed and will return a
    `GreenletExit`. This default behaviour can be circumvented by passing
    `autokill_greenlet=False` and the greenlet will raise the `CancelledError`
    instead.
    """

    def on_cancelled():
        if autokill_greenlet:
            greenlet.kill()
        else:
            raise

    greenlet = gevent.Greenlet(
        run=_run,
        future_or_coro=future,
        loop=loop,
        autostart_future=autostart_future,
        on_cancelled=on_cancelled,
    )

    def cb(gt):
        if isinstance(gt.value, gevent.GreenletExit):
            if asyncio.iscoroutine(future):
                future.close()
            elif asyncio.isfuture(future):
                future.cancel()

    if autocancel_future:
        greenlet.link_value(cb)

    return greenlet


def _run(
    future_or_coro: Union[asyncio.Future, Coroutine],
    loop: Optional[asyncio.AbstractEventLoop],
    autostart_future: bool,
    on_cancelled: Callable,
):
    active_loop = loop

    # If not loop argument was specified, try and use the running loop

    if not active_loop:
        try:
            active_loop = asyncio.get_running_loop()
        except RuntimeError:
            pass

    try:
        future: asyncio.Future

        if not autostart_future:
            if asyncio.iscoroutine(future_or_coro):
                future = asyncio.create_task(future_or_coro)
            elif asyncio.isfuture(future_or_coro):
                future = future_or_coro
            else:
                raise TypeError("Expected a future or coroutine")
        elif not active_loop:
            # If there's no running loop and no loop argument was specified,
            # then get a loop and run it to completion in a spawned greenlet

            active_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(active_loop)

            future = asyncio.ensure_future(future_or_coro, loop=active_loop)

            run_until_complete_greenlet = gevent.spawn(active_loop.run_until_complete, future)
            run_until_complete_greenlet.join()
        else:
            # If there's a running loop already or a loop argument was specified,
            # then schedule the future and block until it's done

            future = asyncio.ensure_future(future_or_coro, loop=active_loop)

            event = gevent.event.Event()

            def done(_):
                event.set()

            future.add_done_callback(done)

            event.wait()

        return future.result()
    except asyncio.CancelledError:
        on_cancelled()
