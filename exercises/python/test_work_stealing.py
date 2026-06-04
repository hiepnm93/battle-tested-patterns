"""Work Stealing — Python Exercise

Implement a work-stealing scheduler where idle workers steal tasks from busy
workers' deques.
Lines marked # TODO: implement are the key logic for learners to delete and rewrite.
"""

from collections import deque


class WorkStealingPool:
    def __init__(self, worker_count: int):
        self._queues: list[deque[int]] = [deque() for _ in range(worker_count)]  # TODO: implement

    def push(self, worker_idx: int, task: int) -> None:  # TODO: implement
        self._queues[worker_idx].append(task)

    def pop(self, worker_idx: int) -> int | None:  # TODO: implement
        """Pop from own queue (LIFO — top of deque)."""
        if self._queues[worker_idx]:
            return self._queues[worker_idx].pop()
        return None

    def steal(self, thief_idx: int) -> int | None:  # TODO: implement
        """Steal from another worker's queue (FIFO — bottom of deque)."""
        for i, q in enumerate(self._queues):
            if i != thief_idx and q:
                return q.popleft()
        return None

    def process(self, worker_idx: int) -> int | None:
        """Try own queue first, then steal from others."""
        result = self.pop(worker_idx)  # TODO: implement
        if result is not None:
            return result
        return self.steal(worker_idx)

    def queue_len(self, worker_idx: int) -> int:
        return len(self._queues[worker_idx])


# ─── Tests (do not modify below this line) ───


def test_own_queue_lifo():
    pool = WorkStealingPool(2)
    pool.push(0, 10)
    pool.push(0, 20)

    item = pool.process(0)
    assert item == 20  # LIFO pop


def test_steal_fifo():
    pool = WorkStealingPool(2)
    pool.push(0, 10)
    pool.push(0, 20)

    # Worker 1 has no work, should steal from worker 0 (FIFO)
    item = pool.process(1)
    assert item == 10  # FIFO steal from bottom


def test_empty_pool():
    pool = WorkStealingPool(3)
    result = pool.process(0)
    assert result is None


def test_steal_all():
    pool = WorkStealingPool(2)
    for i in range(1, 11):
        pool.push(0, i)

    # Worker 1 steals all work
    stolen = []
    while True:
        item = pool.process(1)
        if item is None:
            break
        stolen.append(item)

    assert len(stolen) == 10


def test_mixed_pop_and_steal():
    pool = WorkStealingPool(3)
    pool.push(0, 1)
    pool.push(0, 2)
    pool.push(1, 10)
    pool.push(1, 20)

    # Worker 0 pops its own (LIFO)
    assert pool.process(0) == 2
    # Worker 2 has nothing, steals (FIFO from first non-empty)
    item = pool.process(2)
    assert item is not None


def test_push_and_pop_preserves_order():
    pool = WorkStealingPool(1)
    pool.push(0, 1)
    pool.push(0, 2)
    pool.push(0, 3)

    # LIFO order
    assert pool.pop(0) == 3
    assert pool.pop(0) == 2
    assert pool.pop(0) == 1
    assert pool.pop(0) is None
