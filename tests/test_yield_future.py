import asyncio

import gevent
import pytest

import asyncio_gevent

from .utils import AsyncioOnGeventTestCase, coro_slow_append, greenlet_yield_future

# from .utils import GeventOnAsyncioTestCase


class YieldFutureTests:
    def test_greenlet_yield_future(self):
        result = []
        gt = gevent.spawn(greenlet_yield_future, result, self.loop)
        self.loop.run_forever()
        self.assertEqual(result, [1, 10, 2, 20, "error", 4])

    def test_link_coro(self):
        result = []

        def func():
            value = asyncio_gevent.yield_future(coro_slow_append(result, 3))
            result.append(value)
            self.loop.stop()

        # fut = asyncio.Future(loop=self.loop)
        gevent.spawn(func)
        self.loop.run_forever()
        self.assertEqual(result, [3, 30])

    def test_yield_future_not_running(self):
        result = []

        def func(event, fut):
            event.set()
            value = asyncio_gevent.yield_future(fut)
            result.append(value)
            self.loop.stop()

        event = gevent.event.Event()
        fut = asyncio.Future(loop=self.loop)
        gevent.spawn(func, event, fut)
        event.wait()

        self.loop.call_soon(fut.set_result, 21)
        self.loop.run_forever()
        self.assertEqual(result, [21])

    def test_yield_future_from_loop(self):
        result = []

        def func(fut):
            try:
                value = asyncio_gevent.yield_future(fut)
            except Exception:
                result.append("error")
            else:
                result.append(value)
            self.loop.stop()

        fut = asyncio.Future(loop=self.loop)
        self.loop.call_soon(func, fut)
        self.loop.call_soon(fut.set_result, "unused")
        self.loop.run_forever()
        self.assertEqual(result, ["error"])

    def test_yield_future_invalid_type(self):
        def func(obj):
            return asyncio_gevent.yield_future(obj)

        async def coro_func():
            print("do something")

        def regular_func():
            return 3

        for obj in (coro_func, regular_func):
            with pytest.raises(TypeError):
                gt = gevent.spawn(func, obj)
                gt.get()

    def test_yield_future_wrong_loop(self):
        loop2 = asyncio.new_event_loop()
        self.addCleanup(loop2.close)

        future = asyncio.Future(loop=self.loop)

        async def func(fut: asyncio.Future):
            fut.set_result(42)
            greenlet = asyncio_gevent.yield_future(fut, loop=loop2)
            greenlet.join()

        msg = "The future belongs to a different loop than the one specified as the loop argument"
        with pytest.raises(ValueError, match=msg):
            self.loop.run_until_complete(func(future))


class YieldFutureAsyncioOnGeventTests(YieldFutureTests, AsyncioOnGeventTestCase):
    pass


# class YieldFutureGeventOnAsyncioTests(YieldFutureTests, GeventOnAsyncioTestCase):
#     pass
