from dataclasses import dataclass, field
from bisect import bisect_left

@dataclass
class KVEntry:
    key: str
    value: str | None  # None = tombstone
    seq: int = 0

class Memtable:
    def __init__(self):
        self._entries: dict[str, KVEntry] = {}
        self._size = 0

    def put(self, key: str, value: str, seq: int) -> None:
        self._entries[key] = KVEntry(key=key, value=value, seq=seq)
        self._size += 1

    def delete(self, key: str, seq: int) -> None:
        self._entries[key] = KVEntry(key=key, value=None, seq=seq)
        self._size += 1

    def get(self, key: str) -> KVEntry | None:
        return self._entries.get(key)

    @property
    def size(self) -> int:
        return self._size

    def flush(self) -> list[KVEntry]:
        result = sorted(self._entries.values(), key=lambda e: e.key)
        self._entries.clear()
        self._size = 0
        return result

class LSMTree:
    def __init__(self, flush_threshold: int = 4, max_runs: int = 4):
        self._memtable = Memtable()
        self._runs: list[list[KVEntry]] = []
        self._seq = 0
        self._flush_threshold = flush_threshold
        self._max_runs = max_runs

    def put(self, key: str, value: str) -> None:
        self._memtable.put(key, value, self._seq)
        self._seq += 1
        if self._memtable.size >= self._flush_threshold:
            self._flush()

    def delete(self, key: str) -> None:
        self._memtable.delete(key, self._seq)
        self._seq += 1
        if self._memtable.size >= self._flush_threshold:
            self._flush()

    def get(self, key: str) -> str | None:
        entry = self._memtable.get(key)
        if entry is not None:
            return entry.value

        for run in self._runs:
            entry = self._binary_search(run, key)
            if entry is not None:
                return entry.value
        return None

    def _binary_search(self, run: list[KVEntry], key: str) -> KVEntry | None:
        keys = [e.key for e in run]
        i = bisect_left(keys, key)
        if i < len(run) and run[i].key == key:
            return run[i]
        return None

    def _flush(self) -> None:
        run = self._memtable.flush()
        self._runs.insert(0, run)
        if len(self._runs) > self._max_runs:
            self._compact()

    def _compact(self) -> None:
        merged: dict[str, KVEntry] = {}
        for run in reversed(self._runs):
            for entry in run:
                merged[entry.key] = entry
        result = [e for e in merged.values() if e.value is not None]
        result.sort(key=lambda e: e.key)
        self._runs = [result] if result else []

    @property
    def run_count(self) -> int:
        return len(self._runs)
