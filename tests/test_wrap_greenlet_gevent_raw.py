import asyncio

import gevent
import pytest

import asyncio_gevent

from .utils import AsyncioOnGeventTestCase

# from .utils import GeventOnAsyncioTestCase


class WrapGreenletRawTests:
    def test_wrap_greenlet(self):
        def func():
            gevent.sleep(0.010)
            return "ok"

        gt = gevent.spawn_raw(func)
        fut = asyncio_gevent.wrap_greenlet(gt)
        result = self.loop.run_until_complete(fut)
        assert result == "ok"

    def test_wrap_greenlet_exc(self):
        self.loop.set_debug(True)

        def func():
            raise ValueError(7)

        gt = gevent.spawn_raw(func)
        fut = asyncio_gevent.wrap_greenlet(gt)

        with pytest.raises(ValueError):
            self.loop.run_until_complete(fut)

    def test_wrap_greenlet_running(self):
        msg = "wrap_greenlet: the greenlet is running"

        def func():
            pass

        with pytest.raises(RuntimeError, match=msg):
            gt = gevent.getcurrent()
            fut = asyncio_gevent.wrap_greenlet(gt)
            gevent.spawn_raw(func)

    def test_wrap_greenlet_dead(self):
        def func():
            pass

        gt = gevent.spawn_raw(func)
        gevent.sleep(0)

        msg = "wrap_greenlet: the greenlet already finished"
        with pytest.raises(RuntimeError, match=msg):
            asyncio_gevent.wrap_greenlet(gt)


class WrapGreenletRawAsyncioOnGeventTests(
    WrapGreenletRawTests, AsyncioOnGeventTestCase
):
    pass


# class WrapGreenletRawGeventOnAsyncioTests(WrapGreenletRawTests, GeventOnAsyncioTestCase):
#     pass
