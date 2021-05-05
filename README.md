# asyncio-gevent

asyncio-gevent makes asyncio and gevent compatible. It provides utilities for

- running gevent on asyncio (by using asyncio as gevent's event loop, work in progress)
- running asyncio on gevent (by using gevent as asyncio's event loop)
- converting greenlets to asyncio futures
- converting futures to asyncio greenlets

asyncio-gevent is a fork and complete rewrite of `aiogevent` and `tulipcore` for modern python 3.

## Install

Install `asyncio-gevent` from pypi using your favourite package manager.

```sh
# If you use poetry
poetry add asyncio-gevent

# If you use pip
pip install asyncio-gevent
```

## Usage

### Running gevent on asyncio

In order to run `gevent` on `asyncio`, `gevent` needs to be initialised to use the asyncio event loop. This is done by setting the environment variable `GEVENT_LOOP` to `asyncio_gevent.gevent_loop.GeventLoop` and then starting python.

```sh
GEVENT_LOOP=asyncio_gevent.gevent_loop.GeventLoop python3 myscript.py
```

gevent will now run on asyncio.

Alternatively, you can also set the loop configuration setting, preferably right after importing `gevent` and before monkey patching.

```py3
import gevent
gevent.config.loop = "asyncio_gevent"
```

### Running asyncio on gevent

In order to run `asyncio` on `gevent`, we need to set the (default) `EventLoopPolicy` to use `asyncio_gevent.EventLoopPolicy`.

```py3
import gevent.monkey
gevent.monkey.patch_all()

import asyncio

import asyncio_gevent

asyncio.set_default_event_loop_policy(asyncio_gevent.EventLoopPolicy)
```

### Converting greenlets to asyncio futures

Use `asyncio_gevent.wrap_greenlet` to convert a greenlet to an asyncio future. The future yields once the greenlet has finished execution.

```py3
# The following assumes that the gevent/asyncio bindings have already been initialised
import gevent

import asyncio

import asyncio_gevent


def blocking_function() -> int:
    gevent.sleep(10)
    return 42


async def main() -> None:
    greenlet = gevent.spawn(blocking_function)
    future = asyncio_gevent.wrap_greenlet()
    result = await future


asyncio.run(main())
```

### Converting asyncio futures to greenlets

Use `asyncio_gevent.yield_future` to convert a future to a greenlet.

```py3
# The following assumes that the gevent/asyncio bindings have already been initialised

import gevent

import asyncio

import asyncio_gevent


async def async_function() -> int:
    await asyncio.sleep(10)
    return 42


def main() -> None:
    future = async_function()
    greenlet = asyncio_gevent.yield_future(future)
    greenlet.join()

main()
```

## License

[MIT](LICENSE)
