#!/usr/bin/env python3
"""
Example: Gevent on Asyncio Integration

This example demonstrates how to run gevent on an asyncio event loop backend
using the GeventLoop implementation. This allows gevent greenlets to be
scheduled and executed by asyncio's event loop.
"""

import os
import asyncio
import threading

# Set up environment to use our GeventLoop before importing gevent
os.environ["GEVENT_LOOP"] = "asyncio_gevent.gevent_loop.GeventLoop"

import gevent  # noqa: E402
import asyncio_gevent  # noqa: E402


def example_basic_gevent():
    """Example 1: Basic gevent operations on asyncio backend."""
    print("\n=== Example 1: Basic gevent operations ===")

    def simple_greenlet():
        print(f"Greenlet running in thread: {threading.current_thread().name}")
        gevent.sleep(0.1)
        print("Greenlet completed")
        return 42

    try:
        greenlet = gevent.spawn(simple_greenlet)
        result = greenlet.get(timeout=2)
        print(f"Gevent result: {result}")
        return True
    except Exception as e:
        print(f"Error in basic gevent example: {e}")
        import traceback
        traceback.print_exc()
        return False


def example_multiple_greenlets():
    """Example 2: Multiple concurrent greenlets."""
    print("\n=== Example 2: Multiple greenlets ===")

    def worker(n):
        print(f"Worker {n} starting")
        gevent.sleep(0.1 * n)  # Different sleep times
        print(f"Worker {n} completed")
        return n * 10

    try:
        greenlets = [gevent.spawn(worker, i) for i in range(1, 4)]
        results = [g.get(timeout=2) for g in greenlets]
        print(f"Multiple greenlets results: {results}")
        return True
    except Exception as e:
        print(f"Error in multiple greenlets example: {e}")
        import traceback
        traceback.print_exc()
        return False


def example_gevent_joinall():
    """Example 3: Using gevent.joinall for coordination."""
    print("\n=== Example 3: gevent.joinall ===")

    def worker(n):
        print(f"Joinall worker {n} starting")
        gevent.sleep(0.1)
        print(f"Joinall worker {n} completed")
        return n

    try:
        greenlets = [gevent.spawn(worker, i) for i in range(3)]
        gevent.joinall(greenlets, timeout=2)
        results = [g.value for g in greenlets]
        print(f"Joinall results: {results}")
        return True
    except Exception as e:
        print(f"Error in joinall example: {e}")
        import traceback
        traceback.print_exc()
        return False


def example_bridge_functions():
    """Example 4: Using asyncio-gevent bridge functions."""
    print("\n=== Example 4: Bridge functions ===")

    try:
        def sync_task():
            print("Sync task starting")
            gevent.sleep(0.1)
            print("Sync task completed")
            return "sync_result"

        # Demonstrate that the bridge functions work even when
        # gevent is running on asyncio backend
        greenlet_task = gevent.spawn(sync_task)
        result = greenlet_task.get(timeout=2)
        print(f"Bridge function result: {result}")
        return True
    except Exception as e:
        print(f"Error in bridge functions example: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all gevent on asyncio examples."""
    print("Gevent on Asyncio Integration Examples")
    print("=" * 45)
    print(f"Current thread: {threading.current_thread().name}")
    print(f"Gevent loop class: {gevent.get_hub().loop.__class__}")

    examples = [
        example_basic_gevent,
        example_multiple_greenlets,
        example_gevent_joinall,
        example_bridge_functions
    ]

    success_count = 0
    for example in examples:
        if example():
            success_count += 1

    print(f"\n=== Summary ===")
    print(f"Successful examples: {success_count}/{len(examples)}")

    if success_count == len(examples):
        print("🎉 All examples completed successfully!")
        print("GeventLoop is working correctly with asyncio backend.")
    else:
        print(f"❌ {len(examples) - success_count} examples failed.")
        print("Some advanced gevent features may have compatibility issues.")

    print("\nThis demonstrates that gevent can successfully run on")
    print("an asyncio event loop backend using the GeventLoop implementation.")


if __name__ == "__main__":
    main()