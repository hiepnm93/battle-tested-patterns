"""Tombstone / Deferred Deletion — Python Exercise

Implement a key-value store that uses tombstone markers for deletion and
a compact operation to reclaim space.
Lines marked # TODO: implement are the key logic for learners to delete and rewrite.
"""

import time


class TombstoneMap:
    def __init__(self):
        self._store: dict[str, dict] = {}  # TODO: implement
        self._tombstone_count = 0

    def put(self, key: str, value: str) -> None:  # TODO: implement
        self._store[key] = {
            "value": value,
            "deleted": False,
            "timestamp": time.time() * 1000,
        }

    def get(self, key: str) -> str | None:  # TODO: implement
        entry = self._store.get(key)
        if entry is None or entry["deleted"]:
            return None
        return entry["value"]

    def delete(self, key: str) -> bool:  # TODO: implement
        entry = self._store.get(key)
        if entry is None or entry["deleted"]:
            return False
        entry["deleted"] = True
        entry["value"] = None
        entry["timestamp"] = time.time() * 1000
        self._tombstone_count += 1
        return True

    def compact(self, max_age_ms: float = 0) -> int:  # TODO: implement
        cutoff = time.time() * 1000 - max_age_ms
        to_remove = [
            k
            for k, e in self._store.items()
            if e["deleted"] and e["timestamp"] < cutoff
        ]
        for k in to_remove:
            del self._store[k]
        self._tombstone_count -= len(to_remove)
        return len(to_remove)

    @property
    def size(self) -> int:
        return sum(1 for e in self._store.values() if not e["deleted"])

    @property
    def pending_tombstones(self) -> int:
        return self._tombstone_count


# ─── Tests (do not modify below this line) ───


def test_put_get():
    store = TombstoneMap()
    store.put("a", "1")
    assert store.get("a") == "1"


def test_delete():
    store = TombstoneMap()
    store.put("a", "1")
    result = store.delete("a")

    assert result is True
    assert store.get("a") is None
    assert store.pending_tombstones == 1


def test_delete_nonexistent():
    store = TombstoneMap()
    result = store.delete("z")
    assert result is False


def test_reinsert_after_delete():
    store = TombstoneMap()
    store.put("a", "1")
    store.delete("a")
    store.put("a", "2")

    assert store.get("a") == "2"


def test_compact():
    store = TombstoneMap()
    store.put("a", "1")
    store.put("b", "2")
    store.delete("a")

    # Sleep briefly so tombstone timestamp is old enough
    time.sleep(0.01)

    removed = store.compact(max_age_ms=5)
    assert removed == 1
    assert store.get("b") == "2"
    assert store.size == 1
    assert store.pending_tombstones == 0


def test_size():
    store = TombstoneMap()
    store.put("a", "1")
    store.put("b", "2")
    store.put("c", "3")
    assert store.size == 3

    store.delete("b")
    assert store.size == 2


def test_compact_respects_age():
    store = TombstoneMap()
    store.put("a", "1")
    store.delete("a")

    # Compact with a very large max_age — tombstone is too recent
    removed = store.compact(max_age_ms=999_999_999)
    assert removed == 0
    assert store.pending_tombstones == 1
