"""Circuit Breaker — fail fast when a service is down."""

import time


class CircuitBreaker:
    def __init__(self, threshold: int = 5, reset_timeout: float = 30.0):  # TODO: implement
        self.threshold = threshold
        self.reset_timeout = reset_timeout
        self.state = "CLOSED"
        self.failure_count = 0
        self.last_failure_time = 0.0

    def get_state(self) -> str:  # TODO: implement
        if self.state == "OPEN" and time.time() - self.last_failure_time >= self.reset_timeout:
            self.state = "HALF_OPEN"
        return self.state

    def call(self, fn):  # TODO: implement
        if self.get_state() == "OPEN":
            raise RuntimeError("Circuit is OPEN")
        try:
            result = fn()
            self._on_success()
            return result
        except Exception:
            self._on_failure()
            raise

    def _on_success(self) -> None:  # TODO: implement
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self) -> None:  # TODO: implement
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.threshold:
            self.state = "OPEN"


# ─── Tests (do not modify below this line) ───


def test_circuit_breaker_closed_on_success():
    cb = CircuitBreaker(threshold=3, reset_timeout=1.0)
    result = cb.call(lambda: "ok")
    assert result == "ok"
    assert cb.get_state() == "CLOSED"


def test_circuit_breaker_opens_on_failures():
    cb = CircuitBreaker(threshold=3, reset_timeout=1.0)

    def fail():
        raise RuntimeError("fail")

    for _ in range(2):
        try:
            cb.call(fail)
        except RuntimeError:
            pass
    assert cb.get_state() == "CLOSED", "should still be closed before threshold"

    try:
        cb.call(fail)
    except RuntimeError:
        pass
    assert cb.get_state() == "OPEN", "should be open after threshold failures"


def _make_failure():
    raise RuntimeError("fail")


def test_circuit_breaker_rejects_when_open():
    cb = CircuitBreaker(threshold=1, reset_timeout=3600.0)
    try:
        cb.call(_make_failure)
    except RuntimeError:
        pass

    try:
        cb.call(lambda: "ok")
        assert False, "should have raised"
    except RuntimeError as e:
        assert str(e) == "Circuit is OPEN"


def test_circuit_breaker_recovery():
    cb = CircuitBreaker(threshold=1, reset_timeout=0.001)
    try:
        cb.call(_make_failure)
    except RuntimeError:
        pass

    time.sleep(0.005)

    result = cb.call(lambda: "recovered")
    assert result == "recovered"
    assert cb.get_state() == "CLOSED"
