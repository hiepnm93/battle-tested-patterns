"""Checkpointing pattern — snapshot consistent state for bounded recovery."""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LogEntry:
    id: int
    operation: str
    key: str
    value: Any = None


class CheckpointableStore:  # TODO: implement
    def __init__(self):
        self._state: dict[str, Any] = {}
        self._wal: list[LogEntry] = []
        self._next_id = 1
        self._checkpoint: dict | None = None  # {state, wal_position}

    def apply(self, operation: str, key: str, value: Any = None) -> None:  # TODO: implement
        entry = LogEntry(id=self._next_id, operation=operation, key=key, value=value)
        self._next_id += 1
        self._wal.append(entry)
        self._execute_op(entry)

    def get(self, key: str) -> Any:  # TODO: implement
        return self._state.get(key)

    def take_checkpoint(self) -> None:  # TODO: implement
        self._checkpoint = {
            "state": dict(self._state),
            "wal_position": len(self._wal),
        }

    def simulate_crash(self) -> None:  # TODO: implement
        self._state = {}

    def recover(self) -> int:  # TODO: implement
        if self._checkpoint is not None:
            self._state = dict(self._checkpoint["state"])
            replayed = 0
            for i in range(self._checkpoint["wal_position"], len(self._wal)):
                self._execute_op(self._wal[i])
                replayed += 1
            return replayed
        self._state = {}
        for entry in self._wal:
            self._execute_op(entry)
        return len(self._wal)

    def _execute_op(self, entry: LogEntry) -> None:
        if entry.operation == "SET":
            self._state[entry.key] = entry.value
        elif entry.operation == "DELETE":
            self._state.pop(entry.key, None)

    @property
    def wal_length(self) -> int:
        return len(self._wal)

    @property
    def state_size(self) -> int:
        return len(self._state)


# ─── Tests (do not modify below this line) ───


def test_checkpoint_save_and_restore():
    store = CheckpointableStore()
    store.apply("SET", "a", 10)
    store.apply("SET", "b", 20)
    store.apply("SET", "c", 30)
    store.take_checkpoint()
    store.apply("SET", "d", 40)
    store.apply("SET", "e", 50)

    store.simulate_crash()
    assert store.get("a") is None  # state wiped

    replayed = store.recover()
    assert replayed == 2  # only d and e replayed from checkpoint
    assert store.get("a") == 10
    assert store.get("b") == 20
    assert store.get("c") == 30
    assert store.get("d") == 40
    assert store.get("e") == 50


def test_checkpoint_latest():
    store = CheckpointableStore()
    store.apply("SET", "x", "v1")
    store.apply("SET", "x", "v2")
    store.take_checkpoint()
    store.simulate_crash()
    store.recover()
    assert store.get("x") == "v2"


def test_checkpoint_empty_no_checkpoint():
    store = CheckpointableStore()
    store.apply("SET", "a", 1)
    store.apply("SET", "b", 2)
    store.simulate_crash()
    replayed = store.recover()
    assert replayed == 2  # full WAL replay
    assert store.get("a") == 1
    assert store.get("b") == 2


def test_checkpoint_out_of_bounds():
    """Recovery with no ops after checkpoint replays zero."""
    store = CheckpointableStore()
    store.apply("SET", "a", 1)
    store.take_checkpoint()
    store.simulate_crash()
    replayed = store.recover()
    assert replayed == 0
    assert store.get("a") == 1


def test_checkpoint_delete_operation():
    store = CheckpointableStore()
    store.apply("SET", "a", 1)
    store.apply("SET", "b", 2)
    store.take_checkpoint()
    store.apply("DELETE", "a")

    store.simulate_crash()
    store.recover()
    assert store.get("a") is None
    assert store.get("b") == 2


def test_checkpoint_wal_length():
    store = CheckpointableStore()
    assert store.wal_length == 0
    store.apply("SET", "a", 1)
    store.apply("SET", "b", 2)
    assert store.wal_length == 2
    store.take_checkpoint()
    assert store.wal_length == 2  # checkpoint does not truncate WAL
