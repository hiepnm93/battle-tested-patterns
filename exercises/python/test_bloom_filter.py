# Pattern: Bloom Filter
# Difficulty: Basic -> Intermediate


class BloomFilter:
    def __init__(self, size: int, hash_count: int = 3):  # TODO: implement
        self.size = size
        self.hash_count = hash_count
        self.bits = [False] * size

    def _hashes(self, item: str) -> list[int]:  # TODO: implement
        h1, h2 = 0, 0
        for ch in item:
            h1 = (h1 * 31 + ord(ch)) & 0xFFFFFFFF
            h2 = (h2 * 37 + ord(ch)) & 0xFFFFFFFF
        return [(h1 + i * h2) % self.size for i in range(self.hash_count)]

    def add(self, item: str) -> None:  # TODO: implement
        for pos in self._hashes(item):
            self.bits[pos] = True

    def might_contain(self, item: str) -> bool:  # TODO: implement
        return all(self.bits[pos] for pos in self._hashes(item))


# ─── Tests (do not modify below this line) ───

def test_add_and_check():
    bf = BloomFilter(1024, 3)
    bf.add("hello")
    bf.add("world")
    assert bf.might_contain("hello")
    assert bf.might_contain("world")

def test_no_false_negatives():
    bf = BloomFilter(4096, 5)
    items = ["alpha", "beta", "gamma", "delta", "epsilon"]
    for item in items:
        bf.add(item)
    for item in items:
        assert bf.might_contain(item), f"false negative for {item!r}"

def test_probably_absent():
    bf = BloomFilter(4096, 5)
    bf.add("present")
    absent = ["absent1", "absent2", "absent3", "missing", "nope"]
    false_positives = sum(1 for item in absent if bf.might_contain(item))
    assert false_positives < len(absent), "all absent items reported as present — filter is broken"
