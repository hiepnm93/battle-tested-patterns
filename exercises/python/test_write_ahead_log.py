"""Write-Ahead Log (WAL) — Python Exercise

Implement a write-ahead log that records mutations before applying them,
enabling crash recovery via log replay.
Lines marked # TODO: implement are the key logic for learners to delete and rewrite.
"""

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class LogEntry:
    id: int
    operation: str
    data: dict[str, Any]
    applied: bool = False


class WAL:
    def __init__(self):
        self._entries: list[LogEntry] = []  # TODO: implement
        self._next_id = 1

    def append(self, operation: str, data: dict[str, Any]) -> int:  # TODO: implement
        entry = LogEntry(id=self._next_id, operation=operation, data=data)
        self._next_id += 1
        self._entries.append(entry)
        return entry.id

    def apply(self, apply_fn: Callable[[LogEntry], None]) -> int:  # TODO: implement
        """Apply only unapplied entries."""
        count = 0
        for entry in self._entries:
            if not entry.applied:
                apply_fn(entry)
                entry.applied = True
                count += 1
        return count

    def recover(self, apply_fn: Callable[[LogEntry], None]) -> int:  # TODO: implement
        """Replay all entries (for crash recovery)."""
        count = 0
        for entry in self._entries:
            apply_fn(entry)
            entry.applied = True
            count += 1
        return count

    def __len__(self) -> int:
        return len(self._entries)


# ─── Tests (do not modify below this line) ───


def test_append_and_recover():
    wal = WAL()
    wal.append("SET", {"key": "x", "value": "1"})
    wal.append("SET", {"key": "y", "value": "2"})

    state = {}

    def apply_fn(entry: LogEntry):
        if entry.operation == "SET":
            state[entry.data["key"]] = entry.data["value"]

    count = wal.recover(apply_fn)
    assert count == 2
    assert state == {"x": "1", "y": "2"}


def test_apply_only_unapplied():
    wal = WAL()
    wal.append("SET", {"key": "x", "value": "1"})
    wal.append("SET", {"key": "y", "value": "2"})

    applied_ops = []

    def apply_fn(entry: LogEntry):
        applied_ops.append(entry.id)

    wal.apply(apply_fn)
    assert applied_ops == [1, 2]

    # Apply again — nothing new
    applied_ops.clear()
    wal.apply(apply_fn)
    assert applied_ops == []


def test_append_after_apply():
    wal = WAL()
    wal.append("SET", {"key": "x", "value": "1"})

    state = {}

    def apply_fn(entry: LogEntry):
        if entry.operation == "SET":
            state[entry.data["key"]] = entry.data["value"]

    wal.apply(apply_fn)
    assert state == {"x": "1"}

    wal.append("SET", {"key": "y", "value": "2"})
    wal.apply(apply_fn)
    assert state == {"x": "1", "y": "2"}


def test_recover_replays_all():
    wal = WAL()
    wal.append("SET", {"key": "x", "value": "1"})

    applied = []
    wal.apply(lambda e: applied.append(e.id))
    assert applied == [1]

    # Recover replays everything, including already-applied
    recovered = []
    wal.recover(lambda e: recovered.append(e.id))
    assert recovered == [1]


def test_sequential_ids():
    wal = WAL()
    id1 = wal.append("SET", {"key": "a", "value": "1"})
    id2 = wal.append("DEL", {"key": "a"})
    id3 = wal.append("SET", {"key": "b", "value": "2"})

    assert id1 == 1
    assert id2 == 2
    assert id3 == 3
    assert len(wal) == 3


def test_delete_operation():
    wal = WAL()
    wal.append("SET", {"key": "x", "value": "1"})
    wal.append("SET", {"key": "y", "value": "2"})
    wal.append("DEL", {"key": "x"})

    state = {}

    def apply_fn(entry: LogEntry):
        if entry.operation == "SET":
            state[entry.data["key"]] = entry.data["value"]
        elif entry.operation == "DEL":
            state.pop(entry.data["key"], None)

    wal.recover(apply_fn)
    assert state == {"y": "2"}
