"""Visitor pattern — decouple tree traversal from operations."""
from dataclasses import dataclass


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


def visit(expr: Expr, visitor: dict) -> float:  # TODO: implement
    if isinstance(expr, Number):
        return visitor["number"](expr.value)
    elif isinstance(expr, Add):
        return visitor["add"](expr.left, expr.right)
    elif isinstance(expr, Multiply):
        return visitor["multiply"](expr.left, expr.right)
    raise TypeError(f"Unknown expr: {expr}")


eval_visitor = {  # TODO: implement
    "number": lambda v: v,
    "add": lambda l, r: visit(l, eval_visitor) + visit(r, eval_visitor),
    "multiply": lambda l, r: visit(l, eval_visitor) * visit(r, eval_visitor),
}

print_visitor = {  # TODO: implement
    "number": lambda v: str(int(v)) if v == int(v) else str(v),
    "add": lambda l, r: f"({visit(l, print_visitor)} + {visit(r, print_visitor)})",
    "multiply": lambda l, r: f"({visit(l, print_visitor)} * {visit(r, print_visitor)})",
}


# ─── Tests (do not modify below this line) ───


def test_eval_number():
    assert visit(Number(42), eval_visitor) == 42


def test_eval_add():
    tree = Add(Number(1), Number(2))
    assert visit(tree, eval_visitor) == 3


def test_eval_multiply():
    tree = Multiply(Number(3), Number(4))
    assert visit(tree, eval_visitor) == 12


def test_eval_nested():
    # (3 + (2 * 4)) = 11
    tree = Add(Number(3), Multiply(Number(2), Number(4)))
    assert visit(tree, eval_visitor) == 11


def test_print_simple():
    tree = Add(Number(1), Number(2))
    assert visit(tree, print_visitor) == "(1 + 2)"


def test_print_nested():
    # ((1 + 2) * (3 + 4))
    tree = Multiply(
        Add(Number(1), Number(2)),
        Add(Number(3), Number(4)),
    )
    assert visit(tree, print_visitor) == "((1 + 2) * (3 + 4))"


def test_eval_complex():
    # ((1 + 2) * (3 + 4)) = 21
    tree = Multiply(
        Add(Number(1), Number(2)),
        Add(Number(3), Number(4)),
    )
    assert visit(tree, eval_visitor) == 21
