# Pattern: Ring Buffer
# Difficulty: Basic -> Intermediate


class RingBuffer:
    def __init__(self, capacity: int):  # TODO: implement
        self._buf = [None] * capacity
        self._head = 0
        self._tail = 0
        self._count = 0
        self._cap = capacity

    def enqueue(self, item) -> bool:  # TODO: implement
        if self._count == self._cap:
            return False
        self._buf[self._tail] = item
        self._tail = (self._tail + 1) % self._cap
        self._count += 1
        return True

    def dequeue(self):  # TODO: implement
        if self._count == 0:
            return None
        item = self._buf[self._head]
        self._head = (self._head + 1) % self._cap
        self._count -= 1
        return item

    def is_full(self) -> bool:
        return self._count == self._cap

    def __len__(self) -> int:
        return self._count


# ─── Tests (do not modify below this line) ───

def test_enqueue_dequeue():
    rb = RingBuffer(3)
    assert rb.enqueue(1)
    assert rb.enqueue(2)
    assert rb.enqueue(3)
    assert not rb.enqueue(4)  # full
    for want in [1, 2, 3]:
        assert rb.dequeue() == want

def test_wrap_around():
    rb = RingBuffer(2)
    rb.enqueue("a")
    rb.enqueue("b")
    rb.dequeue()
    rb.enqueue("c")
    assert rb.dequeue() == "b"
    assert rb.dequeue() == "c"

def test_empty_dequeue():
    rb = RingBuffer(4)
    assert len(rb) == 0
    assert rb.dequeue() is None

def test_full_cycle():
    rb = RingBuffer(4)
    for cycle in range(10):
        for i in range(4):
            assert rb.enqueue(cycle * 4 + i)
        assert rb.is_full()
        for i in range(4):
            assert rb.dequeue() == cycle * 4 + i
        assert len(rb) == 0
