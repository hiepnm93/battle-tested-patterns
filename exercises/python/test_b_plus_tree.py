# Pattern: B+ Tree
# Difficulty: Intermediate

from __future__ import annotations


class BPlusLeaf:
    def __init__(self):
        self.keys: list[int] = []
        self.values: list[str] = []
        self.next: BPlusLeaf | None = None


class BPlusInternal:
    def __init__(self):
        self.keys: list[int] = []
        self.children: list[BPlusLeaf | BPlusInternal] = []


class BPlusTree:
    def __init__(self, order: int):  # TODO: implement
        self.order = order
        self.root: BPlusLeaf | BPlusInternal = BPlusLeaf()

    def search(self, key: int) -> str | None:  # TODO: implement
        node = self.root
        while isinstance(node, BPlusInternal):
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        leaf: BPlusLeaf = node
        for i, k in enumerate(leaf.keys):
            if k == key:
                return leaf.values[i]
        return None

    def insert(self, key: int, value: str) -> None:  # TODO: implement
        result = self._insert(self.root, key, value)
        if result:
            new_root = BPlusInternal()
            new_root.keys = [result[0]]
            new_root.children = [self.root, result[1]]
            self.root = new_root

    def _insert(self, node, key, value):
        if isinstance(node, BPlusLeaf):
            i = 0
            while i < len(node.keys) and node.keys[i] < key:
                i += 1
            if i < len(node.keys) and node.keys[i] == key:
                node.values[i] = value
                return None
            node.keys.insert(i, key)
            node.values.insert(i, value)
            if len(node.keys) >= self.order:
                return self._split_leaf(node)
            return None

        internal: BPlusInternal = node
        i = 0
        while i < len(internal.keys) and key >= internal.keys[i]:
            i += 1
        result = self._insert(internal.children[i], key, value)
        if result is None:
            return None
        internal.keys.insert(i, result[0])
        internal.children.insert(i + 1, result[1])
        if len(internal.keys) >= self.order:
            return self._split_internal(internal)
        return None

    def _split_leaf(self, leaf: BPlusLeaf):  # TODO: implement
        mid = len(leaf.keys) // 2
        new_leaf = BPlusLeaf()
        new_leaf.keys = leaf.keys[mid:]
        new_leaf.values = leaf.values[mid:]
        leaf.keys = leaf.keys[:mid]
        leaf.values = leaf.values[:mid]
        new_leaf.next = leaf.next
        leaf.next = new_leaf
        return (new_leaf.keys[0], new_leaf)

    def _split_internal(self, node: BPlusInternal):
        mid = len(node.keys) // 2
        promote_key = node.keys[mid]
        new_node = BPlusInternal()
        new_node.keys = node.keys[mid + 1:]
        new_node.children = node.children[mid + 1:]
        node.keys = node.keys[:mid]
        node.children = node.children[:mid + 1]
        return (promote_key, new_node)

    def range_query(self, start: int, end: int) -> list[str]:  # TODO: implement
        node = self.root
        while isinstance(node, BPlusInternal):
            i = 0
            while i < len(node.keys) and start >= node.keys[i]:
                i += 1
            node = node.children[i]
        results: list[str] = []
        leaf: BPlusLeaf | None = node
        while leaf is not None:
            for i, k in enumerate(leaf.keys):
                if k > end:
                    return results
                if k >= start:
                    results.append(leaf.values[i])
            leaf = leaf.next
        return results


# ─── Tests (do not modify below this line) ───

def test_insert_and_search():
    tree = BPlusTree(3)
    tree.insert(5, "five")
    tree.insert(3, "three")
    tree.insert(7, "seven")
    tree.insert(1, "one")
    assert tree.search(3) == "three"
    assert tree.search(99) is None

def test_range_scan():
    tree = BPlusTree(4)
    for i in range(1, 11):
        tree.insert(i, chr(ord("a") + i - 1))
    result = tree.range_query(3, 6)
    assert len(result) == 4

def test_update():
    tree = BPlusTree(3)
    tree.insert(1, "old")
    tree.insert(1, "new")
    assert tree.search(1) == "new"

def test_split():
    tree = BPlusTree(3)
    for i in range(1, 11):
        tree.insert(i, "v")
    for i in range(1, 11):
        assert tree.search(i) is not None, f"key {i} should exist after splits"
