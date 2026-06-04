"""Middleware / Pipeline Chain pattern — compose handlers with pre/post processing."""
from typing import Any, Callable

Ctx = dict[str, Any]
NextFn = Callable[[], None]
MiddlewareFn = Callable[[Ctx, NextFn], None]


class Pipeline:  # TODO: implement
    def __init__(self) -> None:
        self._middlewares: list[MiddlewareFn] = []

    def use(self, middleware: MiddlewareFn) -> None:  # TODO: implement
        self._middlewares.append(middleware)

    def execute(self, ctx: Ctx) -> None:  # TODO: implement
        index = 0

        def next_fn() -> None:
            nonlocal index
            if index < len(self._middlewares):
                mw = self._middlewares[index]
                index += 1
                mw(ctx, next_fn)

        next_fn()


# ─── Tests (do not modify below this line) ───


def test_middleware_order():
    p = Pipeline()
    p.use(lambda ctx, next: (ctx["log"].append("A-before"), next(), ctx["log"].append("A-after")))
    p.use(lambda ctx, next: (ctx["log"].append("B-before"), next(), ctx["log"].append("B-after")))
    p.use(lambda ctx, next: (ctx["log"].append("handler"), ctx.__setitem__("response", "OK")))

    ctx: Ctx = {"request": "test", "log": []}
    p.execute(ctx)

    assert ctx["log"] == ["A-before", "B-before", "handler", "B-after", "A-after"]


def test_middleware_short_circuit():
    p = Pipeline()
    p.use(lambda ctx, next: ctx.__setitem__("response", "blocked"))  # don't call next
    p.use(lambda ctx, next: (ctx.__setitem__("response", "should not reach"), next()))

    ctx: Ctx = {}
    p.execute(ctx)
    assert ctx["response"] == "blocked"


def test_middleware_empty():
    p = Pipeline()
    ctx: Ctx = {"request": "test"}
    p.execute(ctx)
    assert "response" not in ctx


def test_middleware_context_mutation():
    """Middlewares can modify context and downstream sees changes."""
    p = Pipeline()

    def auth_mw(ctx, next):
        ctx["user"] = "admin"
        next()

    def handler(ctx, next):
        ctx["greeting"] = f"hello {ctx['user']}"

    p.use(auth_mw)
    p.use(handler)

    ctx: Ctx = {}
    p.execute(ctx)
    assert ctx["greeting"] == "hello admin"


def test_middleware_post_processing():
    """Post-processing runs in reverse order after handler."""
    p = Pipeline()

    def timing_mw(ctx, next):
        ctx["steps"].append("start-timer")
        next()
        ctx["steps"].append("stop-timer")

    def handler(ctx, next):
        ctx["steps"].append("handle")

    p.use(timing_mw)
    p.use(handler)

    ctx: Ctx = {"steps": []}
    p.execute(ctx)
    assert ctx["steps"] == ["start-timer", "handle", "stop-timer"]
