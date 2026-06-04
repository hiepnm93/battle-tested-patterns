"""Object Pool — Python Exercise

Implement an object pool that pre-allocates reusable objects to avoid repeated
allocation on hot paths.
Lines marked # TODO: implement are the key logic for learners to delete and rewrite.
"""

from typing import TypeVar, Callable, List

T = TypeVar("T")


class ObjectPool:
    def __init__(
        self,
        factory: Callable[[], T],
        reset: Callable[[T], None],
        initial: int = 0,
    ):
        self._factory = factory  # TODO: implement
        self._reset = reset
        self._pool: List[T] = [factory() for _ in range(initial)]

    def acquire(self) -> T:  # TODO: implement
        if self._pool:
            return self._pool.pop()
        return self._factory()

    def release(self, obj: T) -> None:  # TODO: implement
        self._reset(obj)
        self._pool.append(obj)

    @property
    def size(self) -> int:
        return len(self._pool)


# ─── Tests (do not modify below this line) ───


def test_acquire_and_release():
    pool = ObjectPool(
        factory=lambda: bytearray(1024),
        reset=lambda buf: None,
        initial=0,
    )
    buf = pool.acquire()
    assert len(buf) == 1024
    buf[0] = 42
    pool.release(buf)
    assert pool.size == 1


def test_reuse():
    create_count = 0

    def factory():
        nonlocal create_count
        create_count += 1
        return {"id": create_count}

    pool = ObjectPool(factory=factory, reset=lambda obj: obj.clear(), initial=0)

    obj1 = pool.acquire()
    obj1_id = obj1["id"]
    pool.release(obj1)

    obj2 = pool.acquire()
    # Should reuse the same object (reset clears it, but it is the same dict)
    assert obj2 is obj1
    assert create_count == 1  # Only one object was ever created


def test_pre_allocated():
    pool = ObjectPool(
        factory=lambda: [0] * 64,
        reset=lambda buf: None,
        initial=5,
    )
    assert pool.size == 5
    obj = pool.acquire()
    assert pool.size == 4
    assert len(obj) == 64


def test_pool_grows_on_demand():
    pool = ObjectPool(
        factory=lambda: {"value": 0},
        reset=lambda obj: obj.update(value=0),
        initial=0,
    )
    assert pool.size == 0
    obj = pool.acquire()
    assert obj == {"value": 0}
    assert pool.size == 0  # Nothing left in pool

    pool.release(obj)
    assert pool.size == 1
