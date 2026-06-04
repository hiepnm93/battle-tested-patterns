"""Consistent Hashing — distribute keys on a virtual ring with minimal remapping."""

import bisect


class HashRing:
    def __init__(self, replicas: int = 100):
        self.replicas = replicas  # TODO: implement
        self.ring: dict[int, str] = {}
        self.sorted_keys: list[int] = []

    def _hash(self, key: str) -> int:
        h = 2166136261  # TODO: implement
        for ch in key:
            h ^= ord(ch)
            h = (h * 16777619) & 0xFFFFFFFF
        return h

    def add_node(self, node: str) -> None:
        for i in range(self.replicas):  # TODO: implement
            h = self._hash(f"{node}:{i}")
            self.ring[h] = node
            bisect.insort(self.sorted_keys, h)

    def remove_node(self, node: str) -> None:
        new_keys = []  # TODO: implement
        for k in self.sorted_keys:
            if self.ring.get(k) == node:
                del self.ring[k]
            else:
                new_keys.append(k)
        self.sorted_keys = new_keys

    def get_node(self, key: str) -> str | None:
        if not self.sorted_keys:  # TODO: implement
            return None
        h = self._hash(key)
        idx = bisect.bisect_left(self.sorted_keys, h)
        if idx >= len(self.sorted_keys):
            idx = 0
        return self.ring[self.sorted_keys[idx]]


# ─── Tests (do not modify below this line) ───


def test_hash_ring_basic():
    hr = HashRing(replicas=3)
    hr.add_node("server-a")
    hr.add_node("server-b")
    hr.add_node("server-c")

    node = hr.get_node("my-key")
    assert node is not None and node != "", "should return a node"


def test_hash_ring_consistency():
    hr = HashRing(replicas=50)
    hr.add_node("server-a")
    hr.add_node("server-b")
    hr.add_node("server-c")

    keys = ["user:1", "user:2", "user:3", "session:abc", "order:999"]
    results = {k: hr.get_node(k) for k in keys}

    for k in keys:
        assert hr.get_node(k) == results[k], f"same key {k!r} mapped to different node"


def test_hash_ring_minimal_disruption():
    hr = HashRing(replicas=50)
    hr.add_node("server-a")
    hr.add_node("server-b")

    keys = [f"key-{i}" for i in range(100)]
    before = {k: hr.get_node(k) for k in keys}

    hr.add_node("server-c")
    moved = sum(1 for k in keys if hr.get_node(k) != before[k])

    assert moved < len(keys), "adding a node should not remap all keys"


def test_hash_ring_remove_node():
    hr = HashRing(replicas=10)
    hr.add_node("server-a")
    hr.add_node("server-b")
    hr.remove_node("server-a")

    for k in ["k1", "k2", "k3"]:
        assert hr.get_node(k) == "server-b", \
            "after removing server-a, all keys should go to server-b"
