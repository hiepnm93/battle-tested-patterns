from dataclasses import dataclass
from typing import Callable

@dataclass
class ShapeVtable:
    area: Callable[[list[float]], float]
    perimeter: Callable[[list[float]], float]

@dataclass
class Shape:
    vtable: ShapeVtable
    data: list[float]

import math

circle_vtable = ShapeVtable(
    area=lambda d: math.pi * d[0] ** 2,
    perimeter=lambda d: 2 * math.pi * d[0],
)

rect_vtable = ShapeVtable(
    area=lambda d: d[0] * d[1],
    perimeter=lambda d: 2 * (d[0] + d[1]),
)

def create_circle(r: float) -> Shape:
    return Shape(vtable=circle_vtable, data=[r])

def create_rect(w: float, h: float) -> Shape:
    return Shape(vtable=rect_vtable, data=[w, h])
