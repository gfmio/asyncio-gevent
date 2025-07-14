#!/usr/bin/env python3
"""
Example: Testing GeventLoop Implementation

This example demonstrates the direct usage of the GeventLoop class,
which allows gevent to run on an asyncio event loop backend.
"""

import asyncio
import os
import threading

from asyncio_gevent.sync_to_async import sync_to_async

# Set up environment to use our GeventLoop before importing gevent
os.environ["GEVENT_LOOP"] = "asyncio_gevent.gevent_loop.GeventLoop"

import asyncio_gevent  # noqa: E402


def example_gevent_loop_creation():
    """Example 1: Create and inspect a GeventLoop."""
    print("\n=== Example 1: GeventLoop creation ===")
    try:
        loop = asyncio_gevent.GeventLoop()
        print(f"GeventLoop created successfully: {type(loop)}")
        print(f"Loop format: {loop._format()}")
        return loop
    except Exception as e:
        print(f"Error creating GeventLoop: {e}")
        import traceback

        traceback.print_exc()
        return None


def example_gevent_loop_watchers(loop):
    """Example 2: Create various watchers supported by GeventLoop."""
    print("\n=== Example 2: GeventLoop watchers ===")
    if loop is None:
        print("Skipping watcher examples - no loop available")
        return

    try:
        # Test timer watcher
        timer = loop.timer(1.0)
        print(f"Timer watcher created: {type(timer)}")

        # Test IO watcher (with stdout fd)
        io_watcher = loop.io(1, 2)  # fd=1 (stdout), events=2 (write)
        print(f"IO watcher created: {type(io_watcher)}")

        # Test async watcher
        async_watcher = loop.async_()
        print(f"Async watcher created: {type(async_watcher)}")

        # Test callback
        def dummy_callback():
            print("Callback executed")

        callback = loop.run_callback(dummy_callback)
        print(f"Callback created: {type(callback)}")

    except Exception as e:
        print(f"Error testing watchers: {e}")
        import traceback

        traceback.print_exc()


def example_asyncio_integration(loop):
    """Example 3: Demonstrate asyncio integration."""
    print("\n=== Example 3: Asyncio integration ===")
    if loop is None:
        print("Skipping asyncio examples - no loop available")
        return

    try:
        aio_loop = loop.aio
        print(f"Asyncio loop retrieved: {type(aio_loop)}")
        print(f"Asyncio loop is running: {aio_loop.is_running()}")

        # Test a simple asyncio operation
        async def simple_coro():
            await asyncio.sleep(0.1)
            return "success"

        # Run the coroutine
        result = aio_loop.run_until_complete(simple_coro())
        print(f"Asyncio coroutine result: {result}")

    except Exception as e:
        print(f"Error testing asyncio integration: {e}")
        import traceback

        traceback.print_exc()


def main():
    """Run all GeventLoop examples."""
    print("GeventLoop Implementation Examples")
    print("=" * 40)
    print(f"Current thread: {threading.current_thread().name}")

    loop = example_gevent_loop_creation()
    example_gevent_loop_watchers(loop)
    example_asyncio_integration(loop)

    print("\n=== Summary ===")
    print("These examples demonstrate the GeventLoop implementation")
    print("which allows gevent to use asyncio as its event loop backend.")


if __name__ == "__main__":
    asyncio.run(sync_to_async(main)())
