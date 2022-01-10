import asyncio
from asyncio import CancelledError
from typing import Callable
from typing import Optional

import gevent.event

__all__ = ["future_to_greenlet"]


def future_to_greenlet(
    future: asyncio.Future,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    autostart_future: bool = True,
    autocancel_future: bool = True,
    autokill_greenlet: bool = True,
) -> gevent.Greenlet:
    """
    Wrap a future in a greenlet.

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
    `GreenletExit` objct instead, you can pass `autocancel_future=False` as an
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
        future=future,
        loop=loop,
        autostart_future=autostart_future,
        on_cancelled=on_cancelled,
    )

    def cb(gt):
        if isinstance(gt.value, gevent.GreenletExit):
            future.cancel()

    if autocancel_future:
        greenlet.link_value(cb)

    return greenlet


def _run(
    future: asyncio.Future,
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
        ensured_future: asyncio.Future

        if not autostart_future:
            ensured_future = future
        elif not active_loop:
            # If there's no running loop and no loop argument was specified,
            # then get a loop and run it to completion in a spawned greenlet

            active_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(active_loop)

            ensured_future = asyncio.ensure_future(future, loop=active_loop)

            run_until_complete_greenlet = gevent.spawn(
                active_loop.run_until_complete, ensured_future
            )
            run_until_complete_greenlet.join()
        else:
            # If there's a running loop already or a loop argument was specified,
            # then schedule the future and block until it's done

            ensured_future = asyncio.ensure_future(future, loop=active_loop)

            event = gevent.event.Event()

            def done(_):
                event.set()

            ensured_future.add_done_callback(done)

            event.wait()

        return ensured_future.result()
    except CancelledError:
        on_cancelled()
