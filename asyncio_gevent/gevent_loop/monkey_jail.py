import sys
from types import ModuleType
from typing import Dict

__all__ = ["MonkeyJail"]

_sys_modules: Dict[str, ModuleType] = {}


class MonkeyJail:
    def __init__(self):
        self.saved = {}

    def __enter__(self):
        from gevent import monkey

        # `saved` is a non-public API of `gevent.monkey` that holds all of the
        # original modules that have been patched. Unfortunately, there is no
        # public API to access this information, so we have to rely on this
        # implementation detail. This is the only way to ensure that the
        # original modules are restored correctly after the context manager is
        # exited. This is necessary because `gevent.monkey.patch_all` patches
        # modules in-place, so we need to restore them to their original state
        # after the context manager is exited. This is especially important
        # when running tests, because we need to ensure that the original
        # modules are restored after each test is run.
        saved = getattr(monkey, "saved", {})

        for key in list(saved) + ["selectors"]:
            if key in sys.modules:
                self.saved[key] = sys.modules.pop(key)

        sys.modules.update(_sys_modules)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key in list(self.saved) + ["selectors"]:
            if key in sys.modules:
                _sys_modules[key] = sys.modules[key]

        sys.modules.update(self.saved)
