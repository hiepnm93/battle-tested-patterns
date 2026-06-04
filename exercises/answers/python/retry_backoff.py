import time
import random

def retry_with_backoff(fn, max_retries=5, base_delay=1.0, max_delay=30.0, jitter=0.5):
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception as e:
            last_error = e
            if attempt == max_retries:
                break
            exponential = base_delay * (2 ** attempt)
            delay = min(exponential + exponential * jitter * random.random(), max_delay)
            time.sleep(delay)
    raise last_error
