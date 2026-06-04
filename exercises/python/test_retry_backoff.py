"""Retry with Exponential Backoff — Python Exercise

Implement a retry function that retries a callable with exponential backoff
and jitter upon failure.
Lines marked # TODO: implement are the key logic for learners to delete and rewrite.
"""

import time
import random


def retry_with_backoff(  # TODO: implement
    fn,
    max_retries=5,
    base_delay=1.0,
    max_delay=30.0,
    jitter=0.5,
):
    """Retry fn with exponential backoff. Returns (result, attempts)."""
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            result = fn()
            return result, attempt + 1
        except Exception as e:
            last_error = e
            if attempt == max_retries:
                break
            exponential = base_delay * (2 ** attempt)
            delay = min(exponential + exponential * jitter * random.random(), max_delay)
            time.sleep(delay)
    raise last_error


# ─── Tests (do not modify below this line) ───


def test_succeeds_first_try():
    result, attempts = retry_with_backoff(
        lambda: "ok", max_retries=3, base_delay=0.001
    )
    assert result == "ok"
    assert attempts == 1


def test_succeeds_after_failures():
    call_count = 0

    def flaky():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("transient")
        return "recovered"

    result, attempts = retry_with_backoff(
        flaky, max_retries=5, base_delay=0.001
    )
    assert result == "recovered"
    assert attempts == 3


def test_exhausts_retries():
    try:
        retry_with_backoff(
            lambda: (_ for _ in ()).throw(ValueError("permanent")),
            max_retries=2,
            base_delay=0.001,
        )
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_exponential_delay():
    start = time.monotonic()
    try:
        retry_with_backoff(
            lambda: (_ for _ in ()).throw(RuntimeError("fail")),
            max_retries=3,
            base_delay=0.005,
            max_delay=1.0,
            jitter=0.0,  # No jitter for predictable timing
        )
    except RuntimeError:
        pass
    elapsed = time.monotonic() - start
    # 5ms + 10ms + 20ms = 35ms minimum
    assert elapsed >= 0.030, f"Expected >= 30ms of backoff, got {elapsed*1000:.0f}ms"


def test_max_delay_cap():
    delays = []

    original_sleep = time.sleep

    def mock_sleep(duration):
        delays.append(duration)
        # Don't actually sleep for the test
        pass

    time.sleep = mock_sleep
    try:
        retry_with_backoff(
            lambda: (_ for _ in ()).throw(RuntimeError("fail")),
            max_retries=10,
            base_delay=1.0,
            max_delay=5.0,
            jitter=0.0,
        )
    except RuntimeError:
        pass
    finally:
        time.sleep = original_sleep

    # All delays should be capped at max_delay
    for d in delays:
        assert d <= 5.0, f"Delay {d} exceeds max_delay 5.0"
