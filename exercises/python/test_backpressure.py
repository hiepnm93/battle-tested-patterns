"""Backpressure — bounded queue that rejects when full."""

from collections import deque


class BoundedQueue:
    def __init__(self, capacity: int):
        self._capacity = capacity  # TODO: implement
        self._buf: deque[int] = deque()  # TODO: implement

    def put(self, item: int) -> bool:
        """Add item to queue. Returns False if full (backpressure signal)."""
        if len(self._buf) >= self._capacity:  # TODO: implement
            return False
        self._buf.append(item)
        return True

    def get(self) -> int | None:
        """Remove and return front item, or None if empty."""
        if not self._buf:  # TODO: implement
            return None
        return self._buf.popleft()

    def __len__(self) -> int:
        return len(self._buf)


# ─── Tests (do not modify below this line) ───


def test_backpressure_accepts():
    q = BoundedQueue(3)
    for i in range(3):
        assert q.put(i) is True, f"push {i} should succeed"


def test_backpressure_rejects():
    q = BoundedQueue(2)
    q.put(1)
    q.put(2)
    assert q.put(3) is False, "should reject when full"


def test_backpressure_drain():
    q = BoundedQueue(2)
    q.put(1)
    q.put(2)
    q.get()
    assert q.put(3) is True, "should accept after draining"


def test_backpressure_order():
    q = BoundedQueue(5)
    for i in range(1, 4):
        q.put(i)
    for i in range(1, 4):
        assert q.get() == i
