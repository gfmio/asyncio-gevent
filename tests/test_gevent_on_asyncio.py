import os

# Set environment to use our GeventLoop
os.environ["GEVENT_LOOP"] = "asyncio_gevent.gevent_loop.GeventLoop"

import gevent  # noqa: E402


def test_gevent_on_asyncio_hub_uses_correct_loop():
    """Test that gevent hub uses our GeventLoop."""
    hub = gevent.get_hub()
    assert hub.loop.__class__.__name__ == "GeventLoop"
