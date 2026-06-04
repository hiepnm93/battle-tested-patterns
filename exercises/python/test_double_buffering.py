"""Double Buffering pattern — maintain two copies and swap atomically."""


class DoubleBuffer:  # TODO: implement
    def __init__(self, create_buffer):
        self._buffers = [create_buffer(), create_buffer()]
        self._current = 0

    def current(self):  # TODO: implement
        return self._buffers[self._current]

    def next(self):  # TODO: implement
        return self._buffers[1 - self._current]

    def swap(self):  # TODO: implement
        self._current = 1 - self._current


# ─── Tests (do not modify below this line) ───


def test_swap():
    buf = DoubleBuffer(lambda: {"pixels": [0, 0]})
    buf.next()["pixels"] = [255, 128]
    assert buf.current()["pixels"] == [0, 0]  # front unchanged
    buf.swap()
    assert buf.current()["pixels"] == [255, 128]  # now visible


def test_independence():
    buf = DoubleBuffer(lambda: [0, 0, 0, 0])
    buf.next()[0] = 99
    assert buf.current()[0] == 0, "Front and back should be independent before swap"


def test_multiple_swaps():
    buf = DoubleBuffer(lambda: [0, 0])
    buf.next()[0] = 1
    buf.swap()
    buf.next()[0] = 2
    buf.swap()
    assert buf.current()[0] == 2


def test_back_buffer_recycled():
    buf = DoubleBuffer(lambda: {"data": None})
    buf.next()["data"] = "frame1"
    buf.swap()
    # old front (now back) should be the original buffer
    buf.next()["data"] = "frame2"
    buf.swap()
    assert buf.current()["data"] == "frame2"


def test_swap_does_not_copy():
    """Swap should reuse the same buffer objects, not create new ones."""
    buf = DoubleBuffer(lambda: [0])
    front_before = buf.current()
    back_before = buf.next()
    buf.swap()
    assert buf.current() is back_before
    assert buf.next() is front_before
