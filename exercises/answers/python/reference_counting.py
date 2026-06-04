from typing import TypeVar, Generic, Callable, Optional

T = TypeVar("T")

class RefCounted(Generic[T]):
    def __init__(self, value: T, cleanup: Callable[[T], None]):
        self._value = value
        self._count = 1
        self._dropped = False
        self._cleanup = cleanup
        self._owned = True

    def clone(self) -> "RefCounted[T]":
        if not self._owned:
            raise RuntimeError("Cannot clone a dropped reference")
        self._count += 1
        copy = object.__new__(RefCounted)
        # Share internal state by reference
        copy.__dict__ = self.__dict__
        copy._owned = True
        return copy

    def drop(self) -> None:
        if not self._owned:
            return
        self._owned = False
        self._count -= 1
        if self._count == 0 and not self._dropped:
            self._dropped = True
            self._cleanup(self._value)

    @property
    def ref_count(self) -> int:
        return self._count

    @property
    def value(self) -> T:
        if not self._owned:
            raise RuntimeError("Reference has been dropped")
        return self._value
