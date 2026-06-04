# Pattern: Skip List
# Difficulty: Intermediate

import random


class SkipNode:
    def __init__(self, key: int, value: str, level: int):
        self.key = key
        self.value = value
        self.forward: list["SkipNode | None"] = [None] * (level + 1)


class SkipList:
    def __init__(self, max_level: int = 16, p: float = 0.5):  # TODO: implement
        self.max_level = max_level
        self.p = p
        self.level = 0
        self.header = SkipNode(-1, "", max_level)

    def _random_level(self) -> int:  # TODO: implement
        lvl = 0
        while lvl < self.max_level and random.random() < self.p:
            lvl += 1
        return lvl

    def insert(self, key: int, value: str) -> None:  # TODO: implement
        update = [self.header] * (self.max_level + 1)
        cur = self.header
        for i in range(self.level, -1, -1):
            while cur.forward[i] and cur.forward[i].key < key:
                cur = cur.forward[i]
            update[i] = cur
        if cur.forward[0] and cur.forward[0].key == key:
            cur.forward[0].value = value
            return
        lvl = self._random_level()
        if lvl > self.level:
            for i in range(self.level + 1, lvl + 1):
                update[i] = self.header
            self.level = lvl
        node = SkipNode(key, value, lvl)
        for i in range(lvl + 1):
            node.forward[i] = update[i].forward[i]
            update[i].forward[i] = node

    def search(self, key: int) -> str | None:  # TODO: implement
        cur = self.header
        for i in range(self.level, -1, -1):
            while cur.forward[i] and cur.forward[i].key < key:
                cur = cur.forward[i]
        if cur.forward[0] and cur.forward[0].key == key:
            return cur.forward[0].value
        return None

    def delete(self, key: int) -> bool:  # TODO: implement
        update = [self.header] * (self.max_level + 1)
        cur = self.header
        for i in range(self.level, -1, -1):
            while cur.forward[i] and cur.forward[i].key < key:
                cur = cur.forward[i]
            update[i] = cur
        target = cur.forward[0]
        if target is None or target.key != key:
            return False
        for i in range(self.level + 1):
            if update[i].forward[i] != target:
                break
            update[i].forward[i] = target.forward[i]
        while self.level > 0 and self.header.forward[self.level] is None:
            self.level -= 1
        return True


# ─── Tests (do not modify below this line) ───

def test_insert_and_search():
    sl = SkipList()
    sl.insert(3, "three")
    sl.insert(1, "one")
    sl.insert(2, "two")
    assert sl.search(2) == "two"
    assert sl.search(99) is None

def test_delete():
    sl = SkipList()
    sl.insert(1, "one")
    sl.insert(2, "two")
    sl.insert(3, "three")
    assert sl.delete(2)
    assert sl.search(2) is None
    assert sl.search(1) == "one"

def test_update():
    sl = SkipList()
    sl.insert(1, "old")
    sl.insert(1, "new")
    assert sl.search(1) == "new"

def test_ordering():
    sl = SkipList()
    for k in [50, 10, 30, 20, 40]:
        sl.insert(k, "")
    keys = []
    cur = sl.header.forward[0]
    while cur is not None:
        keys.append(cur.key)
        cur = cur.forward[0]
    assert keys == sorted(keys)
