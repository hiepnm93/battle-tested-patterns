"""Copy-on-Write — share data until mutation, then copy."""

import copy


class COWList:
    def __init__(self, data: list[int]):
        self._data = list(data)  # TODO: implement
        self._shared = False

    @classmethod
    def _clone(cls, source: "COWList") -> "COWList":
        """Create a shared clone (no copy until write)."""
        cow = cls.__new__(cls)
        cow._data = source._data  # share reference  # TODO: implement
        cow._shared = True
        source._shared = True
        return cow

    def read(self) -> list[int]:
        return self._data  # TODO: implement

    def write(self) -> list[int]:
        if self._shared:  # TODO: implement
            self._data = copy.copy(self._data)
            self._shared = False
        return self._data


# ─── Tests (do not modify below this line) ───


def test_cow_shared_read():
    a = COWList([1, 2, 3])
    b = COWList._clone(a)

    assert a.read()[0] == b.read()[0], "clones should share same data"
    assert a.read() is b.read(), "before write, data reference should be shared"


def test_cow_copy_on_write():
    a = COWList([1, 2, 3])
    b = COWList._clone(a)

    mutable_b = b.write()
    mutable_b[0] = 99

    assert a.read()[0] == 1, "original should be unchanged"
    assert b.read()[0] == 99, "clone should reflect mutation"


def test_cow_no_unnecessary_copy():
    a = COWList([10, 20])
    # sole owner, no clone
    mutable = a.write()
    mutable[0] = 99
    assert a.read()[0] == 99, "should mutate in place when sole owner"
