import asyncio

import gevent

__all__ = ["greenlet_to_future"]


def _dead_greenlet_to_future(greenlet: gevent.Greenlet, future: asyncio.Future, autocancel_future: bool) -> None:
    try:
        result = greenlet.get(block=False)
        if autocancel_future and isinstance(result, gevent.GreenletExit):
            future.cancel()
        else:
            future.set_result(result)
    except Exception as e:
        future.set_exception(e)


async def _await_greenlet(
    greenlet: gevent.Greenlet,
    autocancel_future: bool,
    autostart_greenlet: bool,
    autokill_greenlet: bool,
):
    # Start the greenlet if it is not yet running
    if not greenlet and autostart_greenlet:
        greenlet.start()

    future: asyncio.Future = asyncio.Future()

    # If the greenlet is dead, set the result

    if greenlet.dead:
        _dead_greenlet_to_future(greenlet, future, autocancel_future)
    else:

        def cb(_):
            _dead_greenlet_to_future(greenlet, future, autocancel_future)

        greenlet.link(cb)

    try:
        loop = asyncio.get_running_loop()

        result, _ = await asyncio.gather(future, loop.run_in_executor(None, greenlet.join))

        return result
    except asyncio.CancelledError:
        if autokill_greenlet:
            greenlet.kill()
        raise


def greenlet_to_future(
    greenlet: gevent.Greenlet,
    autocancel_future: bool = True,
    autostart_greenlet: bool = True,
    autokill_greenlet: bool = True,
) -> asyncio.Future:
    """
    Wrap a greenlet in a future.

    If the greenlet is already dead when the future is awaited/scheduled, then
    the future will resolve with the result or raise the exception thrown
    immediately.

    If the greenlet is not yet running, the greenlet will by default be started
    when the future is awaited/scheduled. This is to ensure a sensible default
    behaviour and prevent odd concurrency issues. To prevent this
    auto-starting, you can pass `autostart_greenlet=False` as an argument to
    `greenlet_to_future`.

    When a greenlet is killed without a custom exception type, it will return
    (*not* raise) a `GreenletExit` exception. In this instance, by default, the
    future gets cancelled. To circumvent this behaviour and have the function
    return the `GreenletExit` object, you can pass `autocancel_future=False` as
    an argument to `greenlet_to_future`. If a custom exception type is used,
    the future will always raise the exception.

    If the future gets cancelled, then by default the greenlet is killed. To
    prevent the greenlet from getting killed, you can pass
    `autokill_greenlet=False` as an argument to `greenlet_to_future`.
    """

    return asyncio.ensure_future(_await_greenlet(greenlet, autocancel_future, autostart_greenlet, autokill_greenlet))
