"""Reference Counting — Python Exercise

Implement a RefCounted wrapper that tracks owners via a counter and triggers
cleanup when the count reaches zero.
Lines marked # TODO: implement are the key logic for learners to delete and rewrite.
"""

from typing import TypeVar, Generic, Callable

T = TypeVar("T")


class _RcInner(Generic[T]):
    """Shared inner state for all clones of a RefCounted value."""

    def __init__(self, value: T, cleanup: Callable[[T], None]):
        self.value = value
        self.count = 1
        self.dropped = False
        self.cleanup = cleanup


class RefCounted(Generic[T]):
    def __init__(self, value: T, cleanup: Callable[[T], None]):
        self._inner = _RcInner(value, cleanup)  # TODO: implement
        self._owned = True

    @classmethod
    def _from_inner(cls, inner: _RcInner) -> "RefCounted[T]":
        obj = object.__new__(cls)
        obj._inner = inner
        obj._owned = True
        return obj

    def clone(self) -> "RefCounted[T]":  # TODO: implement
        if not self._owned:
            raise RuntimeError("Cannot clone a dropped reference")
        self._inner.count += 1
        return RefCounted._from_inner(self._inner)

    def drop(self) -> None:  # TODO: implement
        if not self._owned:
            return
        self._owned = False
        self._inner.count -= 1
        if self._inner.count == 0 and not self._inner.dropped:
            self._inner.dropped = True
            self._inner.cleanup(self._inner.value)

    @property
    def strong_count(self) -> int:
        return self._inner.count

    @property
    def value(self) -> T:
        if not self._owned:
            raise RuntimeError("Reference has been dropped")
        return self._inner.value


# ─── Tests (do not modify below this line) ───


def test_basic():
    dropped = []
    rc = RefCounted(42, cleanup=lambda v: dropped.append(v))
    assert rc.value == 42
    assert rc.strong_count == 1
    rc.drop()
    assert dropped == [42]


def test_clone():
    dropped = []
    r1 = RefCounted("hello", cleanup=lambda v: dropped.append(v))
    r2 = r1.clone()

    assert r1.strong_count == 2

    r1.drop()
    assert dropped == []  # Not dropped yet, r2 still holds a ref
    assert r2.strong_count == 1

    r2.drop()
    assert dropped == ["hello"]  # Now cleaned up


def test_multiple_clones():
    dropped = []
    rc = RefCounted(99, cleanup=lambda v: dropped.append(v))
    clones = [rc.clone() for _ in range(5)]
    assert rc.strong_count == 6

    for c in clones:
        c.drop()
    assert dropped == []  # Original still alive
    assert rc.strong_count == 1

    rc.drop()
    assert dropped == [99]


def test_double_drop_is_noop():
    dropped = []
    rc = RefCounted("data", cleanup=lambda v: dropped.append(v))
    rc.drop()
    rc.drop()  # Should be a no-op
    assert dropped == ["data"]  # Cleanup only called once


def test_clone_after_drop_raises():
    rc = RefCounted(1, cleanup=lambda v: None)
    rc.drop()
    try:
        rc.clone()
        assert False, "Should have raised RuntimeError"
    except RuntimeError:
        pass


def test_value_after_drop_raises():
    rc = RefCounted(1, cleanup=lambda v: None)
    rc.drop()
    try:
        _ = rc.value
        assert False, "Should have raised RuntimeError"
    except RuntimeError:
        pass
