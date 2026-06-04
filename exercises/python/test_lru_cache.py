# Pattern: LRU Cache
# Difficulty: Basic -> Intermediate

from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity: int):  # TODO: implement
        self.capacity = capacity
        self.cache: OrderedDict[str, object] = OrderedDict()

    def get(self, key: str):  # TODO: implement
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: str, value: object) -> None:  # TODO: implement
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)


# ─── Tests (do not modify below this line) ───

def test_basic_get_put():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert c.get("a") == 1
    c.put("c", 3)  # evicts "b"
    assert c.get("b") is None

def test_update_existing_key():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("a", 10)  # update, promotes "a"
    c.put("c", 3)   # evicts "b" (LRU)
    assert c.get("a") == 10
    assert c.get("b") is None

def test_access_reorders():
    c = LRUCache(3)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    c.get("a")      # promotes "a"
    c.put("d", 4)   # evicts "b" (LRU)
    assert c.get("b") is None
    assert c.get("a") == 1

def test_get_nonexistent():
    c = LRUCache(2)
    assert c.get("missing") is None
    c.put("a", 1)
    assert c.get("missing") is None

def test_capacity_one():
    c = LRUCache(1)
    c.put("a", 1)
    assert c.get("a") == 1
    c.put("b", 2)
    assert c.get("a") is None
    assert c.get("b") == 2

def test_eviction_order():
    c = LRUCache(3)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    c.put("d", 4)   # evicts "a" (oldest)
    assert c.get("a") is None
    assert c.get("b") == 2
    assert c.get("c") == 3
    assert c.get("d") == 4
