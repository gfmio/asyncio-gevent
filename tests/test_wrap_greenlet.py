import asyncio

import greenlet
import pytest

import asyncio_gevent

from .utils import AsyncioOnGeventTestCase

# from .utils import GeventOnAsyncioTestCase


class WrapGreenletTests:
    def test_wrap_greenlet(self):
        def func(value):
            return value * 3

        gl = greenlet.greenlet(func)
        fut = asyncio_gevent.wrap_greenlet(gl)
        gl.switch(5)
        result = self.loop.run_until_complete(fut)
        assert result == 15

    def test_wrap_greenlet_exc(self):
        def func():
            raise ValueError(7)

        with pytest.raises(ValueError):
            gl = greenlet.greenlet(func)
            fut = asyncio_gevent.wrap_greenlet(gl)
            gl.switch()
            self.loop.run_until_complete(fut)

    def test_wrap_greenlet_no_run_attr(self):
        gl = greenlet.greenlet()
        msg = "wrap_greenlet: the run attribute of the greenlet is not set"
        with pytest.raises(RuntimeError, match=msg):
            asyncio_gevent.wrap_greenlet(gl)

    def test_wrap_greenlet_running(self):
        def func(value):
            gl = greenlet.getcurrent()
            return asyncio_gevent.wrap_greenlet(gl)

        gl = greenlet.greenlet(func)
        msg = "wrap_greenlet: the greenlet is running"

        with pytest.raises(RuntimeError, match=msg):
            gl.switch(5)

    def test_wrap_greenlet_dead(self):
        def func(value):
            return value * 3

        gl = greenlet.greenlet(func)
        gl.switch(5)
        msg = "wrap_greenlet: the greenlet already finished"

        with pytest.raises(RuntimeError, match=msg):
            asyncio_gevent.wrap_greenlet(gl)


class WrapGreenletAsyncioOnGeventTests(WrapGreenletTests, AsyncioOnGeventTestCase):
    pass


# class WrapGreenletGeventOnAsyncioTests(WrapGreenletTests, GeventOnAsyncioTestCase):
#     pass
