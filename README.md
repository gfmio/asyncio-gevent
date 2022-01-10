# asyncio-gevent

asyncio-gevent makes asyncio and gevent compatible. It provides utilities for

- running asyncio on gevent (by using gevent as asyncio's event loop)
- running gevent on asyncio (by using asyncio as gevent's event loop, still work in progress)
- converting greenlets to asyncio futures
- converting futures to asyncio greenlets
- wrapping blocking or spawning functions in coroutines which spawn a greenlet and wait for its completion
- wrapping coroutines in spawning functions which block until the future is resolved

asyncio-gevent is a fork and rewrite of `aiogevent` and `tulipcore` for modern python 3.

## Install

Install `asyncio-gevent` from pypi using your favourite package manager.

```sh
# If you use poetry
poetry add asyncio-gevent

# If you use pip
pip install asyncio-gevent
```

## Usage

### Running asyncio on gevent

In order to run `asyncio` on `gevent`, we need to set the (default) `EventLoopPolicy` to use `asyncio_gevent.EventLoopPolicy`.

```py3
import gevent.monkey
gevent.monkey.patch_all()

import asyncio

import asyncio_gevent

asyncio.set_event_loop_policy(asyncio_gevent.EventLoopPolicy())

async def main():
    await asyncio.sleep(1)
    print("done")

asyncio.run(main())
```

After setting the event loop policy, asyncio will use an event loop that uses greenlets for scheduling.

Under the hood, it uses the default selector-based event loop in asyncio with the the gevent selector implementation.

Alternatively, you can also manually set and use the event loop.

```py3
import gevent.monkey
gevent.monkey.patch_all()

import asyncio

import asyncio_gevent

loop = asyncio_gevent.EventLoop()
asyncio.set_event_loop(loop)

async def main():
    await asyncio.sleep(1)
    print("done")

loop.run_until_complete(main())
```

### Running gevent on asyncio

> This implementation is still work-in-progress. It may work for simple examples, but otherwise fail in unexpected ways.

In order to run `gevent` on `asyncio`, `gevent` needs to be initialised to use the asyncio event loop. This is done by setting the environment variable `GEVENT_LOOP` to `asyncio_gevent.gevent_loop.GeventLoop` and then starting python.

```sh
GEVENT_LOOP=asyncio_gevent.gevent_loop.GeventLoop python3 myscript.py
```

gevent will now run on asyncio.

Alternatively, you can also set the loop configuration setting, preferably right after importing `gevent` and before monkey patching.

```py3
import gevent
gevent.config.loop = "asyncio_gevent.gevent_loop.GeventLoop"
```

### Converting greenlets to asyncio futures

Use `asyncio_gevent.greenlet_to_future` to convert a greenlet to an asyncio future. The future yields once the greenlet has finished execution.

```py3
# Preamble: Apply the gevent monkey patch and initialise the asyncio event loop policy

import gevent.monkey
gevent.monkey.patch_all()

import asyncio

import asyncio_gevent

asyncio.set_event_loop_policy(asyncio_gevent.EventLoopPolicy())

# Main example

import gevent

def blocking_function() -> int:
    gevent.sleep(10)
    return 42


async def main() -> None:
    greenlet = gevent.spawn(blocking_function)
    future = asyncio_gevent.greenlet_to_future(greenlet)
    result = await future

asyncio.run(main())
```

If the greenlet is already dead when the future is awaited/scheduled, then the future will resolve with the result or raise the exception thrown immediately.

If the greenlet is not yet running, the greenlet will by default be started when the future is awaited/scheduled. This is to ensure a sensible default behaviour and prevent odd concurrency issues. To prevent this auto-starting, you can pass `autostart_greenlet=False` as an argument to `greenlet_to_future`.

When a greenlet is killed without a custom exception type, it will return a `GreenletExit` exception. In this instance, the future get cancelled. If a custom exception type is used, the future will raise the exception.

If the future gets cancelled, then by default the greenlet is killed. To prevent the greenlet from getting killed, you can pass `autokill_greenlet=False` as an argument to `greenlet_to_future`.

### Converting asyncio futures to greenlets

Use `asyncio_gevent.future_to_greenlet` to convert a future to a greenlet.

```py3
# Preamble: Apply the gevent monkey patch and initialise the asyncio event loop policy

import gevent.monkey
gevent.monkey.patch_all()

import asyncio

import asyncio_gevent

asyncio.set_event_loop_policy(asyncio_gevent.EventLoopPolicy())

# Main example

import gevent

async def async_function() -> int:
    await asyncio.sleep(1)
    return 42


def main() -> None:
    future = async_function()
    greenlet = asyncio_gevent.future_to_greenlet(future)
    greenlet.start()
    greenlet.join()
    assert greenlet.get() == 42

main()
```

The greenlet returned by this function will not start automatically, so you need to call `Greenlet.start()` manually.

If `future` is a coroutine object, it will be scheduled as a task on the `loop` when the greenlet starts. If no `loop` argument has been passed, the running event loop will be used. If there is no running event loop, a new event loop will be started using the current event loop policy.

If the future is not already scheduled, then it won't be scheduled for execution until the greenlet starts running. To prevent the future from being scheduled automatically, you can pass `autostart_future=False` as an argument to `future_to_greenlet`.

If the greenlet gets killed, the by default the future gets cancelled. To prevent this from happening and having the future return the `GreenletExit` objct instead, you can pass `autocancel_future=False` as an argument to `future_to_greenlet`.

If the future gets cancelled, the greenlet gets killed and will return a `GreenletExit`. This default behaviour can be circumvented by passing `autokill_greenlet=False` and the greenlet will raise the `CancelledError` instead.

### Wrapping blocking or spawning functions in coroutines

Use `asyncio_gevent.sync_to_async` to wrap a blocking function or a function that may spawn greenlets and wait for their completion in a coroutine.

```py3
# Preamble: Apply the gevent monkey patch and initialise the asyncio event loop policy

import gevent.monkey
gevent.monkey.patch_all()

import asyncio

import asyncio_gevent

asyncio.set_event_loop_policy(asyncio_gevent.EventLoopPolicy())

# Main example

import gevent

def blocking_function(duration: float):
    gevent.sleep(duration)
    return 42

async_function = asyncio_gevent.sync_to_async(blocking_function)

asyncio.run(async_function(1.0))
```

The returned corountine function will execute the original function in a spawned greenlet and await it's completion.

Under the hood, this is just a thin convenience wrapper around `asyncio_gevent.greenlet_to_future`.

As a result, `asyncio_gevent.sync_to_async` accepts the same arguments as `asyncio_gevent.greenlet_to_future` to achieve the same behaviour.

`asyncio_gevent.sync_to_async` can also be used as a decorator

```py3
# Preamble: Apply the gevent monkey patch and initialise the asyncio event loop policy

import gevent.monkey
gevent.monkey.patch_all()

import asyncio

import asyncio_gevent

asyncio.set_event_loop_policy(asyncio_gevent.EventLoopPolicy())

# Main example

import gevent

@asyncio_gevent.sync_to_async()
def fn(duration: float):
    gevent.sleep(duration)
    return 42

asyncio.run(fn(1.0))
```


### Wrapping coroutines in spawning functions

Use `asyncio_gevent.async_to_sync` to wrap a coroutine function or in a blocking function that spawns a greenlet and waits until the coroutine has returned.

```py3
# Preamble: Apply the gevent monkey patch and initialise the asyncio event loop policy

import gevent.monkey
gevent.monkey.patch_all()

import asyncio

import asyncio_gevent

asyncio.set_event_loop_policy(asyncio_gevent.EventLoopPolicy())

# Main example

import gevent

async def async_function(duration: float):
    await asyncio.sleep(duration)
    return 42

blocking_function = asyncio_gevent.async_to_sync(async_function)

blocking_function(1)
```

The returned function will execute the coroutine on an existing running loop or a new event loop and await it's completion.

Under the hood, this is just a thin convenience wrapper around `asyncio_gevent.future_to_greenlet`.

As a result, `asyncio_gevent.async_to_sync` accepts the same arguments as `asyncio_gevent.future_to_greenlet` to achieve the same behaviour.

`asyncio_gevent.async_to_sync` can also be used as a decorator.


```py3
# Preamble: Apply the gevent monkey patch and initialise the asyncio event loop policy

import gevent.monkey
gevent.monkey.patch_all()

import asyncio

import asyncio_gevent

asyncio.set_event_loop_policy(asyncio_gevent.EventLoopPolicy())

# Main example

import gevent

@asyncio_gevent.async_to_sync
async def fn(duration: float):
    await asyncio.sleep(duration)
    return 42

fn(1)
```

## License

[MIT](LICENSE)
