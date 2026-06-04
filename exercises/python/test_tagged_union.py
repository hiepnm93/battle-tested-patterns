# Pattern: Tagged Union
# Difficulty: Basic -> Intermediate

from dataclasses import dataclass
from typing import Union


@dataclass
class TaggedValue:
    tag: str  # "null", "bool", "number", "string"
    value: Union[None, bool, int, float, str]


def display(tv: TaggedValue) -> str:  # TODO: implement
    if tv.tag == "null":
        return "null"
    elif tv.tag == "bool":
        return str(tv.value).lower()
    elif tv.tag == "number":
        return str(tv.value)
    elif tv.tag == "string":
        return f'"{tv.value}"'
    raise ValueError(f"Unknown tag: {tv.tag}")


def try_add(a: TaggedValue, b: TaggedValue) -> TaggedValue | None:  # TODO: implement
    if a.tag != "number" or b.tag != "number":
        return None
    return TaggedValue("number", a.value + b.value)


def is_numeric(tv: TaggedValue) -> bool:
    return tv.tag == "number"


# ─── Tests (do not modify below this line) ───

def test_int():
    v = TaggedValue("number", 42)
    assert display(v) == "42"
    assert is_numeric(v)

def test_float():
    v = TaggedValue("number", 3.14)
    assert display(v) == "3.14"
    assert is_numeric(v)

def test_string():
    v = TaggedValue("string", "hello")
    assert display(v) == '"hello"'
    assert not is_numeric(v)

def test_bool():
    v = TaggedValue("bool", True)
    assert display(v) == "true"
    assert not is_numeric(v)

def test_null():
    v = TaggedValue("null", None)
    assert display(v) == "null"
    assert not is_numeric(v)

def test_try_add_numbers():
    a = TaggedValue("number", 10)
    b = TaggedValue("number", 20)
    result = try_add(a, b)
    assert result is not None
    assert result.value == 30

def test_try_add_non_numbers():
    a = TaggedValue("number", 10)
    b = TaggedValue("string", "hello")
    assert try_add(a, b) is None

def test_collection():
    values = [
        TaggedValue("number", 1),
        TaggedValue("number", 2.5),
        TaggedValue("string", "three"),
    ]
    num_count = sum(1 for v in values if is_numeric(v))
    assert num_count == 2
