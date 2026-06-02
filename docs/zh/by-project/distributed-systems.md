# 分布式系统中的模式

| 模式 | 项目 | 位置 | 作用 |
|------|------|------|------|
| [环形缓冲区](/zh/patterns/ring-buffer/) | LMAX Disruptor | `RingBuffer.java` | 每秒 600 万笔订单的核心数据结构 |
| [批处理](/zh/patterns/batch-processing/) | Apache Kafka | `RecordAccumulator.java` | 按分区累积记录为批次提升吞吐 |
| [熔断器](/zh/patterns/circuit-breaker/) | Netflix Hystrix | `HystrixCircuitBreaker.java` | 微服务弹性的三态熔断器 |
| [熔断器](/zh/patterns/circuit-breaker/) | Sony gobreaker | `gobreaker.go` | 带代计数器防过期检测的 Go 熔断器 |
| [背压](/zh/patterns/backpressure/) | Reactive Streams | `Subscription.java` | `request(n)` 拉模型流控规范 |
| [预写日志](/zh/patterns/write-ahead-log/) | etcd | `wal.go` | Raft 共识 WAL——分布式状态的事实来源 |
| [预写日志](/zh/patterns/write-ahead-log/) | PostgreSQL | `xlog.c` | 事务 WAL 用于崩溃恢复、复制、PITR |
| [MVCC](/zh/patterns/mvcc/) | PostgreSQL | `heapam_visibility.c` | `HeapTupleSatisfiesMVCC` — 快照隔离可见性检查 |
| [MVCC](/zh/patterns/mvcc/) | etcd | `kvstore.go` | 多版本键值存储，驱动 Kubernetes 配置 |
| [一致性哈希](/zh/patterns/consistent-hashing/) | groupcache | `consistenthash.go` | 带虚拟副本的哈希环，用于分布式缓存 |
| [Actor 模型](/zh/patterns/actor-model/) | Akka | `Actor.scala` | `trait Actor` — JVM 上的消息驱动并发 |
| [Actor 模型](/zh/patterns/actor-model/) | Erlang/OTP | `erl_process.h` | BEAM VM 进程结构体 — 带信箱的轻量级 Actor |
| [限流器](/zh/patterns/rate-limiter/) | Nginx | `ngx_http_limit_req_module.c` | HTTP 请求的漏桶限流 |
