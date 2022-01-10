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

        for key in list(monkey.saved) + ["selectors"]:
            if key in sys.modules:
                self.saved[key] = sys.modules.pop(key)
        sys.modules.update(_sys_modules)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key in list(self.saved) + ["selectors"]:
            if key in sys.modules:
                _sys_modules[key] = sys.modules[key]
        sys.modules.update(self.saved)
