from dataclasses import dataclass, field
from typing import Any

@dataclass
class LogEntry:
    id: int
    operation: str
    key: str
    value: Any = None

class CheckpointableStore:
    def __init__(self):
        self._state: dict[str, Any] = {}
        self._wal: list[LogEntry] = []
        self._next_id = 1
        self._checkpoint: dict | None = None  # {state, wal_position}

    def apply(self, operation: str, key: str, value: Any = None) -> None:
        entry = LogEntry(id=self._next_id, operation=operation, key=key, value=value)
        self._next_id += 1
        self._wal.append(entry)
        self._execute_op(entry)

    def get(self, key: str) -> Any:
        return self._state.get(key)

    def take_checkpoint(self) -> None:
        self._checkpoint = {
            "state": dict(self._state),
            "wal_position": len(self._wal),
        }

    def simulate_crash(self) -> None:
        self._state = {}

    def recover(self) -> int:
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
