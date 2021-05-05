import gevent.monkey

gevent.monkey.patch_all()
import asyncio

import asyncio_gevent

policy = asyncio_gevent.EventLoopPolicy()
asyncio.set_event_loop_policy(policy)

import threading
import time


async def async_sleep():
    print("async_sleep start", threading.current_thread())
    await asyncio.sleep(1)
    print("async_sleep done", threading.current_thread())


def async_sleep_in_greenlet():
    print("async_sleep_in_greenlet start", threading.current_thread())
    asyncio_gevent.yield_future(asyncio.sleep(1))
    print("async_sleep_in_greenlet done", threading.current_thread())


def gevent_sleep():
    print("gevent_sleep start", threading.current_thread())
    gevent.sleep(1)
    print("gevent_sleep done", threading.current_thread())


async def gevent_sleep_in_async():
    print("gevent_sleep_in_async start", threading.current_thread())
    await asyncio_gevent.wrap_greenlet(gevent.spawn(gevent.sleep, 1))
    print("gevent_sleep_in_async done", threading.current_thread())


async def main():
    await asyncio.gather(
        async_sleep(),
        asyncio_gevent.wrap_greenlet(gevent.spawn(async_sleep_in_greenlet)),
        asyncio_gevent.wrap_greenlet(gevent.spawn(gevent_sleep)),
        gevent_sleep_in_async(),
    )


if __name__ == "__main__":
    asyncio.run(main())
