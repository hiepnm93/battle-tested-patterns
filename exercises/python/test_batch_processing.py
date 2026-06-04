"""Batch Processing — accumulate items and flush as a group."""

from typing import Any


class Batcher:
    def __init__(self, size: int):
        self._size = size  # TODO: implement
        self._buffer: list[Any] = []  # TODO: implement
        self._batches: list[list[Any]] = []

    def add(self, item: Any) -> None:
        self._buffer.append(item)  # TODO: implement
        if len(self._buffer) >= self._size:
            self.flush()

    def flush(self) -> None:
        if not self._buffer:  # TODO: implement
            return
        self._batches.append(list(self._buffer))
        self._buffer.clear()

    @property
    def batches(self) -> list[list[Any]]:
        return self._batches  # TODO: implement


# ─── Tests (do not modify below this line) ───


def test_batch_auto_flush():
    b = Batcher(3)
    for i in range(1, 7):
        b.add(i)

    assert len(b.batches) == 2
    assert len(b.batches[0]) == 3
    assert b.batches[0][0] == 1


def test_batch_manual_flush():
    b = Batcher(10)
    b.add("a")
    b.add("b")
    b.flush()

    assert len(b.batches) == 1
    assert len(b.batches[0]) == 2


def test_batch_empty_flush():
    b = Batcher(5)
    b.flush()
    assert len(b.batches) == 0, "flushing empty buffer should produce no batch"


def test_batch_partial_and_full():
    b = Batcher(3)
    for i in range(1, 8):
        b.add(i)
    b.flush()  # flush remaining [7]

    assert len(b.batches) == 3
    assert len(b.batches[2]) == 1, "last batch should have 1 item"
