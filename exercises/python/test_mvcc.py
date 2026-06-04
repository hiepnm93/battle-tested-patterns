"""MVCC (Multi-Version Concurrency Control) — Python Exercise

Implement an MVCC store where each write creates a new version and readers see
a consistent snapshot based on their timestamp.
Lines marked # TODO: implement are the key logic for learners to delete and rewrite.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class Version:
    timestamp: int
    value: Any
    deleted: bool = False


class MVCCStore:
    def __init__(self):
        self._data: dict[str, list[Version]] = {}
        self._clock = 0

    def put(self, key: str, value: Any) -> int:  # TODO: implement
        self._clock += 1
        self._data.setdefault(key, []).append(Version(self._clock, value))
        return self._clock

    def get(self, key: str, timestamp: int) -> Any:  # TODO: implement
        versions = self._data.get(key, [])
        best = None
        for v in versions:
            if v.timestamp <= timestamp and (best is None or v.timestamp > best.timestamp):
                best = v
        if best is None or best.deleted:
            return None
        return best.value

    def delete(self, key: str) -> int:  # TODO: implement
        self._clock += 1
        self._data.setdefault(key, []).append(
            Version(self._clock, None, deleted=True)
        )
        return self._clock

    @property
    def clock(self) -> int:
        return self._clock


# ─── Tests (do not modify below this line) ───


def test_basic_put_get():
    store = MVCCStore()
    ts = store.put("key", "v1")
    assert store.get("key", ts) == "v1"


def test_time_travel():
    store = MVCCStore()
    ts1 = store.put("key", "v1")
    ts2 = store.put("key", "v2")
    _ts3 = store.put("key", "v3")

    assert store.get("key", ts1) == "v1"
    assert store.get("key", ts2) == "v2"


def test_delete():
    store = MVCCStore()
    ts1 = store.put("key", "alive")
    ts_del = store.delete("key")

    assert store.get("key", ts_del) is None
    assert store.get("key", ts1) == "alive"


def test_future_read():
    store = MVCCStore()
    store.put("key", "v1")
    # Reading at timestamp 0 (before any write) should return None
    assert store.get("key", 0) is None


def test_multiple_keys():
    store = MVCCStore()
    ts_a = store.put("a", "100")
    ts_b = store.put("b", "200")
    assert store.get("a", ts_a) == "100"
    assert store.get("b", ts_b) == "200"
    assert store.get("a", ts_b) == "100"  # a still visible at later timestamp


def test_overwrite_then_read_old():
    store = MVCCStore()
    ts1 = store.put("balance", 500)
    ts2 = store.put("balance", 450)

    assert store.get("balance", ts1) == 500
    assert store.get("balance", ts2) == 450
