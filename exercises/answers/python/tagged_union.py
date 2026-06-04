from dataclasses import dataclass
from typing import Union

@dataclass
class TaggedValue:
    tag: str  # "null", "bool", "number", "string"
    value: Union[None, bool, int, float, str]

def display(tv: TaggedValue) -> str:
    if tv.tag == "null":
        return "null"
    elif tv.tag == "bool":
        return str(tv.value).lower()
    elif tv.tag == "number":
        return str(tv.value)
    elif tv.tag == "string":
        return f'"{tv.value}"'
    raise ValueError(f"Unknown tag: {tv.tag}")

def try_add(a: TaggedValue, b: TaggedValue) -> TaggedValue | None:
    if a.tag != "number" or b.tag != "number":
        return None
    return TaggedValue("number", a.value + b.value)
