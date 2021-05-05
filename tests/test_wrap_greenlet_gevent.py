import asyncio
from unittest import mock

import gevent
import pytest

import asyncio_gevent

# from .utils import GeventOnAsyncioTestCase
from .utils import AsyncioOnGeventTestCase, coro_wrap_greenlet


class WrapGreenletGeventTests:
    def test_wrap_greenlet(self):
        def func():
            gevent.sleep(0.010)
            return "ok"

        gt = gevent.spawn(func)
        fut = asyncio_gevent.wrap_greenlet(gt)
        result = self.loop.run_until_complete(fut)
        self.assertEqual(result, "ok")

    def test_wrap_greenlet_exc(self):
        self.loop.set_debug(True)

        def func():
            raise ValueError(7)

        with pytest.raises(ValueError):
            gt = gevent.spawn(func)
            fut = asyncio_gevent.wrap_greenlet(gt)
            self.loop.run_until_complete(fut)

    def test_wrap_greenlet_running(self):
        def func():
            return asyncio_gevent.wrap_greenlet(gt)

        self.loop.set_debug(False)
        gt = gevent.spawn(func)
        msg = "wrap_greenlet: the greenlet is running"
        with pytest.raises(RuntimeError, match=msg):
            gt.get()
        gt.join()

    def test_wrap_greenlet_dead(self):
        def func():
            return "ok"

        gt = gevent.spawn(func)
        result = gt.get()
        self.assertEqual(result, "ok")

        msg = "wrap_greenlet: the greenlet already finished"
        with pytest.raises(RuntimeError, match=msg):
            asyncio_gevent.wrap_greenlet(gt)

    def test_coro_wrap_greenlet(self):
        result = self.loop.run_until_complete(coro_wrap_greenlet())
        self.assertEqual(result, [1, 10, 2, 20, "error", 4])

    def test_wrap_invalid_type(self):
        def func():
            pass

        with pytest.raises(TypeError):
            asyncio_gevent.wrap_greenlet(func)

        async def coro_func():
            pass

        coro_obj = coro_func()
        self.addCleanup(coro_obj.close)

        with pytest.raises(TypeError):
            asyncio_gevent.wrap_greenlet(coro_obj)

    def test_wrap_empty_greenlet(self):
        gl = gevent.spawn()
        future = asyncio_gevent.wrap_greenlet(gl)
        result = self.loop.run_until_complete(future)

        assert result == None
        assert gl.get() == None


class WrapGreenletGeventAsyncioOnGeventTests(
    WrapGreenletGeventTests, AsyncioOnGeventTestCase
):
    pass


# class WrapGreenletGeventGeventOnAsyncioTests(WrapGreenletGeventTests, GeventOnAsyncioTestCase):
#     pass
