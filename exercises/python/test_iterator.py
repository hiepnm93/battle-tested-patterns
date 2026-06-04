"""Iterator / Lazy Evaluation — Python Exercise

Implement a RangeIter that supports lazy iteration with map, filter, take, and collect.
Lines marked # TODO: implement are the key logic for learners to delete and rewrite.
"""


class RangeIter:
    """A lazy iterator over a range of integers with chainable transformations."""

    def __init__(self, source):
        self._source = source  # TODO: implement

    @classmethod
    def from_list(cls, items: list[int]) -> "RangeIter":
        return cls(iter(items))  # TODO: implement

    @classmethod
    def from_range(cls, start: int, stop: int) -> "RangeIter":
        return cls(iter(range(start, stop)))  # TODO: implement

    def __iter__(self):
        return self  # TODO: implement

    def __next__(self) -> int:
        return next(self._source)  # TODO: implement

    def map(self, fn):
        """Lazily apply fn to each element."""
        def _gen():  # TODO: implement
            for item in self._source:
                yield fn(item)
        return RangeIter(_gen())

    def filter(self, pred):
        """Lazily keep only elements where pred returns True."""
        def _gen():  # TODO: implement
            for item in self._source:
                if pred(item):
                    yield item
        return RangeIter(_gen())

    def take(self, n: int):
        """Lazily yield at most n elements."""
        def _gen():  # TODO: implement
            count = 0
            for item in self._source:
                if count >= n:
                    break
                yield item
                count += 1
        return RangeIter(_gen())

    def collect(self) -> list[int]:
        """Consume the iterator and return a list."""
        return list(self._source)  # TODO: implement

    def fold(self, init, fn):
        """Reduce the iterator to a single value."""
        acc = init  # TODO: implement
        for item in self._source:
            acc = fn(acc, item)
        return acc


# ─── Tests (do not modify below this line) ───


def test_filter():
    source = RangeIter.from_list([1, 2, 3, 4, 5, 6])
    odds = source.filter(lambda x: x % 2 != 0).collect()
    assert odds == [1, 3, 5]


def test_map_and_take():
    source = RangeIter.from_list([1, 2, 3, 4, 5])
    doubled = source.map(lambda x: x * 2).take(3).collect()
    assert doubled == [2, 4, 6]


def test_pipeline():
    source = RangeIter.from_list([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    result = (
        source
        .filter(lambda x: x % 2 != 0)
        .map(lambda x: x * 10)
        .take(3)
        .collect()
    )
    assert result == [10, 30, 50]


def test_empty():
    source = RangeIter.from_list([])
    result = source.filter(lambda x: True).collect()
    assert result == []


def test_fold():
    source = RangeIter.from_list([1, 2, 3, 4, 5])
    total = source.fold(0, lambda acc, x: acc + x)
    assert total == 15


def test_from_range():
    result = RangeIter.from_range(1, 6).collect()
    assert result == [1, 2, 3, 4, 5]


def test_take_more_than_available():
    source = RangeIter.from_list([1, 2])
    result = source.take(10).collect()
    assert result == [1, 2]
