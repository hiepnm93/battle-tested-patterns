# Patterns from Go

Go's runtime and standard library demonstrate clean, practical pattern implementations.

| Pattern | Where in Go | What It Does |
|---------|------------|--------------|
| [Cooperative Scheduling](/patterns/cooperative-scheduling/) | `runtime/proc.go` | Goroutine scheduling with cooperative preemption points |
| [Bitmask](/patterns/bitmask/) | `os/types.go` | `FileMode` — Unix permission flags via typed constants with `iota` |
| [Object Pool](/patterns/object-pool/) | `sync/pool.go` | `sync.Pool` — per-P local pools with lock-free fast path, used in `fmt`, `encoding/json` |
| [Work Stealing](/patterns/work-stealing/) | `runtime/proc.go` | `stealWork` — goroutine scheduler steals from other P's run queues via `runqsteal`/`runqgrab` |
| [Free List](/patterns/free-list/) | `runtime/mfixalloc.go` | `fixalloc` — fixed-size free-list allocator with intrusive `mlink` nodes |
| [LRU Cache](/patterns/lru-cache/) | groupcache `lru/lru.go` | `Cache` struct with doubly linked list + hash map, by Brad Fitzpatrick |
| [Consistent Hashing](/patterns/consistent-hashing/) | groupcache `consistenthash.go` | Hash ring with virtual nodes for distributed caching |
| [Rate Limiter](/patterns/rate-limiter/) | `x/time/rate` | Token bucket rate limiter in the extended standard library |

## Further Reading

- [Go Source Code (GitHub)](https://github.com/golang/go)
- [Go Runtime Package Docs](https://pkg.go.dev/runtime)
