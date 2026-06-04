"""Vtable / Ops Dispatch pattern — function pointer structs for runtime polymorphism."""
import math
from dataclasses import dataclass
from typing import Callable


@dataclass
class ShapeVtable:  # TODO: implement
    area: Callable[[list[float]], float]
    perimeter: Callable[[list[float]], float]


@dataclass
class Shape:  # TODO: implement
    vtable: ShapeVtable
    data: list[float]


circle_vtable = ShapeVtable(  # TODO: implement
    area=lambda d: math.pi * d[0] ** 2,
    perimeter=lambda d: 2 * math.pi * d[0],
)

rect_vtable = ShapeVtable(  # TODO: implement
    area=lambda d: d[0] * d[1],
    perimeter=lambda d: 2 * (d[0] + d[1]),
)


def create_circle(r: float) -> Shape:  # TODO: implement
    return Shape(vtable=circle_vtable, data=[r])


def create_rect(w: float, h: float) -> Shape:  # TODO: implement
    return Shape(vtable=rect_vtable, data=[w, h])


# ─── Tests (do not modify below this line) ───


def test_circle_area():
    c = create_circle(5.0)
    assert abs(c.vtable.area(c.data) - math.pi * 25) < 1e-9


def test_circle_perimeter():
    c = create_circle(5.0)
    assert abs(c.vtable.perimeter(c.data) - 2 * math.pi * 5) < 1e-9


def test_rect_area():
    r = create_rect(4.0, 6.0)
    assert r.vtable.area(r.data) == 24.0


def test_rect_perimeter():
    r = create_rect(4.0, 6.0)
    assert r.vtable.perimeter(r.data) == 20.0


def test_polymorphic_dispatch():
    """Heterogeneous list of shapes using vtable dispatch."""
    shapes = [create_circle(1.0), create_rect(2.0, 3.0), create_circle(2.0)]
    total = sum(s.vtable.area(s.data) for s in shapes)
    expected = math.pi * 1 + 6.0 + math.pi * 4
    assert abs(total - expected) < 1e-9


def test_shared_vtable():
    """All circles share the same vtable object."""
    c1 = create_circle(1.0)
    c2 = create_circle(2.0)
    assert c1.vtable is c2.vtable, "Same type should share vtable"


def test_different_vtables():
    c = create_circle(1.0)
    r = create_rect(1.0, 1.0)
    assert c.vtable is not r.vtable, "Different types should have different vtables"
