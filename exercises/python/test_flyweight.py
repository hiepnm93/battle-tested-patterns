"""Flyweight / Interning pattern — share identical immutable objects."""


class Interner:  # TODO: implement
    def __init__(self):
        self._pool: dict[str, object] = {}

    def intern(self, key: str, factory=None):  # TODO: implement
        if key in self._pool:
            return self._pool[key]
        value = factory() if factory else key
        self._pool[key] = value
        return value

    @property
    def size(self) -> int:  # TODO: implement
        return len(self._pool)


# ─── Tests (do not modify below this line) ───


def test_shared_instance():
    interner = Interner()
    r1 = interner.intern("red", lambda: {"r": 255, "g": 0, "b": 0})
    r2 = interner.intern("red", lambda: {"r": 255, "g": 0, "b": 0})
    assert r1 is r2, "Same key should return same object"


def test_different_instances():
    interner = Interner()
    r = interner.intern("red", lambda: {"r": 255, "g": 0, "b": 0})
    g = interner.intern("green", lambda: {"r": 0, "g": 255, "b": 0})
    assert r is not g, "Different keys should return different objects"


def test_correct_values():
    interner = Interner()
    r = interner.intern("red", lambda: {"r": 255, "g": 0, "b": 0})
    assert r == {"r": 255, "g": 0, "b": 0}


def test_memory_saving():
    interner = Interner()
    for _ in range(1000):
        interner.intern("blue", lambda: "blue-value")
    assert interner.size == 1


def test_string_interning_default():
    interner = Interner()
    s1 = interner.intern("hello")
    s2 = interner.intern("hello")
    assert s1 is s2
    assert s1 == "hello"


def test_factory_called_only_once():
    interner = Interner()
    counter = {"calls": 0}

    def factory():
        counter["calls"] += 1
        return f"value-{counter['calls']}"

    v1 = interner.intern("key", factory)
    v2 = interner.intern("key", factory)
    assert v1 is v2
    assert counter["calls"] == 1, "Factory should be called only once"
