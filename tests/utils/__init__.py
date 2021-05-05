import asyncio
import threading
import unittest

import gevent.monkey

import asyncio_gevent


class AsyncioOnGeventTestCase(unittest.TestCase):
    def setUp(self):
        gevent.monkey.patch_all()
        policy = asyncio_gevent.EventLoopPolicy()
        asyncio.set_event_loop_policy(policy)
        self.addCleanup(asyncio.set_event_loop_policy, None)
        self.loop = policy.get_event_loop()
        self.addCleanup(self.loop.close)
        self.addCleanup(asyncio.set_event_loop, None)


# class GeventOnAsyncioTestCase(unittest.TestCase):
#     def setUp(self):
#         old_value = gevent.config.settings.get("loop")
#         gevent.config.set("loop", "asyncio_gevent.gevent_loop.GeventLoop")
#         gevent.monkey.patch_all()
#         self.addCleanup(gevent.config.set, "loop", old_value)
#         self.loop = asyncio.get_event_loop()
#         self.addCleanup(self.loop.close)


SHORT_SLEEP = 0.001


def gevent_slow_append(result, value, delay):
    gevent.sleep(delay)
    result.append(value)
    return value * 10


def gevent_slow_error():
    gevent.sleep(SHORT_SLEEP)
    raise ValueError("error")


async def coro_wrap_greenlet():
    result = []

    gt = gevent.spawn(gevent_slow_append, result, 1, 0.002)
    value = await asyncio_gevent.wrap_greenlet(gt)
    result.append(value)

    gt = gevent.spawn(gevent_slow_append, result, 2, 0.001)
    value = await asyncio_gevent.wrap_greenlet(gt)
    result.append(value)

    gt = gevent.spawn(gevent_slow_error)
    try:
        await asyncio_gevent.wrap_greenlet(gt)
    except ValueError as exc:
        result.append(str(exc))

    result.append(4)
    return result


async def coro_slow_append(result, value, delay=SHORT_SLEEP):
    await asyncio.sleep(delay)
    result.append(value)
    return value * 10


async def coro_slow_error():
    await asyncio.sleep(0.001)
    raise ValueError("error")


def greenlet_yield_future(result, loop):
    try:
        value = asyncio_gevent.yield_future(coro_slow_append(result, 1, 0.002), loop)
        result.append(value)

        value = asyncio_gevent.yield_future(coro_slow_append(result, 2, 0.001), loop)
        result.append(value)

        try:
            value = asyncio_gevent.yield_future(coro_slow_error())
        except ValueError as exc:
            result.append(str(exc))

        result.append(4)
        return result
    except Exception as exc:
        result.append(repr(exc))
    finally:
        loop.stop()
