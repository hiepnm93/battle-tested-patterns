"""Actor Model — each actor has a mailbox and processes messages sequentially."""

from collections import deque
from typing import Any, Callable


class Actor:
    def __init__(self, initial_state: Any, handler: Callable[[Any, Any], Any]):
        self.state = initial_state  # TODO: implement
        self.handler = handler  # TODO: implement
        self._mailbox: deque[Any] = deque()  # TODO: implement
        self._processing = False

    def send(self, msg: Any) -> None:
        self._mailbox.append(msg)  # TODO: implement
        if not self._processing:
            self._process_mailbox()

    def _process_mailbox(self) -> None:
        self._processing = True  # TODO: implement
        while self._mailbox:
            msg = self._mailbox.popleft()
            self.state = self.handler(self.state, msg)
        self._processing = False

    def get_state(self) -> Any:
        return self.state  # TODO: implement


# ─── Tests (do not modify below this line) ───


def test_actor_processes_messages():
    def handler(state, msg):
        if msg["type"] == "add":
            return state + msg["payload"]
        return state

    a = Actor(0, handler)
    a.send({"type": "add", "payload": 10})
    a.send({"type": "add", "payload": 20})

    assert a.get_state() == 30


def test_actor_reset():
    def handler(state, msg):
        if msg["type"] == "add":
            return state + msg["payload"]
        elif msg["type"] == "reset":
            return 0
        return state

    a = Actor(0, handler)
    a.send({"type": "add", "payload": 100})
    a.send({"type": "reset", "payload": 0})
    a.send({"type": "add", "payload": 5})

    assert a.get_state() == 5


def test_actor_multiple_senders():
    def handler(state, msg):
        if msg["type"] == "add":
            return state + msg["payload"]
        return state

    a = Actor(0, handler)
    for i in range(100):
        a.send({"type": "add", "payload": 1})

    assert a.get_state() == 100


def test_actor_isolation():
    """Two actors with the same handler maintain independent state."""
    def handler(state, msg):
        return state + msg

    a = Actor(0, handler)
    b = Actor(0, handler)

    a.send(10)
    a.send(20)
    b.send(5)

    assert a.get_state() == 30
    assert b.get_state() == 5
