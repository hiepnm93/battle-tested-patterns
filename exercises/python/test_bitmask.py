# Pattern: Bitmask
# Difficulty: Basic -> Intermediate

READ    = 1 << 0  # 0b0001
WRITE   = 1 << 1  # 0b0010
EXECUTE = 1 << 2  # 0b0100
DELETE  = 1 << 3  # 0b1000

def has_flag(flags: int, flag: int) -> bool:  # TODO: implement
    return (flags & flag) == flag

def has_any(flags: int, mask: int) -> bool:  # TODO: implement
    return (flags & mask) != 0

def set_flag(flags: int, flag: int) -> int:  # TODO: implement
    return flags | flag

def clear_flag(flags: int, flag: int) -> int:  # TODO: implement
    return flags & ~flag

def toggle_flag(flags: int, flag: int) -> int:  # TODO: implement
    return flags ^ flag


# ─── Tests (do not modify below this line) ───

def test_set_and_check_flag():
    flags = set_flag(0, READ)
    assert has_flag(flags, READ)
    assert not has_flag(flags, WRITE)

def test_multiple_flags():
    flags = READ | WRITE
    assert has_flag(flags, READ)
    assert has_flag(flags, WRITE)
    assert not has_flag(flags, EXECUTE)

def test_clear_flag():
    flags = READ | WRITE | EXECUTE
    flags = clear_flag(flags, WRITE)
    assert not has_flag(flags, WRITE)
    assert has_flag(flags, READ)
    assert has_flag(flags, EXECUTE)

def test_toggle_flag():
    flags = READ
    flags = toggle_flag(flags, WRITE)
    assert has_flag(flags, WRITE)
    flags = toggle_flag(flags, WRITE)
    assert not has_flag(flags, WRITE)

def test_has_any():
    dangerous = WRITE | DELETE
    assert not has_any(READ, dangerous)
    assert has_any(READ | WRITE, dangerous)

def test_compound_permission():
    required = READ | WRITE
    editor = READ | WRITE | EXECUTE
    viewer = READ
    assert has_flag(editor, required)
    assert not has_flag(viewer, required)
