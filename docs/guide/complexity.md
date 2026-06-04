---
description: "Big-O complexity reference for all 46 patterns — key operations, time & space at a glance."
---

# Complexity Cheat Sheet

Quick reference for time and space complexity of every pattern's key operations. Use this to compare trade-offs before choosing a pattern.

## How to Read This

- **n** = number of elements / items
- **k** = key length (for string-keyed structures)
- **m** = number of hash functions (Bloom filter)
- **L** = number of levels (skip list, LSM tree)
- Amortized costs marked with **(amort.)**

## Data Structures

| Pattern | Insert | Lookup | Delete | Space | Notes |
|---------|--------|--------|--------|-------|-------|
| [Bitmask](/patterns/bitmask/) | O(1) | O(1) | O(1) | O(1) | Fixed-size; limited to word width (32/64 flags) |
| [Ring Buffer](/patterns/ring-buffer/) | O(1) | O(1) | O(1) | O(n) | Fixed capacity; overwrites oldest on full |
| [Tagged Union](/patterns/tagged-union/) | — | O(1) | — | O(max variant) | Dispatch by tag; no dynamic allocation |
| [Min Heap](/patterns/min-heap/) | O(log n) | O(1) peek | O(log n) | O(n) | O(1) min access; used for priority queues |
| [Trie](/patterns/trie/) | O(k) | O(k) | O(k) | O(n × k) | Independent of total entries; prefix queries O(k + results) |
| [Bloom Filter](/patterns/bloom-filter/) | O(m) | O(m) | ✗ | O(n) | Probabilistic; false positives possible, no false negatives |
| [LRU Cache](/patterns/lru-cache/) | O(1) | O(1) | O(1) | O(n) | Hash map + doubly linked list |
| [Skip List](/patterns/skip-list/) | O(log n) avg | O(log n) avg | O(log n) avg | O(n) | Probabilistic balancing; range queries supported |
| [B+ Tree](/patterns/b-plus-tree/) | O(log n) | O(log n) | O(log n) | O(n) | Disk-optimized; high fan-out minimizes I/O |
| [Merkle Tree](/patterns/merkle-tree/) | O(log n) | O(log n) | O(log n) | O(n) | Verification O(log n) proofs |
| [Merge Iterator](/patterns/merge-iterator/) | — | O(log k) next | — | O(k) | k = number of streams; heap-based merge |

## Concurrency

| Pattern | Key Operation | Cost | Space | Notes |
|---------|--------------|------|-------|-------|
| [Semaphore](/patterns/semaphore/) | acquire / release | O(1) | O(1) | Counter-based; may block on contention |
| [Double Buffering](/patterns/double-buffering/) | swap | O(1) | O(2n) | Pointer swap; no copy |
| [Event Loop](/patterns/event-loop/) | enqueue / dequeue | O(1) | O(queue) | Single-threaded; I/O multiplexed |
| [Backpressure](/patterns/backpressure/) | signal / check | O(1) | O(1) | Flow control; often piggybacked on existing channel |
| [Copy-on-Write](/patterns/copy-on-write/) | read | O(1) | O(n) per snapshot | Write triggers O(n) clone; reads never block |
| [Cooperative Scheduling](/patterns/cooperative-scheduling/) | yield | O(1) | O(tasks) | Requires voluntary yield points |
| [MVCC](/patterns/mvcc/) | read / write | O(1) + GC | O(n × versions) | Reads never block; GC cost amortized |
| [Work Stealing](/patterns/work-stealing/) | push / steal | O(1) amort. | O(tasks) | Lock-free deque; cache-line aware |
| [Actor Model](/patterns/actor-model/) | send message | O(1) | O(actors × mailbox) | Isolated state; no shared memory |
| [Logical Clock](/patterns/logical-clock/) | tick / merge | O(1) Lamport, O(n) Vector | O(1) / O(n) | Vector clock grows with node count |

## System

| Pattern | Key Operation | Cost | Space | Notes |
|---------|--------------|------|-------|-------|
| [State Machine](/patterns/state-machine/) | transition | O(1) | O(states) | Constant-time dispatch; explicit states |
| [Circuit Breaker](/patterns/circuit-breaker/) | call / check | O(1) | O(1) | Counter + timer; 3 states |
| [Rate Limiter](/patterns/rate-limiter/) | allow? | O(1) | O(1) per limiter | Token bucket or sliding window |
| [Retry with Backoff](/patterns/retry-backoff/) | retry | O(retries) total | O(1) | Exponential delay + jitter |
| [Batch Processing](/patterns/batch-processing/) | flush | O(batch) | O(batch) | Amortizes per-item overhead |
| [Middleware Chain](/patterns/middleware-chain/) | execute | O(middlewares) | O(middlewares) | Linear pipeline; each handler O(1) |
| [Registry](/patterns/registry/) | register / lookup | O(1) hash | O(n) | String-keyed service locator |
| [Dirty Flag](/patterns/dirty-flag/) | check / mark | O(1) | O(1) | Boolean guard; skip unchanged |
| [Dependency Graph](/patterns/dependency-graph/) | topo sort | O(V + E) | O(V + E) | DAG; detects cycles |
| [Consistent Hashing](/patterns/consistent-hashing/) | lookup node | O(log n) | O(n × vnodes) | Binary search on ring; minimal reshuffling |
| [Write-Ahead Log](/patterns/write-ahead-log/) | append | O(1) amort. | O(log size) | Sequential writes; fsync for durability |
| [Checkpointing](/patterns/checkpointing/) | snapshot | O(state size) | O(state size) | Periodic; truncates WAL |
| [LSM Tree](/patterns/lsm-tree/) | write / read | O(1) write, O(L) read | O(n) | Write-optimized; compaction in background |

## Memory

| Pattern | Allocate | Free | Lookup | Space | Notes |
|---------|----------|------|--------|-------|-------|
| [Object Pool](/patterns/object-pool/) | O(1) | O(1) | — | O(pool size) | Pre-allocated; avoids GC pressure |
| [Flyweight](/patterns/flyweight/) | — | — | O(1) | O(unique) | Share identical instances |
| [Arena Allocator](/patterns/arena-allocator/) | O(1) bump | O(1) bulk | — | O(arena size) | Bump pointer; free all at once |
| [Free List](/patterns/free-list/) | O(1) | O(1) | — | O(n) | Linked list of freed slots |
| [Copy-on-Write](/patterns/copy-on-write/) | O(1) share | O(n) on write | O(1) | O(n) per snapshot | Deferred copy |
| [Reference Counting](/patterns/reference-counting/) | O(1) clone | O(1) drop | — | O(1) per ref | Deterministic; no cycles |
| [Tombstone](/patterns/tombstone/) | — | O(1) mark | O(1) | O(n + deleted) | Soft delete; compacted later |
| [Interning](/patterns/interning/) | O(k) first, O(1) after | — | O(1) | O(unique × k) | Hash-based dedup; compare by pointer |

## Behavioral

| Pattern | Key Operation | Cost | Space | Notes |
|---------|--------------|------|-------|-------|
| [Observer](/patterns/observer/) | notify | O(subscribers) | O(subscribers) | Fan-out; order may vary |
| [Iterator](/patterns/iterator/) | next | O(1) per step | O(1) | Lazy evaluation; pull-based |
| [Diff / Patch](/patterns/diff-patch/) | diff | O(n × m) Myers | O(n + m) | Minimal edit distance |
| [Vtable](/patterns/vtable/) | dispatch | O(1) | O(methods) | Pointer indirection; static resolution |
| [Visitor](/patterns/visitor/) | visit | O(nodes) | O(tree depth) | Double dispatch; traversal + operation |

## Key Trade-offs Summary

| If you need... | Choose | Trade-off |
|---------------|--------|-----------|
| O(1) lookup + O(1) eviction | [LRU Cache](/patterns/lru-cache/) | Extra memory for doubly linked list |
| O(1) writes at scale | [LSM Tree](/patterns/lsm-tree/) | Read amplification (multiple levels) |
| O(1) membership test | [Bloom Filter](/patterns/bloom-filter/) | False positives (no false negatives) |
| O(1) allocation | [Arena](/patterns/arena-allocator/) or [Free List](/patterns/free-list/) | No individual free (arena) or fragmentation (free list) |
| O(log n) sorted access | [Skip List](/patterns/skip-list/) or [B+ Tree](/patterns/b-plus-tree/) | Skip list simpler, B+ tree disk-optimized |
| Zero-copy reads | [Copy-on-Write](/patterns/copy-on-write/) or [MVCC](/patterns/mvcc/) | Write amplification on mutation |
| Minimal rehash on scale | [Consistent Hashing](/patterns/consistent-hashing/) | Virtual nodes add memory overhead |
