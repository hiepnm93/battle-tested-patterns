# Patterns from Distributed Systems

High-throughput messaging and trading systems push throughput patterns to the extreme.

| Pattern | Project | Where | What It Does |
|---------|---------|-------|--------------|
| [Ring Buffer](/patterns/ring-buffer/) | LMAX Disruptor | `RingBuffer.java` | Core data structure — 6M orders/sec at LMAX Exchange |
| [Batch Processing](/patterns/batch-processing/) | Apache Kafka | `RecordAccumulator.java` | Accumulate records into batches per partition for throughput |
| [Circuit Breaker](/patterns/circuit-breaker/) | Netflix Hystrix | `HystrixCircuitBreaker.java` | Three-state circuit breaker for microservice resilience |
| [Circuit Breaker](/patterns/circuit-breaker/) | Sony gobreaker | `gobreaker.go` | Go circuit breaker with generation-based staleness detection |
| [Backpressure](/patterns/backpressure/) | Reactive Streams | `Subscription.java` | `request(n)` pull-based flow control specification |
| [Write-Ahead Log](/patterns/write-ahead-log/) | etcd | `wal.go` | Raft consensus WAL — source of truth for distributed state |
| [Write-Ahead Log](/patterns/write-ahead-log/) | PostgreSQL | `xlog.c` | Transaction WAL for crash recovery, replication, PITR |
| [MVCC](/patterns/mvcc/) | PostgreSQL | `heapam_visibility.c` | `HeapTupleSatisfiesMVCC` — snapshot isolation visibility check |
| [MVCC](/patterns/mvcc/) | etcd | `kvstore.go` | Multi-version key-value store powering Kubernetes config |
| [Consistent Hashing](/patterns/consistent-hashing/) | groupcache | `consistenthash.go` | Hash ring with virtual replicas for distributed caching |
| [Actor Model](/patterns/actor-model/) | Akka | `Actor.scala` | `trait Actor` — message-driven concurrency for JVM |
| [Actor Model](/patterns/actor-model/) | Erlang/OTP | `erl_process.h` | BEAM VM process struct — lightweight actor with mailbox |
| [Rate Limiter](/patterns/rate-limiter/) | Nginx | `ngx_http_limit_req_module.c` | Leaky bucket rate limiting for HTTP requests |

## Further Reading

- [LMAX Disruptor (GitHub)](https://github.com/LMAX-Exchange/disruptor) · [Apache Kafka (GitHub)](https://github.com/apache/kafka)
- [Netflix Hystrix (GitHub)](https://github.com/Netflix/Hystrix) · [etcd (GitHub)](https://github.com/etcd-io/etcd)
