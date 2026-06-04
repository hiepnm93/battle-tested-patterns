# Pattern: Min Heap
# Difficulty: Basic -> Intermediate


class MinHeap:
    def __init__(self):  # TODO: implement
        self._data: list[int] = []

    def push(self, val: int) -> None:  # TODO: implement
        self._data.append(val)
        self._sift_up(len(self._data) - 1)

    def pop(self) -> int | None:  # TODO: implement
        if not self._data:
            return None
        self._data[0], self._data[-1] = self._data[-1], self._data[0]
        val = self._data.pop()
        if self._data:
            self._sift_down(0)
        return val

    def peek(self) -> int | None:  # TODO: implement
        return self._data[0] if self._data else None

    def __len__(self) -> int:
        return len(self._data)

    def _sift_up(self, i: int) -> None:  # TODO: implement
        while i > 0:
            parent = (i - 1) // 2
            if self._data[i] < self._data[parent]:
                self._data[i], self._data[parent] = self._data[parent], self._data[i]
                i = parent
            else:
                break

    def _sift_down(self, i: int) -> None:  # TODO: implement
        n = len(self._data)
        while True:
            smallest, left, right = i, 2 * i + 1, 2 * i + 2
            if left < n and self._data[left] < self._data[smallest]:
                smallest = left
            if right < n and self._data[right] < self._data[smallest]:
                smallest = right
            if smallest != i:
                self._data[i], self._data[smallest] = self._data[smallest], self._data[i]
                i = smallest
            else:
                break


# ─── Tests (do not modify below this line) ───

def test_push_and_peek():
    h = MinHeap()
    h.push(5)
    h.push(3)
    h.push(7)
    assert h.peek() == 3

def test_pop_order():
    h = MinHeap()
    h.push(5)
    h.push(1)
    h.push(3)
    h.push(2)
    h.push(4)
    expected = [1, 2, 3, 4, 5]
    for want in expected:
        assert h.pop() == want
    assert h.pop() is None

def test_empty_heap():
    h = MinHeap()
    assert len(h) == 0
    assert h.pop() is None
    assert h.peek() is None

def test_peek_does_not_remove():
    h = MinHeap()
    h.push(10)
    h.push(5)
    assert h.peek() == 5
    assert h.peek() == 5
    assert len(h) == 2
