"""Diff/Patch pattern — compute minimal edit operations between two sequences."""
from typing import TypeVar, List, Tuple, Literal

T = TypeVar("T")
Op = Tuple[Literal["keep", "insert", "delete"], T]


def diff(old: List[T], new: List[T]) -> List[Op]:  # TODO: implement
    ops: List[Op] = []
    oi, ni = 0, 0

    while oi < len(old) and ni < len(new):
        if old[oi] == new[ni]:
            ops.append(("keep", old[oi]))
            oi += 1; ni += 1
        elif old[oi] not in new[ni:]:
            ops.append(("delete", old[oi]))
            oi += 1
        else:
            ops.append(("insert", new[ni]))
            ni += 1

    while oi < len(old): ops.append(("delete", old[oi])); oi += 1
    while ni < len(new): ops.append(("insert", new[ni])); ni += 1
    return ops


def patch(ops: List[Op]) -> List[T]:  # TODO: implement
    return [val for op_type, val in ops if op_type != "delete"]


# ─── Tests (do not modify below this line) ───


def test_diff_no_change():
    items = ["a", "b", "c"]
    ops = diff(items, items)
    for op_type, _ in ops:
        assert op_type == "keep"


def test_diff_add_remove():
    old = ["a", "b", "c"]
    new = ["a", "x", "c"]
    ops = diff(old, new)

    has_remove = any(op == ("delete", "b") for op in ops)
    has_add = any(op == ("insert", "x") for op in ops)
    assert has_remove, "Should detect removal of 'b'"
    assert has_add, "Should detect insertion of 'x'"


def test_patch_apply():
    old = ["a", "b", "c"]
    new = ["a", "c", "e", "d"]
    ops = diff(old, new)
    result = patch(ops)
    assert result == new


def test_diff_empty_old():
    ops = diff([], ["a", "b"])
    add_count = sum(1 for op_type, _ in ops if op_type == "insert")
    assert add_count == 2


def test_diff_empty_new():
    ops = diff(["a", "b"], [])
    delete_count = sum(1 for op_type, _ in ops if op_type == "delete")
    assert delete_count == 2


def test_diff_both_empty():
    ops = diff([], [])
    assert ops == []


def test_patch_roundtrip():
    old = ["a", "b", "c", "d"]
    new = ["a", "c", "e", "d"]
    ops = diff(old, new)
    result = patch(ops)
    assert result == new
