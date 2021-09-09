from typing import Callable

from .future_to_greenlet import future_to_greenlet


def async_to_sync(
    coroutine: Callable,
    autostart_future: bool = True,
    autocancel_future: bool = True,
    autokill_greenlet: bool = True,
):
    """
    Wrap a coroutine function in a blocking function that spawns a greenlet and blocks until the future is done.
    """

    def fn(*args, **kwargs):
        greenlet = future_to_greenlet(
            coroutine(*args, **kwargs),
            autostart_future=autostart_future,
            autocancel_future=autocancel_future,
            autokill_greenlet=autokill_greenlet,
        )
        greenlet.start()
        greenlet.join()
        return greenlet.get()

    return fn
