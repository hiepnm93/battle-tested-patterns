# Pattern: Interning
# Difficulty: Basic -> Intermediate


class StringInterner:
    def __init__(self):  # TODO: implement
        self._str_to_id: dict[str, int] = {}
        self._id_to_str: list[str] = []

    def intern(self, s: str) -> int:  # TODO: implement
        if s in self._str_to_id:
            return self._str_to_id[s]
        sym_id = len(self._id_to_str)
        self._str_to_id[s] = sym_id
        self._id_to_str.append(s)
        return sym_id

    def resolve(self, sym_id: int) -> str | None:  # TODO: implement
        if 0 <= sym_id < len(self._id_to_str):
            return self._id_to_str[sym_id]
        return None

    @property
    def size(self) -> int:
        return len(self._id_to_str)


# ─── Tests (do not modify below this line) ───

def test_same_id_for_same_string():
    interner = StringInterner()
    id1 = interner.intern("hello")
    id2 = interner.intern("hello")
    assert id1 == id2

def test_different_ids_for_different_strings():
    interner = StringInterner()
    id1 = interner.intern("hello")
    id2 = interner.intern("world")
    assert id1 != id2
    assert interner.size == 2

def test_resolve():
    interner = StringInterner()
    sym_id = interner.intern("test")
    assert interner.resolve(sym_id) == "test"

def test_resolve_invalid():
    interner = StringInterner()
    assert interner.resolve(999) is None

def test_many_strings():
    interner = StringInterner()
    strs = ["alpha", "beta", "gamma", "alpha", "beta"]
    ids = [interner.intern(s) for s in strs]
    assert interner.size == 3
    assert ids[0] == ids[3]  # "alpha" at index 0 and 3
    assert ids[1] == ids[4]  # "beta" at index 1 and 4
