"""Free List pattern — O(1) alloc and free with slot reuse."""


class FreeList:  # TODO: implement
    def __init__(self, capacity: int):
        self.capacity = capacity
        self._next_slot = 0
        self._free: list[int] = []

    def alloc(self) -> int | None:  # TODO: implement
        if self._free:
            return self._free.pop()
        if self._next_slot >= self.capacity:
            return None
        slot = self._next_slot
        self._next_slot += 1
        return slot

    def free(self, slot: int) -> None:  # TODO: implement
        self._free.append(slot)

    @property
    def available(self) -> int:  # TODO: implement
        return len(self._free) + (self.capacity - self._next_slot)

    @property
    def allocated(self) -> int:  # TODO: implement
        return self._next_slot - len(self._free)


# ─── Tests (do not modify below this line) ───


def test_alloc_and_free():
    fl = FreeList(4)
    assert fl.available == 4

    s1 = fl.alloc()
    assert s1 is not None
    assert fl.available == 3
    assert fl.allocated == 1


def test_exhaustion():
    fl = FreeList(2)
    fl.alloc()
    fl.alloc()
    assert fl.alloc() is None, "Should return None when exhausted"


def test_reuse():
    fl = FreeList(2)
    s1 = fl.alloc()
    assert s1 is not None
    fl.free(s1)
    s2 = fl.alloc()
    assert s2 is not None, "Should reuse freed slot"


def test_all_alloc_and_free():
    fl = FreeList(8)
    slots = []
    for _ in range(8):
        s = fl.alloc()
        assert s is not None
        slots.append(s)

    assert fl.available == 0
    assert fl.allocated == 8

    for s in slots:
        fl.free(s)

    assert fl.available == 8
    assert fl.allocated == 0


def test_allocated_count():
    fl = FreeList(4)
    assert fl.allocated == 0
    s1 = fl.alloc()
    s2 = fl.alloc()
    assert fl.allocated == 2
    fl.free(s1)
    assert fl.allocated == 1
    fl.free(s2)
    assert fl.allocated == 0
