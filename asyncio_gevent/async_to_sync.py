from typing import Callable
from typing import Optional

from .future_to_greenlet import future_to_greenlet


def async_to_sync(
    coroutine: Optional[Callable] = None,
    autostart_future: bool = True,
    autocancel_future: bool = True,
    autokill_greenlet: bool = True,
):
    """
    Wrap a coroutine function in a blocking function that spawns a greenlet and blocks until the future is done.
    """
    if coroutine is None:

        def decorator(coroutine: Callable):
            return async_to_sync(
                coroutine=coroutine,
                autostart_future=autostart_future,
                autocancel_future=autocancel_future,
                autokill_greenlet=autokill_greenlet,
            )

        return decorator

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
