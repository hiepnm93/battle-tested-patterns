"""Dirty Flag pattern — defer expensive recomputation until the value is actually needed."""
from typing import TypeVar, Generic, Callable

T = TypeVar("T")


class DirtyFlag(Generic[T]):  # TODO: implement
    def __init__(self, compute: Callable[[], T]):
        self._compute = compute
        self._dirty = True
        self._cached: T | None = None

    def mark_dirty(self) -> None:  # TODO: implement
        self._dirty = True

    def get(self) -> T:  # TODO: implement
        if self._dirty:
            self._cached = self._compute()
            self._dirty = False
        return self._cached  # type: ignore

    @property
    def is_dirty(self) -> bool:  # TODO: implement
        return self._dirty


# ─── Tests (do not modify below this line) ───


def test_initially_dirty():
    counter = {"calls": 0}

    def compute():
        counter["calls"] += 1
        return 42

    d = DirtyFlag(compute)
    assert d.is_dirty


def test_cleared_after_compute():
    d = DirtyFlag(lambda: 42)
    d.get()
    assert not d.is_dirty


def test_dirty_after_mark():
    d = DirtyFlag(lambda: 42)
    d.get()
    d.mark_dirty()
    assert d.is_dirty


def test_cache_reuse():
    counter = {"calls": 0}

    def compute():
        counter["calls"] += 1
        return 99

    d = DirtyFlag(compute)
    r1 = d.get()
    r2 = d.get()
    assert r1 == r2 == 99
    assert counter["calls"] == 1  # computed only once


def test_recompute_after_dirty():
    value = {"v": 10}

    def compute():
        return value["v"]

    d = DirtyFlag(compute)
    assert d.get() == 10

    value["v"] = 20
    d.mark_dirty()
    assert d.get() == 20


def test_multiple_dirty_cycles():
    counter = {"calls": 0}

    def compute():
        counter["calls"] += 1
        return counter["calls"]

    d = DirtyFlag(compute)
    assert d.get() == 1
    d.mark_dirty()
    d.mark_dirty()  # multiple marks still single recompute
    assert d.get() == 2
    assert counter["calls"] == 2
