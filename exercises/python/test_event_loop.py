"""Event Loop — single-threaded task queue with FIFO dispatch."""

from typing import Callable


class EventLoop:
    def __init__(self) -> None:
        self._queue: list[tuple[str, Callable[[], None]]] = []  # TODO: implement

    def add_task(self, name: str, fn: Callable[[], None]) -> None:
        self._queue.append((name, fn))  # TODO: implement

    def run(self) -> list[str]:
        executed: list[str] = []  # TODO: implement
        while self._queue:
            name, fn = self._queue.pop(0)
            fn()
            executed.append(name)
        return executed

    @property
    def pending(self) -> int:
        return len(self._queue)


# ─── Tests (do not modify below this line) ───


def test_event_loop_order():
    el = EventLoop()
    log: list[int] = []
    el.add_task("a", lambda: log.append(1))
    el.add_task("b", lambda: log.append(2))
    el.add_task("c", lambda: log.append(3))

    names = el.run()
    assert names == ["a", "b", "c"]
    assert log == [1, 2, 3]


def test_event_loop_enqueue_during_run():
    el = EventLoop()
    log: list[str] = []

    def first():
        log.append("first")
        el.add_task("nested", lambda: log.append("nested"))

    el.add_task("first", first)

    el.run()
    assert log == ["first", "nested"]


def test_event_loop_empty():
    el = EventLoop()
    names = el.run()
    assert names == []
