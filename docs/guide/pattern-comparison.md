---
description: "Head-to-head comparisons of similar patterns — when to pick one over the other."
---

# Pattern Comparison Matrix

Some patterns look alike but serve different purposes. This guide compares commonly confused pairs to help you choose the right tool.

## Cache vs Pool

| Dimension | [LRU Cache](/patterns/lru-cache/) | [Object Pool](/patterns/object-pool/) |
|-----------|-----------|-------------|
| **Purpose** | Speed up repeated lookups | Avoid allocation/GC cost |
| **Eviction** | Least-recently-used out | Returned by user, reused |
| **Content** | Read-only cached values | Mutable, reusable objects |
| **Hit rate** | Depends on access pattern | 100% (pre-allocated) |
| **Example** | DNS cache, HTTP cache | DB connection pool, thread pool |
| **When confused** | If you're "caching" objects to reuse | → that's a pool |

## Arena Allocator vs Free List

| Dimension | [Arena Allocator](/patterns/arena-allocator/) | [Free List](/patterns/free-list/) |
|-----------|-----------------|-----------|
| **Allocation** | O(1) bump pointer | O(1) pop from free chain |
| **Deallocation** | All-at-once only | Individual O(1) return |
| **Fragmentation** | None (contiguous) | Possible (non-contiguous) |
| **Lifetime** | Phase-based (parse, render) | Object-by-object |
| **Example** | Compiler per-query arena | Game entity recycling |
| **When confused** | If you need individual free | → use free list |

## Observer vs Actor Model

| Dimension | [Observer](/patterns/observer/) | [Actor Model](/patterns/actor-model/) |
|-----------|----------|-------------|
| **Communication** | Synchronous callbacks | Asynchronous messages |
| **Coupling** | Shared memory, same thread | Isolated state, any location |
| **Scaling** | Single process | Distributed systems |
| **Failure isolation** | One bad observer blocks all | Actor crashes independently |
| **Example** | DOM events, React state | Erlang/OTP, Akka |
| **When confused** | If observers need isolation | → use actors |

## Skip List vs B+ Tree

| Dimension | [Skip List](/patterns/skip-list/) | [B+ Tree](/patterns/b-plus-tree/) |
|-----------|-----------|---------|
| **Balancing** | Probabilistic (random levels) | Deterministic (splits/merges) |
| **Concurrency** | Lock-free possible | Complex locking |
| **Disk I/O** | Poor (pointer chasing) | Excellent (high fan-out) |
| **Implementation** | Simple (~100 lines) | Complex (~500+ lines) |
| **Example** | Redis sorted sets, LevelDB memtable | MySQL InnoDB, filesystem indexes |
| **When confused** | In-memory sorted data → skip list | On-disk → B+ tree |

## Ring Buffer vs Queue (FIFO)

| Dimension | [Ring Buffer](/patterns/ring-buffer/) | Standard Queue |
|-----------|-------------|------|
| **Capacity** | Fixed, pre-allocated | Dynamic, grows on demand |
| **Overflow** | Overwrites oldest (or blocks) | Allocates more memory |
| **Memory** | O(capacity), no alloc | O(n), may cause GC |
| **Use case** | Bounded buffers, audio streams | Unbounded task queues |
| **Example** | Linux `io_uring`, logging | Message queues, BFS |
| **When confused** | If capacity is known → ring buffer | If unbounded → queue |

## Copy-on-Write vs Double Buffering

| Dimension | [Copy-on-Write](/patterns/copy-on-write/) | [Double Buffering](/patterns/double-buffering/) |
|-----------|---------------|-----------------|
| **Buffer count** | 1 (cloned on write) | 2 (always allocated) |
| **Copy trigger** | On mutation | Never (swap pointers) |
| **Read cost** | O(1) always | O(1) always |
| **Write cost** | O(n) clone on first write | O(write) to back buffer |
| **Memory** | O(n) only when written | O(2n) always |
| **Example** | Linux fork(), Rc\<T\> | GPU rendering, game loops |
| **When confused** | If writes are rare → CoW | If writes are continuous → double buffer |

## Circuit Breaker vs Rate Limiter

| Dimension | [Circuit Breaker](/patterns/circuit-breaker/) | [Rate Limiter](/patterns/rate-limiter/) |
|-----------|-----------------|-------------|
| **Protects** | Caller from broken downstream | Server from excess traffic |
| **Trigger** | Failure count threshold | Request count threshold |
| **Direction** | Outbound (your calls to others) | Inbound (others' calls to you) |
| **Recovery** | Auto-recover after timeout | Refill tokens over time |
| **Example** | Microservice → database | API gateway, login attempts |
| **When confused** | Protecting yourself → circuit breaker | Protecting your server → rate limiter |

## State Machine vs Strategy/Vtable

| Dimension | [State Machine](/patterns/state-machine/) | [Vtable](/patterns/vtable/) |
|-----------|---------------|--------|
| **Dispatch by** | Current state | Object type |
| **Transitions** | Explicit, guarded | Not applicable |
| **State count** | Changes at runtime | Fixed at compile time |
| **Validation** | "Can this transition happen?" | "Which implementation to call?" |
| **Example** | TCP connection states | Trait objects, interfaces |
| **When confused** | If behavior changes over time → state machine | If it varies by type → vtable |

## Bloom Filter vs Hash Set

| Dimension | [Bloom Filter](/patterns/bloom-filter/) | Hash Set |
|-----------|-------------|----------|
| **False positives** | Yes (tunable) | No |
| **False negatives** | No | No |
| **Memory** | ~10 bits/element | ~50+ bytes/element |
| **Delete** | Not supported | O(1) |
| **Use case** | "Definitely not in set" fast check | Exact membership |
| **Example** | Chrome Safe Browsing, LSM read filter | Deduplication, visited URLs |
| **When confused** | If 1% false positive is OK + memory matters | → Bloom filter |

## Write-Ahead Log vs Checkpointing

| Dimension | [Write-Ahead Log](/patterns/write-ahead-log/) | [Checkpointing](/patterns/checkpointing/) |
|-----------|-----------------|---------------|
| **Granularity** | Every operation | Periodic snapshot |
| **Recovery** | Replay from last checkpoint | Load snapshot + replay remaining WAL |
| **Disk usage** | Grows unbounded (without truncation) | Fixed per snapshot |
| **Write cost** | O(1) append per op | O(state size) per snapshot |
| **Together?** | **Yes** — WAL provides durability | Checkpoint limits replay length |
| **Example** | PostgreSQL WAL, Redis AOF | PostgreSQL base backup, Redis RDB |

## Choosing the Right Pattern: Decision Flowchart

```text
Need to store/retrieve data?
├── Fixed set of flags? → Bitmask
├── Ordered access needed?
│   ├── In memory? → Skip List
│   └── On disk? → B+ Tree
├── Approximate membership? → Bloom Filter
├── Key-value with eviction? → LRU Cache
└── FIFO with fixed capacity? → Ring Buffer

Need to manage concurrency?
├── Limit concurrent access? → Semaphore
├── Producer faster than consumer? → Backpressure
├── Shared data, rare writes? → Copy-on-Write
├── Multiple writers, no blocking? → MVCC
└── Independent actors? → Actor Model

Need resilience?
├── Downstream failing? → Circuit Breaker
├── Too many requests? → Rate Limiter
├── Transient errors? → Retry with Backoff
└── Need crash recovery? → WAL + Checkpointing

Need memory efficiency?
├── Many identical objects? → Flyweight / Interning
├── Reuse expensive objects? → Object Pool
├── Phase-based allocation? → Arena Allocator
└── Recycle fixed-size slots? → Free List
```
