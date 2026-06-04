from dataclasses import dataclass
from typing import Protocol, TypeVar

T = TypeVar("T")

@dataclass
class Number:
    value: float

@dataclass
class Add:
    left: "Expr"
    right: "Expr"

@dataclass
class Multiply:
    left: "Expr"
    right: "Expr"

Expr = Number | Add | Multiply

def visit(expr: Expr, visitor: dict) -> float:
    if isinstance(expr, Number):
        return visitor["number"](expr.value)
    elif isinstance(expr, Add):
        return visitor["add"](expr.left, expr.right)
    elif isinstance(expr, Multiply):
        return visitor["multiply"](expr.left, expr.right)
    raise TypeError(f"Unknown expr: {expr}")

eval_visitor = {
    "number": lambda v: v,
    "add": lambda l, r: visit(l, eval_visitor) + visit(r, eval_visitor),
    "multiply": lambda l, r: visit(l, eval_visitor) * visit(r, eval_visitor),
}
