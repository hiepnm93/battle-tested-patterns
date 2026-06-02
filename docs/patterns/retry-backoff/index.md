# Pattern: Retry with Exponential Backoff

## One Liner

When an operation fails, retry it with progressively longer delays plus random jitter to avoid thundering herd.

## Core Idea

Instead of retrying immediately (which overloads the failing service) or giving up (which loses the request), exponential backoff doubles the wait time on each retry. Adding jitter randomizes the delay so thousands of clients don't retry simultaneously.

```text
Attempt 1: failed → wait  1s + jitter
Attempt 2: failed → wait  2s + jitter
Attempt 3: failed → wait  4s + jitter
Attempt 4: failed → wait  8s + jitter
Attempt 5: failed → wait 16s + jitter (capped)
Attempt 6: success ✓
```

The formula: `delay = min(base * 2^attempt + random(0, jitter), maxDelay)`

## Production Proof

| Project | Source | Usage |
|---------|--------|-------|
| Kubernetes | [backoff.go#L30-L50](https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/apimachinery/pkg/util/wait/backoff.go#L30-L50) | `Backoff` struct defines `Duration`, `Factor`, `Jitter`, `Steps`, `Cap`. `ExponentialBackoff` (line 475) retries with this config. Used for pod restart backoff, API server retries, controller reconciliation. |
| gRPC | [connection-backoff.md](https://github.com/grpc/grpc/blob/master/doc/connection-backoff.md) | gRPC's connection backoff spec defines the algorithm all gRPC clients must implement: initial 1s, multiply by 1.6, jitter ±20%, cap at 120s. Used by every gRPC connection worldwide. |

## Implementation

::: code-group

```typescript [TypeScript]
interface BackoffConfig {
  maxRetries: number;
  baseDelay: number;
  maxDelay: number;
  jitter: number; // 0-1
}

async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  config: BackoffConfig = { maxRetries: 5, baseDelay: 1000, maxDelay: 30000, jitter: 0.5 },
): Promise<T> {
  let lastError: Error | undefined;

  for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      lastError = err as Error;
      if (attempt === config.maxRetries) break;

      const exponential = config.baseDelay * Math.pow(2, attempt);
      const jitter = exponential * config.jitter * Math.random();
      const delay = Math.min(exponential + jitter, config.maxDelay);

      await new Promise((r) => setTimeout(r, delay));
    }
  }

  throw lastError;
}
```

```rust [Rust]
use std::time::Duration;

pub struct Backoff {
    pub max_retries: u32,
    pub base_delay: Duration,
    pub max_delay: Duration,
}

impl Backoff {
    pub fn delay_for(&self, attempt: u32) -> Duration {
        let exponential = self.base_delay.as_millis() as u64 * 2u64.pow(attempt);
        let capped = exponential.min(self.max_delay.as_millis() as u64);
        Duration::from_millis(capped)
    }
}
```

```go [Go]
package backoff

import (
	"math"
	"math/rand"
	"time"
)

type Config struct {
	MaxRetries int
	BaseDelay  time.Duration
	MaxDelay   time.Duration
	Jitter     float64
}

func Retry(fn func() error, cfg Config) error {
	var lastErr error
	for attempt := 0; attempt <= cfg.MaxRetries; attempt++ {
		lastErr = fn()
		if lastErr == nil {
			return nil
		}
		if attempt == cfg.MaxRetries {
			break
		}
		exp := float64(cfg.BaseDelay) * math.Pow(2, float64(attempt))
		jitter := exp * cfg.Jitter * rand.Float64()
		delay := time.Duration(math.Min(exp+jitter, float64(cfg.MaxDelay)))
		time.Sleep(delay)
	}
	return lastErr
}
```

```python [Python]
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
```

:::

## Exercises

| Level | Exercise | File |
|-------|----------|------|
| Basic | Implement retry with configurable backoff | `exercises/typescript/retry-backoff/01-basic.test.ts` |

Run exercises: `pnpm test`

## When to Use

- **Network requests** — HTTP calls, database connections, RPC
- **Distributed systems** — service-to-service calls that may transiently fail
- **Rate-limited APIs** — back off when hitting rate limits (often 429 responses)
- **Queue consumers** — retry failed message processing

## When NOT to Use

- **Non-transient errors** — 400 Bad Request won't succeed on retry; validate input instead
- **Idempotency not guaranteed** — retrying a non-idempotent POST could create duplicates
- **User-facing latency** — exponential backoff means 30+ second waits; show an error instead
- **Local operations** — file not found, parse error — these won't fix themselves on retry

## More Production Uses

AWS SDK (all services), Azure SDK, Google Cloud client libraries, Envoy proxy, Istio service mesh, Celery (Python task queue), Sidekiq (Ruby background jobs).
