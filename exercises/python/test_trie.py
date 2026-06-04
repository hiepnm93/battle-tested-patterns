# Pattern: Trie
# Difficulty: Basic -> Intermediate


class TrieNode:
    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.is_end = False


class Trie:
    def __init__(self):  # TODO: implement
        self.root = TrieNode()

    def insert(self, word: str) -> None:  # TODO: implement
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:  # TODO: implement
        node = self._find(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:  # TODO: implement
        return self._find(prefix) is not None

    def _find(self, s: str) -> TrieNode | None:
        node = self.root
        for ch in s:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def auto_complete(self, prefix: str) -> list[str]:  # TODO: implement
        node = self._find(prefix)
        if node is None:
            return []
        results: list[str] = []
        self._collect(node, prefix, results)
        return sorted(results)

    def _collect(self, node: TrieNode, prefix: str, results: list[str]) -> None:
        if node.is_end:
            results.append(prefix)
        for ch, child in node.children.items():
            self._collect(child, prefix + ch, results)


# ─── Tests (do not modify below this line) ───

def test_insert_and_search():
    trie = Trie()
    trie.insert("apple")
    trie.insert("app")
    assert trie.search("apple")
    assert trie.search("app")
    assert not trie.search("ap")

def test_starts_with():
    trie = Trie()
    trie.insert("hello")
    assert trie.starts_with("hel")
    assert not trie.starts_with("world")

def test_auto_complete():
    trie = Trie()
    trie.insert("car")
    trie.insert("card")
    trie.insert("care")
    trie.insert("careful")
    trie.insert("dog")
    results = trie.auto_complete("car")
    assert results == ["car", "card", "care", "careful"]

def test_empty_trie():
    trie = Trie()
    assert not trie.search("anything")
