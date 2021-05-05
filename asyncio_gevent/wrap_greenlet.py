import asyncio
import threading
from typing import Optional

import gevent
import greenlet


def wrap_greenlet(
    gt: greenlet.greenlet, loop: Optional[asyncio.AbstractEventLoop] = None
) -> asyncio.Future:
    """Wrap a greenlet into a Future object.

    The Future object waits for the completion of a greenlet. The result or the
    exception of the greenlet will be stored in the Future object.

    Greenlet of greenlet and gevent modules are supported: gevent.greenlet
    and greenlet.greenlet.

    The greenlet must be wrapped before its execution starts. If the greenlet
    is running or already finished, an exception is raised.

    For gevent.Greenlet, the _run attribute must be set. For greenlet.greenlet,
    the run attribute must be set.
    """
    future = asyncio.Future(loop=loop)

    if not isinstance(gt, greenlet.greenlet):
        raise TypeError(
            "greenlet.greenlet or gevent.greenlet request, not %s" % type(gt)
        )

    if gt.dead:
        raise RuntimeError("wrap_greenlet: the greenlet already finished")

    def wrap_fn(fn):
        def wrapped_fn(*args, **kw):
            try:
                result = fn(*args, **kw)
            except Exception as exception:
                future.set_exception(exception)
            else:
                future.set_result(result)

        return wrapped_fn

    if isinstance(gt, gevent.Greenlet):
        # Don't use gevent.Greenlet.__bool__() because since gevent 1.0, a
        # greenlet is True if it already starts, and gevent.spawn() starts
        # the greenlet just after its creation.
        is_running = greenlet.greenlet.__bool__
        if is_running(gt):
            raise RuntimeError("wrap_greenlet: the greenlet is running")

        try:
            gt._run = wrap_fn(gt._run)
        except AttributeError:
            raise RuntimeError(
                "wrap_greenlet: the _run attribute of the greenlet is not set"
            )
    else:
        if gt:
            raise RuntimeError("wrap_greenlet: the greenlet is running")

        try:
            gt.run = wrap_fn(gt.run)
        except AttributeError:
            raise RuntimeError(
                "wrap_greenlet: the run attribute of the greenlet is not set"
            )
    return future
