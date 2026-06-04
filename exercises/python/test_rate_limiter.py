"""Rate Limiter (Token Bucket) — control throughput with token-based admission."""

import time


class TokenBucket:
    def __init__(self, capacity: float, refill_rate: float):
        self.capacity = capacity  # TODO: implement
        self.refill_rate = refill_rate  # TODO: implement
        self.tokens = capacity
        self.last_refill = time.time()

    def _refill(self) -> None:
        now = time.time()  # TODO: implement
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def allow(self, tokens: float = 1) -> bool:
        self._refill()  # TODO: implement
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


# ─── Tests (do not modify below this line) ───


def test_token_bucket_allows():
    tb = TokenBucket(capacity=3, refill_rate=1)
    assert tb.allow() is True, "should allow with tokens available"


def test_token_bucket_exhaustion():
    tb = TokenBucket(capacity=2, refill_rate=0)
    tb.allow()
    tb.allow()
    assert tb.allow() is False, "should deny when tokens exhausted"


def test_token_bucket_refill():
    tb = TokenBucket(capacity=1, refill_rate=1000)  # 1000 tokens/sec
    tb.allow()  # drain
    time.sleep(0.005)
    assert tb.allow() is True, "should allow after refill"


def test_token_bucket_max_cap():
    tb = TokenBucket(capacity=2, refill_rate=1000)
    time.sleep(0.010)  # would add many tokens
    tb.allow()
    tb.allow()
    assert tb.allow() is False, "should not exceed max capacity"
