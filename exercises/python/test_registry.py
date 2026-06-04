"""Registry / Self-Registration — Python Exercise

Implement a registry that maps string names to factory functions, supporting
register, create, and list_registered operations.
Lines marked # TODO: implement are the key logic for learners to delete and rewrite.
"""

from typing import Any, Callable


class Registry:
    def __init__(self):
        self._entries: dict[str, Callable[..., Any]] = {}  # TODO: implement

    def register(self, name: str, factory: Callable[..., Any]) -> None:  # TODO: implement
        if name in self._entries:
            raise ValueError(f'"{name}" is already registered')
        self._entries[name] = factory

    def get(self, name: str) -> Callable[..., Any]:  # TODO: implement
        if name not in self._entries:
            raise KeyError(f'"{name}" is not registered')
        return self._entries[name]

    def create(self, name: str, *args: Any, **kwargs: Any) -> Any:  # TODO: implement
        return self.get(name)(*args, **kwargs)

    def has(self, name: str) -> bool:
        return name in self._entries

    def list_registered(self) -> list[str]:  # TODO: implement
        return list(self._entries.keys())


# ─── Tests (do not modify below this line) ───


def test_register_and_get():
    reg = Registry()
    reg.register("json", lambda data: f'{{"data": "{data}"}}')

    handler = reg.get("json")
    assert handler("test") == '{"data": "test"}'


def test_duplicate_registration():
    reg = Registry()
    reg.register("xml", lambda d: d)
    try:
        reg.register("xml", lambda d: d)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_missing_key():
    reg = Registry()
    try:
        reg.get("nonexistent")
        assert False, "Should have raised KeyError"
    except KeyError:
        pass


def test_create():
    reg = Registry()
    reg.register("greet", lambda name: f"Hello, {name}!")
    result = reg.create("greet", "World")
    assert result == "Hello, World!"


def test_multiple_entries():
    reg = Registry()
    reg.register("a", lambda d: "a:" + d)
    reg.register("b", lambda d: "b:" + d)
    reg.register("c", lambda d: "c:" + d)

    assert len(reg.list_registered()) == 3
    assert reg.create("b", "x") == "b:x"


def test_has():
    reg = Registry()
    reg.register("json", lambda: None)
    assert reg.has("json") is True
    assert reg.has("yaml") is False


def test_list_registered():
    reg = Registry()
    reg.register("alpha", lambda: None)
    reg.register("beta", lambda: None)
    names = reg.list_registered()
    assert "alpha" in names
    assert "beta" in names
    assert len(names) == 2
