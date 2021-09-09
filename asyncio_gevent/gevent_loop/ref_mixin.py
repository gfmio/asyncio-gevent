__all__ = ["RefMixin"]


class RefMixin:
    def __init__(self, loop, ref=True):
        self.loop = loop
        self.ref = ref
        self._ref_increased = False

    def _increase_ref(self):
        if self.ref:
            self._ref_increased = True
            self.loop.increase_ref()

    def _decrease_ref(self):
        if self._ref_increased:
            self._ref_increased = False
            self.loop.decrease_ref()

    def __del__(self):
        self._decrease_ref()
