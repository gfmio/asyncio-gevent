import asyncio
import sys
import unittest
from unittest import mock

import gevent
import pytest

import asyncio_gevent

from .utils import AsyncioOnGeventTestCase

# from .utils import GeventOnAsyncioTestCase


class GeventTests:
    def test_stop(self):
        def func():
            self.loop.stop()

        gevent.spawn(func).join()
        self.loop.run_forever()

    def test_soon(self):
        result = []

        def func():
            result.append("spawn")
            self.loop.stop()

        gevent.spawn(func).join()
        self.loop.run_forever()
        self.assertEqual(result, ["spawn"])

    def test_soon_spawn(self):
        result = []

        def func1():
            result.append("spawn")

        def func2():
            result.append("spawn_later")
            self.loop.stop()

        def schedule_greenlet():
            gevent.spawn(func1).join()
            gevent.spawn_later(0.010, func2).join()

        self.loop.call_soon(schedule_greenlet)
        self.loop.run_forever()
        self.assertEqual(result, ["spawn", "spawn_later"])


class GeventAsyncioOnGeventTests(GeventTests, AsyncioOnGeventTestCase):
    pass


# class GeventGeventOnAsyncioTests(GeventTests, GeventOnAsyncioTestCase):
#     pass
