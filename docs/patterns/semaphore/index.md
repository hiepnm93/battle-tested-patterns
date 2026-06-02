# Pattern: Semaphore / Bounded Concurrency

## One Liner

Limit the number of concurrent operations by maintaining a counter — acquire before work, release after, block when the limit is reached.

## Core Idea

A semaphore is a counter with two atomic operations: `acquire` (decrement, block if zero) and `release` (increment). It controls how many concurrent tasks can access a shared resource.

```mermaid
sequenceDiagram
    participant T1 as Task 1
    participant S as Semaphore (max=2)
    participant T2 as Task 2
    participant T3 as Task 3

    T1->>S: acquire (count: 2→1)
    T2->>S: acquire (count: 1→0)
    T3->>S: acquire (blocked — count=0)
    T1->>S: release (count: 0→1)
    S->>T3: unblock (count: 1→0)
```

## Production Proof

| Project | Source | Usage |
|---------|--------|-------|
| Linux Kernel | [semaphore.h#L15-L55](https://github.com/torvalds/linux/blob/master/include/linux/semaphore.h#L15-L55) | `struct semaphore` — kernel counting semaphore with `down()` (acquire) and `up()` (release). Used for device driver access control, limiting concurrent I/O operations. |
| Go stdlib | [Semaphore (x/sync)](https://github.com/golang/sync/blob/master/semaphore/semaphore.go) | `semaphore.Weighted` — a weighted semaphore used internally by `errgroup` to limit goroutine concurrency. Idiomatic Go also uses buffered channels as semaphores: `make(chan struct{}, n)`. |

## Implementation

::: code-group

```typescript [TypeScript]
class Semaphore {
  private queue: (() => void)[] = [];
  private count: number;

  constructor(private max: number) {
    this.count = max;
  }

  async acquire(): Promise<void> {
    if (this.count > 0) {
      this.count--;
      return;
    }
    return new Promise<void>((resolve) => this.queue.push(resolve));
  }

  release(): void {
    const next = this.queue.shift();
    if (next) {
      next();
    } else {
      this.count++;
    }
  }

  get available(): number {
    return this.count;
  }
}

async function withSemaphore<T>(sem: Semaphore, fn: () => Promise<T>): Promise<T> {
  await sem.acquire();
  try { return await fn(); }
  finally { sem.release(); }
}
```

```go [Go]
// Idiomatic Go: buffered channel as semaphore
func processWithLimit(items []string, maxConcurrent int) {
	sem := make(chan struct{}, maxConcurrent)
	var wg sync.WaitGroup

	for _, item := range items {
		wg.Add(1)
		sem <- struct{}{} // acquire
		go func(s string) {
			defer wg.Done()
			defer func() { <-sem }() // release
			process(s)
		}(item)
	}
	wg.Wait()
}
```

```python [Python]
import asyncio

async def fetch_with_limit(urls: list[str], max_concurrent: int = 5):
    sem = asyncio.Semaphore(max_concurrent)
    async def fetch_one(url: str):
        async with sem:  # acquire + release via context manager
            return await do_fetch(url)
    return await asyncio.gather(*(fetch_one(u) for u in urls))
```

```rust [Rust]
use std::sync::{Arc, Mutex, Condvar};

pub struct Semaphore {
    count: Mutex<usize>,
    cvar: Condvar,
}

impl Semaphore {
    pub fn new(max: usize) -> Self {
        Semaphore { count: Mutex::new(max), cvar: Condvar::new() }
    }

    pub fn acquire(&self) {
        let mut count = self.count.lock().unwrap();
        while *count == 0 { count = self.cvar.wait(count).unwrap(); }
        *count -= 1;
    }

    pub fn release(&self) {
        *self.count.lock().unwrap() += 1;
        self.cvar.notify_one();
    }
}
```

:::

## Exercises

| Level | Exercise | File |
|-------|----------|------|
| Basic | Implement a counting semaphore with acquire/release | `exercises/typescript/semaphore/01-basic.test.ts` |

Run exercises: `pnpm test`

## When to Use

- **Rate limiting** — limit concurrent API calls, database connections
- **Resource pools** — control access to a fixed number of resources
- **Backpressure** — prevent overwhelming downstream services
- **Throttling** — limit concurrent file I/O, network requests

## When NOT to Use

- **Mutual exclusion** — if you need exclusive access (max=1), use a mutex/lock instead
- **Simple counters** — if you don't need blocking, use an atomic counter
- **Queue-based flow** — if order matters, use a bounded queue instead

## More Production Uses

Java `Semaphore`, Python `threading.Semaphore`, Nginx worker connections, PostgreSQL `max_connections`, Kubernetes resource quotas.
