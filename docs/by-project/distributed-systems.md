---
title: "Pattern trong các hệ phân tán"
description: "Pattern hệ phân tán: ring buffer (LMAX Disruptor), consistent hashing, WAL, MVCC và circuit breaker."
---

# Pattern trong các hệ phân tán

Các hệ thống nhắn tin và giao dịch throughput cao đẩy các pattern throughput tới mức cực hạn.

| Pattern | Dự án | Tại đâu | Tác dụng |
|---------|---------|-------|--------------|
| [Ring Buffer](/patterns/ring-buffer/) | LMAX Disruptor | [`RingBuffer.java`](https://github.com/LMAX-Exchange/disruptor/blob/c871ca49826a6be7ada6957f6fbafcfecf7b1f87/src/main/java/com/lmax/disruptor/RingBuffer.java#L84-L130) | Cấu trúc dữ liệu cốt lõi — 6M lệnh/giây tại LMAX Exchange |
| [Batch Processing](/patterns/batch-processing/) | Apache Kafka | [`RecordAccumulator.java`](https://github.com/apache/kafka/blob/b7b1c0a83d856766390ee0c05e33b63711eee80e/clients/src/main/java/org/apache/kafka/clients/producer/internals/RecordAccumulator.java#L69-L120) | Gom record thành lô theo partition để tăng throughput |
| [Circuit Breaker](/patterns/circuit-breaker/) | Netflix Hystrix | [`HystrixCircuitBreaker.java`](https://github.com/Netflix/Hystrix/blob/5ce3bc58c38e7ca60ef2fe0e516e390e294ad941/hystrix-core/src/main/java/com/netflix/hystrix/HystrixCircuitBreaker.java#L138-L289) | Circuit breaker 3 trạng thái cho phục hồi microservice |
| [Circuit Breaker](/patterns/circuit-breaker/) | Sony gobreaker | [`gobreaker.go`](https://github.com/sony/gobreaker/blob/fed8e9eb35f9cd3e5c2a67842c924346c3e1fbdd/gobreaker.go#L117-L131) | Circuit breaker Go với phát hiện cũ dựa trên generation |
| [Backpressure](/patterns/backpressure/) | Reactive Streams | [`Subscription.java`](https://github.com/reactive-streams/reactive-streams-jvm/blob/a625d3aba756e9842ad1291a5b73f5db280b6168/api/src/main/java/org/reactivestreams/Subscription.java#L14-L37) | Spec kiểm soát luồng kiểu pull `request(n)` |
| [Write-Ahead Log](/patterns/write-ahead-log/) | etcd | [`wal.go`](https://github.com/etcd-io/etcd/blob/e9b62f804766edf77cfa918d600cb6fb2c56b401/server/storage/wal/wal.go#L72-L95) | WAL đồng thuận Raft — nguồn sự thật cho state phân tán |
| [Write-Ahead Log](/patterns/write-ahead-log/) | PostgreSQL | [`xlog.c`](https://github.com/postgres/postgres/blob/e18b0cb7344cb4bd28468f6c0aeeb9b9241d30aa/src/backend/access/transam/xlog.c#L783-L1128) | WAL transaction để khôi phục crash, replication, PITR |
| [MVCC](/patterns/mvcc/) | PostgreSQL | [`heapam_visibility.c`](https://github.com/postgres/postgres/blob/e18b0cb7344cb4bd28468f6c0aeeb9b9241d30aa/src/backend/access/heap/heapam_visibility.c#L917-L1096) | `HeapTupleSatisfiesMVCC` — kiểm tra hiển thị cô lập theo snapshot |
| [MVCC](/patterns/mvcc/) | etcd | [`kvstore.go`](https://github.com/etcd-io/etcd/blob/e9b62f804766edf77cfa918d600cb6fb2c56b401/server/storage/mvcc/kvstore.go#L53-L135) | Kho key-value đa phiên bản chạy config Kubernetes |
| [Consistent Hashing](/patterns/consistent-hashing/) | groupcache | [`consistenthash.go`](https://github.com/golang/groupcache/blob/2c02b8208cf8c02a3e358cb1d9b60950647543fc/consistenthash/consistenthash.go#L28-L81) | Vòng hash với virtual replica cho cache phân tán |
| [Actor Model](/patterns/actor-model/) | Akka | [`Actor.scala`](https://github.com/akka/akka-core/blob/aded7b67a9dafcb32b8a5dc95f6debce3a97c0e9/akka-actor/src/main/scala/akka/actor/Actor.scala#L476-L547) | `trait Actor` — concurrency hướng thông điệp cho JVM |
| [Actor Model](/patterns/actor-model/) | Erlang/OTP | [`erl_process.h`](https://github.com/erlang/otp/blob/c75602432b4eff922bcaf4a175144dc61adbd6d6/erts/emulator/beam/erl_process.h#L1043-L1205) | Struct process BEAM VM — actor nhẹ với mailbox |
| [Rate Limiter](/patterns/rate-limiter/) | Nginx | [`ngx_http_limit_req_module.c`](https://github.com/nginx/nginx/blob/d994f5b8220847eb8f7e4400be5f7e6eb4538e46/src/http/modules/ngx_http_limit_req_module.c#L405-L532) | Leaky bucket rate limiting cho request HTTP |
| [Logical Clock](/patterns/logical-clock/) | etcd | [`mvcc/revision.go`](https://github.com/etcd-io/etcd/blob/e9b62f804766edf77cfa918d600cb6fb2c56b401/server/storage/mvcc/revision.go) | Bộ đếm revision tăng dần để sắp xếp sự kiện qua cluster |
| [Logical Clock](/patterns/logical-clock/) | LevelDB | [`db_impl.cc` sequence number](https://github.com/google/leveldb/blob/7ee830d02b623e8ffe0b95d59a74db1e58da04c5/db/db_impl.cc#L1311-L1337) | Sequence number sắp xếp mọi thao tác ghi không cần wall-clock |
| [Retry Backoff](/patterns/retry-backoff/) | Kubernetes | [`backoff.go`](https://github.com/kubernetes/kubernetes/blob/586cc904093af4fe7492e564908a796f0b107f97/staging/src/k8s.io/apimachinery/pkg/util/wait/backoff.go#L30-L50) | Backoff khởi động lại pod, retry API server với delay tăng cấp số nhân |
| [Tombstone](/patterns/tombstone/) | Cassandra | [Tombstone markers](https://github.com/apache/cassandra) | Marker xoá trong việc lan truyền xoá phân tán |
| [LSM Tree](/patterns/lsm-tree/) | LevelDB | [`db_impl.cc`](https://github.com/google/leveldb/blob/7ee830d02b623e8ffe0b95d59a74db1e58da04c5/db/db_impl.cc#L1241-L1368) | Đệm ghi trong bộ nhớ, flush thành file đã sắp xếp, compaction ở background |
| [Checkpointing](/patterns/checkpointing/) | PostgreSQL | [`checkpointer.c`](https://github.com/postgres/postgres/blob/e18b0cb7344cb4bd28468f6c0aeeb9b9241d30aa/src/backend/postmaster/checkpointer.c#L218-L360) | Snapshot state định kỳ giới hạn thời gian replay WAL khi khôi phục |

## Cách chúng kết hợp: Một thao tác ghi phân tán

Khi client ghi một key vào database phân tán như etcd, các pattern móc nối nhau qua toàn bộ đường đi:

<CompositionFlow variant="distributed-write" />

Các pattern tạo thành một pipeline bền vững: rate limit bảo vệ hệ thống, consistent hashing định tuyến request, WAL đảm bảo bền vững, logical clock sắp xếp sự kiện, MVCC cung cấp cô lập và checkpoint giới hạn thời gian khôi phục.

## Đọc thêm

- [LMAX Disruptor (GitHub)](https://github.com/LMAX-Exchange/disruptor) · [Apache Kafka (GitHub)](https://github.com/apache/kafka)
- [Netflix Hystrix (GitHub)](https://github.com/Netflix/Hystrix) · [etcd (GitHub)](https://github.com/etcd-io/etcd)
