"""LSM Tree (Log-Structured Merge Tree) — Python Exercise

Implement an LSM tree with in-memory memtable, flush to sorted runs, and compaction.
Lines marked # TODO: implement are the key logic for learners to delete and rewrite.
"""

from dataclasses import dataclass
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

    def put(self, key: str, value: str, seq: int) -> None:  # TODO: implement
        self._entries[key] = KVEntry(key=key, value=value, seq=seq)
        self._size += 1

    def delete(self, key: str, seq: int) -> None:  # TODO: implement
        self._entries[key] = KVEntry(key=key, value=None, seq=seq)
        self._size += 1

    def get(self, key: str) -> KVEntry | None:  # TODO: implement
        return self._entries.get(key)

    @property
    def size(self) -> int:
        return self._size

    def flush(self) -> list[KVEntry]:  # TODO: implement
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

    def put(self, key: str, value: str) -> None:  # TODO: implement
        self._memtable.put(key, value, self._seq)
        self._seq += 1
        if self._memtable.size >= self._flush_threshold:
            self._flush()

    def delete(self, key: str) -> None:  # TODO: implement
        self._memtable.delete(key, self._seq)
        self._seq += 1
        if self._memtable.size >= self._flush_threshold:
            self._flush()

    def get(self, key: str) -> str | None:  # TODO: implement
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

    def _flush(self) -> None:  # TODO: implement
        run = self._memtable.flush()
        self._runs.insert(0, run)
        if len(self._runs) > self._max_runs:
            self._compact()

    def _compact(self) -> None:  # TODO: implement
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


# ─── Tests (do not modify below this line) ───


def test_put_get():
    tree = LSMTree(flush_threshold=10)
    tree.put("foo", "bar")
    tree.put("baz", "qux")
    assert tree.get("foo") == "bar"
    assert tree.get("baz") == "qux"


def test_auto_flush():
    tree = LSMTree(flush_threshold=3)
    tree.put("a", "1")
    tree.put("b", "2")
    tree.put("c", "3")  # triggers flush
    assert tree.run_count == 1
    # All keys still findable after flush
    assert tree.get("a") == "1"
    assert tree.get("b") == "2"


def test_overwrite():
    tree = LSMTree(flush_threshold=10)
    tree.put("key", "old")
    tree._flush()
    tree.put("key", "new")
    assert tree.get("key") == "new"


def test_missing_key():
    tree = LSMTree(flush_threshold=10)
    tree.put("a", "1")
    assert tree.get("z") is None


def test_delete():
    tree = LSMTree(flush_threshold=10)
    tree.put("a", "1")
    tree.delete("a")
    assert tree.get("a") is None


def test_compaction():
    tree = LSMTree(flush_threshold=2, max_runs=2)
    tree.put("a", "1")
    tree.put("b", "2")  # flush 1
    tree.put("c", "3")
    tree.put("d", "4")  # flush 2
    tree.put("e", "5")
    tree.put("f", "6")  # flush 3 -> triggers compaction
    assert tree.run_count <= 2
    # All keys still accessible
    assert tree.get("a") == "1"
    assert tree.get("d") == "4"
