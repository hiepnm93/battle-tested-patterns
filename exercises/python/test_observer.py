"""Observer / Pub-Sub — decouple producers from consumers via event subscription."""

from collections import defaultdict
from typing import Callable, Any


class EventEmitter:
    def __init__(self):  # TODO: implement
        self._listeners: dict[str, list[Callable]] = defaultdict(list)

    def on(self, event: str, listener: Callable) -> Callable:  # TODO: implement
        self._listeners[event].append(listener)
        return lambda: self._listeners[event].remove(listener)

    def off(self, event: str, listener: Callable) -> None:  # TODO: implement
        try:
            self._listeners[event].remove(listener)
        except ValueError:
            pass

    def emit(self, event: str, data: Any = None) -> None:  # TODO: implement
        for listener in self._listeners[event]:
            listener(data)

    def listener_count(self, event: str) -> int:
        return len(self._listeners[event])


# ─── Tests (do not modify below this line) ───


def test_observer_receives_events():
    emitter = EventEmitter()
    events: list[str] = []
    emitter.on("click", lambda data: events.append(data))
    emitter.emit("click", "click-1")
    emitter.emit("click", "click-2")

    assert len(events) == 2


def test_observer_multiple_subscribers():
    emitter = EventEmitter()
    r1: list[str] = []
    r2: list[str] = []
    emitter.on("resize", lambda data: r1.append(data))
    emitter.on("resize", lambda data: r2.append(data))
    emitter.emit("resize", "100x200")

    assert len(r1) == 1
    assert len(r2) == 1


def test_observer_no_false_notifications():
    emitter = EventEmitter()
    events: list[str] = []
    emitter.on("click", lambda data: events.append(data))
    emitter.emit("scroll", "scrolled")

    assert len(events) == 0, "should not receive events for unsubscribed topics"


def test_observer_unsubscribe():
    emitter = EventEmitter()
    events: list[str] = []
    unsub = emitter.on("message", lambda data: events.append(data))

    emitter.emit("message", "hello")
    unsub()
    emitter.emit("message", "ignored")

    assert events == ["hello"]


def test_observer_off():
    emitter = EventEmitter()
    events: list[str] = []
    listener = lambda data: events.append(data)
    emitter.on("data", listener)
    emitter.emit("data", "a")

    emitter.off("data", listener)
    emitter.emit("data", "b")

    assert events == ["a"]
    assert emitter.listener_count("data") == 0
