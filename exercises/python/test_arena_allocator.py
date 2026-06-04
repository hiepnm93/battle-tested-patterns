"""Arena Allocator — bump-pointer allocation with bulk free."""


class Arena:
    def __init__(self, capacity: int):
        self.buf = bytearray(capacity)  # TODO: implement
        self.offset = 0  # TODO: implement

    def alloc(self, size: int) -> memoryview | None:
        if self.offset + size > len(self.buf):  # TODO: implement
            return None
        start = self.offset
        self.offset += size
        return memoryview(self.buf)[start:start + size]

    def reset(self) -> None:
        self.offset = 0  # TODO: implement

    @property
    def used(self) -> int:
        return self.offset  # TODO: implement

    @property
    def capacity(self) -> int:
        return len(self.buf)

    @property
    def available(self) -> int:
        return len(self.buf) - self.offset


# ─── Tests (do not modify below this line) ───


def test_arena_alloc():
    a = Arena(64)
    s1 = a.alloc(16)
    assert s1 is not None
    assert len(s1) == 16

    s2 = a.alloc(32)
    assert s2 is not None
    assert len(s2) == 32

    assert a.used == 48


def test_arena_overflow():
    a = Arena(32)
    s1 = a.alloc(16)
    assert s1 is not None

    s2 = a.alloc(20)
    assert s2 is None, "should fail when not enough space"


def test_arena_reset():
    a = Arena(64)
    a.alloc(32)
    a.alloc(16)
    a.reset()

    assert a.used == 0
    assert a.available == 64


def test_arena_disjoint():
    a = Arena(64)
    s1 = a.alloc(8)
    s2 = a.alloc(8)
    assert s1 is not None and s2 is not None

    # Write to s1 shouldn't affect s2
    for i in range(len(s1)):
        s1[i] = 0xFF
    for b in s2:
        assert b == 0, "allocations should be disjoint"
