# All Patterns

46 production-proven patterns organized by category. Each one has interactive visualization, multi-language implementations, exercises, and precise source links.

## Data Structures

| Pattern | One-Liner | Sources |
|---------|-----------|---------|
| [Bitmask](./bitmask/) | Pack N flags into one integer, O(1) test any combo | React, Linux |
| [Min Heap](./min-heap/) | O(1) peek at highest priority, O(log n) push/pop | React, Linux CFS |
| [Ring Buffer](./ring-buffer/) | Fixed-size FIFO, wraps around, zero allocation | LMAX, Linux |
| [Trie](./trie/) | O(k) prefix lookup, shared prefixes share nodes | Linux FIB, Redis |
| [Skip List](./skip-list/) | Probabilistic O(log n) sorted structure | Redis, LevelDB |
| [Bloom Filter](./bloom-filter/) | Probabilistic set membership, zero false negatives | LevelDB, Chromium |
| [LRU Cache](./lru-cache/) | Evict least recently used, O(1) get/put | groupcache, Linux |
| [B+ Tree](./b-plus-tree/) | High-branching tree, leaf-linked for range scans | PostgreSQL, SQLite |
| [Tagged Union](./tagged-union/) | Type tag + union for safe multi-type dispatch | Godot, PyTorch |
| [Merkle Tree](./merkle-tree/) | Hash upward for O(log n) integrity proof | Git, ZFS |
| [Merge Iterator](./merge-iterator/) | K-way merge via min-heap | LevelDB, RocksDB |

## Concurrency

| Pattern | One-Liner | Sources |
|---------|-----------|---------|
| [Semaphore](./semaphore/) | Counter limits concurrent access | Linux, Go |
| [Actor Model](./actor-model/) | Private state + mailbox, no shared memory | Akka, Erlang |
| [Work Stealing](./work-stealing/) | Idle threads steal from busy queues | Go, Tokio |
| [MVCC](./mvcc/) | Versioned rows let readers never block writers | PostgreSQL, etcd |
| [Cooperative Scheduling](./cooperative-scheduling/) | Yield between work chunks to stay responsive | React, Go |
| [Double Buffering](./double-buffering/) | Swap two copies for atomic update | React Fiber, GPU |
| [Backpressure](./backpressure/) | Slow producer when consumer can't keep up | Node.js, Reactive |
| [Event Loop](./event-loop/) | Single-threaded I/O multiplexing | libuv, Redis |
| [Logical Clock](./logical-clock/) | Order events without wall-clock time | etcd, LevelDB |

## System

| Pattern | One-Liner | Sources |
|---------|-----------|---------|
| [Circuit Breaker](./circuit-breaker/) | Stop calling failing services, fail fast | Hystrix, gobreaker |
| [Rate Limiter](./rate-limiter/) | Token bucket controls throughput | Go, Nginx |
| [Retry with Backoff](./retry-backoff/) | Exponential delay + jitter on failure | K8s, gRPC |
| [Write-Ahead Log](./write-ahead-log/) | Log changes before applying, crash-safe | etcd, PostgreSQL |
| [Batch Processing](./batch-processing/) | Accumulate ops, execute as group | Kafka, React |
| [Consistent Hashing](./consistent-hashing/) | Add/remove nodes remaps ~1/n keys | groupcache, HAProxy |
| [Dependency Graph](./dependency-graph/) | DAG + topological sort | Cargo, pnpm |
| [Middleware Chain](./middleware-chain/) | Composable pre/post handlers | gRPC, Koa |
| [Registry](./registry/) | Self-register by name, discover at runtime | TensorFlow, gRPC |
| [Dirty Flag](./dirty-flag/) | Recompute only when marked changed | Chromium, React |
| [LSM Tree](./lsm-tree/) | Buffer writes in memory, flush sorted to disk | LevelDB, RocksDB |
| [Checkpointing](./checkpointing/) | Periodic snapshot, recover from checkpoint | PostgreSQL, Redis |

## Memory

| Pattern | One-Liner | Sources |
|---------|-----------|---------|
| [Object Pool](./object-pool/) | Pre-allocate and reuse to skip GC | Go sync.Pool, Godot |
| [Flyweight](./flyweight/) | Share identical immutable objects | Python int cache, V8 |
| [Arena Allocator](./arena-allocator/) | Bump-allocate in region, free all at once | bumpalo, Go |
| [Free List](./free-list/) | O(1) alloc/free via linked freed slots | Go runtime, Linux |
| [Copy-on-Write](./copy-on-write/) | Share by reference, copy on mutation | Git, Rust Cow |
| [Reference Counting](./reference-counting/) | Auto-cleanup at zero owners | CPython, Rust Arc |
| [Tombstone](./tombstone/) | Mark deleted, reclaim later | LevelDB, Cassandra |
| [Interning](./interning/) | Deduplicate immutable values, pointer equality | Rust compiler, CPython |

## Behavioral

| Pattern | One-Liner | Sources |
|---------|-----------|---------|
| [State Machine](./state-machine/) | Explicit states, impossible transitions unrepresentable | XState, Linux TCP |
| [Observer](./observer/) | Subscribe to events, decouple producer/consumer | EventEmitter, Redux |
| [Iterator](./iterator/) | Lazy sequences, zero intermediate allocations | Rust, Python |
| [Diff / Patch](./diff-patch/) | Compute minimal changes between two states | React, Git |
| [Vtable](./vtable/) | Function pointer struct for polymorphism | Linux kernel, CPython |
| [Visitor](./visitor/) | Dispatch type-specific callbacks on tree nodes | LLVM, Vue |
