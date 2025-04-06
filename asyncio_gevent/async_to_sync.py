import contextvars
import functools
from typing import Callable
from typing import Optional

from .future_to_greenlet import future_to_greenlet


def async_to_sync(
    coroutine: Optional[Callable] = None,
    autostart_future: bool = True,
    autocancel_future: bool = True,
    autokill_greenlet: bool = True,
    autorestore_context: bool = True,
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
                autorestore_context=autorestore_context,
            )

        return decorator

    @functools.wraps(coroutine)
    def fn(*args, **kwargs):
        greenlet = future_to_greenlet(
            coroutine(*args, **kwargs),
            autostart_future=autostart_future,
            autocancel_future=autocancel_future,
            autokill_greenlet=autokill_greenlet,
        )
        greenlet.gr_context = contextvars.copy_context()

        greenlet.start()
        greenlet.join()

        try:
            return greenlet.get()
        finally:
            if autorestore_context:
                for var in greenlet.gr_context:
                    var.set(greenlet.gr_context[var])

    return fn
