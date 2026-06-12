---
title: "Thêm các dự án khác"
description: "Thêm pattern từ PostgreSQL, Redis, Kafka, LLVM, Chromium, V8 và các dự án mã nguồn mở đáng chú ý khác."
---

# Thêm các dự án khác

Pattern từ database, hệ sinh thái JVM, trình duyệt và các dự án mã nguồn mở đáng chú ý khác.

## Database & lưu trữ

| Pattern | Dự án | Ở đâu | Tác dụng |
|---------|---------|-------|--------------|
| [MVCC](/patterns/mvcc/) | PostgreSQL | [`heapam_visibility.c`](https://github.com/postgres/postgres/blob/e18b0cb7344cb4bd28468f6c0aeeb9b9241d30aa/src/backend/access/heap/heapam_visibility.c#L917-L1096) | `HeapTupleSatisfiesMVCC` — kiểm tra hiển thị cô lập snapshot |
| [Write-Ahead Log](/patterns/write-ahead-log/) | PostgreSQL | [`xlog.c`](https://github.com/postgres/postgres/blob/e18b0cb7344cb4bd28468f6c0aeeb9b9241d30aa/src/backend/access/transam/xlog.c#L783-L1128) | WAL transaction cho khôi phục crash, replication, PITR |
| [MVCC](/patterns/mvcc/) | etcd | [`kvstore.go`](https://github.com/etcd-io/etcd/blob/e9b62f804766edf77cfa918d600cb6fb2c56b401/server/storage/mvcc/kvstore.go#L53-L135) | KV store đa phiên bản chạy config Kubernetes |
| [Write-Ahead Log](/patterns/write-ahead-log/) | etcd | [`wal.go`](https://github.com/etcd-io/etcd/blob/e9b62f804766edf77cfa918d600cb6fb2c56b401/server/storage/wal/wal.go#L72-L95) | WAL đồng thuận Raft cho state phân tán |
| [LRU Cache](/patterns/lru-cache/) | Redis | [`evict.c`](https://github.com/redis/redis/blob/df63a65d4d4ee33ae67e9f101885074febe0bccb/src/evict.c#L55-L83) | LRU xấp xỉ với pool loại bỏ dựa trên lấy mẫu |
| [Trie](/patterns/trie/) | Redis | [`rax.c` / `rax.h`](https://github.com/redis/redis/blob/df63a65d4d4ee33ae67e9f101885074febe0bccb/src/rax.h#L80-L130) | Radix tree RAX cho Stream và khoảng key đã sắp xếp |
| [Skip List](/patterns/skip-list/) | Redis | [`t_zset.c`](https://github.com/redis/redis/blob/df63a65d4d4ee33ae67e9f101885074febe0bccb/src/t_zset.c#L70-L130) | Triển khai sorted set với cân bằng theo xác suất |
| [Bloom Filter](/patterns/bloom-filter/) | LevelDB | [`bloom.cc`](https://github.com/google/leveldb/blob/7ee830d02b623e8ffe0b95d59a74db1e58da04c5/util/bloom.cc#L17-L80) | Bloom filter cấp block để bỏ qua đọc đĩa không cần |
| [Skip List](/patterns/skip-list/) | LevelDB | [`skiplist.h`](https://github.com/google/leveldb/blob/7ee830d02b623e8ffe0b95d59a74db1e58da04c5/db/skiplist.h#L40-L90) | Memtable lock-free với con trỏ next nguyên tử |
| [Arena Allocator](/patterns/arena-allocator/) | LevelDB | [`arena.cc`](https://github.com/google/leveldb/blob/7ee830d02b623e8ffe0b95d59a74db1e58da04c5/util/arena.cc) | Arena dựa trên block cho cấp phát memtable |
| [Merge Iterator](/patterns/merge-iterator/) | LevelDB | [`merger.cc`](https://github.com/google/leveldb/blob/7ee830d02b623e8ffe0b95d59a74db1e58da04c5/table/merger.cc#L17-L100) | `MergingIterator` gộp các iterator đã sắp xếp (memtable + tầng SSTable) thành một view sắp xếp duy nhất |
| [LSM Tree](/patterns/lsm-tree/) | LevelDB | [`db_impl.cc`](https://github.com/google/leveldb/blob/7ee830d02b623e8ffe0b95d59a74db1e58da04c5/db/db_impl.cc#L1241-L1368) | `DBImpl::Write` — ghi batch vào WAL, chèn vào memtable, flush sang SST khi đạt ngưỡng |
| [Merge Iterator](/patterns/merge-iterator/) | RocksDB | [`merge_helper.cc`](https://github.com/facebook/rocksdb/blob/7affaee1c49ebc80cb213ad86fe7d2a3ad447da2/db/merge_helper.cc#L87-L156) | `TimedFullMerge` kết hợp nhiều phiên bản của cùng key khi compaction |
| [LSM Tree](/patterns/lsm-tree/) | RocksDB | [`memtable.cc`](https://github.com/facebook/rocksdb/blob/7affaee1c49ebc80cb213ad86fe7d2a3ad447da2/db/memtable.cc#L458-L534) | `MemTable::Add` — memtable nền skip-list, flush sang L0 SST khi đầy |
| [B+ Tree](/patterns/b-plus-tree/) | PostgreSQL | [`nbtinsert.c`](https://github.com/postgres/postgres/blob/e18b0cb7344cb4bd28468f6c0aeeb9b9241d30aa/src/backend/access/nbtree/nbtinsert.c#L22-L55) | B-link tree (biến thể Lehman-Yao) — mọi bảng và index đều nền B+ tree trên các page đĩa |
| [B+ Tree](/patterns/b-plus-tree/) | SQLite | [`btreeInt.h`](https://github.com/sqlite/sqlite/blob/2cb57d9d4ac7eac3b1d15cfa71511f54817cb3e4/src/btreeInt.h#L190-L198) | Cell nội chứa con trỏ page con + key; cell lá chứa payload. Tách page qua `balance_nonroot()` |
| [Merkle Tree](/patterns/merkle-tree/) | ZFS (OpenZFS) | [`blkptr.c`](https://github.com/openzfs/zfs/blob/7e054b2e7ea80c7c838f7fd44b7d517eea5c9d18/module/zfs/blkptr.c#L30-L77) | Checksum block pointer tạo thành Merkle tree từ block dữ liệu tới uberblock để phát hiện hư hỏng âm thầm |
| [Checkpointing](/patterns/checkpointing/) | PostgreSQL | [`checkpointer.c`](https://github.com/postgres/postgres/blob/e18b0cb7344cb4bd28468f6c0aeeb9b9241d30aa/src/backend/postmaster/checkpointer.c#L218-L360) | `CheckpointerMain` — flush buffer dirty, ghi bản ghi checkpoint WAL, cập nhật `pg_control` |
| [Checkpointing](/patterns/checkpointing/) | Redis | [`rdb.c`](https://github.com/redis/redis/blob/df63a65d4d4ee33ae67e9f101885074febe0bccb/src/rdb.c#L1414-L1529) | `rdbSaveRio` — fork process con để ghi snapshot RDB tại thời điểm mà không chặn main thread |

## Hệ sinh thái JVM

| Pattern | Dự án | Ở đâu | Tác dụng |
|---------|---------|-------|--------------|
| [Actor Model](/patterns/actor-model/) | Akka | [`Actor.scala`](https://github.com/akka/akka-core/blob/aded7b67a9dafcb32b8a5dc95f6debce3a97c0e9/akka-actor/src/main/scala/akka/actor/Actor.scala#L476-L547) | `trait Actor` — concurrency hướng thông điệp cho JVM |
| [Circuit Breaker](/patterns/circuit-breaker/) | Netflix Hystrix | [`HystrixCircuitBreaker.java`](https://github.com/Netflix/Hystrix/blob/5ce3bc58c38e7ca60ef2fe0e516e390e294ad941/hystrix-core/src/main/java/com/netflix/hystrix/HystrixCircuitBreaker.java#L138-L289) | Circuit breaker 3 trạng thái cho phục hồi microservice |
| [Batch Processing](/patterns/batch-processing/) | Apache Kafka | [`RecordAccumulator.java`](https://github.com/apache/kafka/blob/b7b1c0a83d856766390ee0c05e33b63711eee80e/clients/src/main/java/org/apache/kafka/clients/producer/internals/RecordAccumulator.java#L69-L120) | Gom record thành lô theo partition |
| [Work Stealing](/patterns/work-stealing/) | OpenJDK | [`ForkJoinPool.java`](https://github.com/openjdk/jdk/blob/4b3ec455c85314d051800a8f46dd8f5c93881e3a/src/java.base/share/classes/java/util/concurrent/ForkJoinPool.java) | Method `scan` với work stealing ngẫu nhiên |
| [LRU Cache](/patterns/lru-cache/) | Guava | [`CacheBuilder`](https://github.com/google/guava/blob/3e65944ec9207ca652128969fd1334e9920dde07/guava/src/com/google/common/cache/CacheBuilder.java) | `maximumSize()` với loại bỏ LRU |
| [Rate Limiter](/patterns/rate-limiter/) | Guava | [`RateLimiter`](https://github.com/google/guava/blob/3e65944ec9207ca652128969fd1334e9920dde07/guava/src/com/google/common/util/concurrent/RateLimiter.java) | Token bucket smooth bursty / warm-up |
| [Consistent Hashing](/patterns/consistent-hashing/) | groupcache | [`consistenthash.go`](https://github.com/golang/groupcache/blob/2c02b8208cf8c02a3e358cb1d9b60950647543fc/consistenthash/consistenthash.go#L28-L81) | Vòng hash với virtual replica (do Brad Fitzpatrick viết) |

## Erlang / BEAM VM

| Pattern | Dự án | Ở đâu | Tác dụng |
|---------|---------|-------|--------------|
| [Actor Model](/patterns/actor-model/) | Erlang/OTP | [`erl_process.h`](https://github.com/erlang/otp/blob/c75602432b4eff922bcaf4a175144dc61adbd6d6/erts/emulator/beam/erl_process.h#L1043-L1205) | Struct process BEAM VM — actor nhẹ với mailbox |
| [Cooperative Scheduling](/patterns/cooperative-scheduling/) | Erlang/OTP | [BEAM scheduler](https://github.com/erlang/otp/blob/c75602432b4eff922bcaf4a175144dc61adbd6d6/erts/emulator/beam/erl_process.c) | Preemption dựa trên reduction cho hàng triệu process |
| [Semaphore](/patterns/semaphore/) | Erlang/OTP | [`erl_process_lock.c`](https://github.com/erlang/otp/blob/c75602432b4eff922bcaf4a175144dc61adbd6d6/erts/emulator/beam/erl_process_lock.c) | Khoá process cho truy cập đồng thời an toàn |

## Trình duyệt & web

| Pattern | Dự án | Ở đâu | Tác dụng |
|---------|---------|-------|--------------|
| [Bloom Filter](/patterns/bloom-filter/) | Chromium | [`selector_filter.h`](https://github.com/chromium/chromium/blob/5cffea3f665b7762369a0fa84d2f208875e7225e/third_party/blink/renderer/core/css/selector_filter.h#L149-L175) | Bloom filter selector CSS — bỏ qua 60-70% rule |
| [Bitmask](/patterns/bitmask/) | React | [`ReactFiberFlags.js`](https://github.com/facebook/react/blob/34b78a2897cc208260a88e6b62ecaf9ca2a9dfe4/packages/react-reconciler/src/ReactFiberFlags.js#L14-L36) | Flag tác dụng Fiber — `Placement`, `Update`, `Deletion` |
| [Double Buffering](/patterns/double-buffering/) | React | [Kiến trúc Fiber](https://github.com/facebook/react/blob/34b78a2897cc208260a88e6b62ecaf9ca2a9dfe4/packages/react-reconciler/src/ReactFiber.js#L327-L355) | Hoán đổi cây current vs work-in-progress khi commit |
| [Diff / Patch](/patterns/diff-patch/) | React | [`ReactChildFiber.js`](https://github.com/facebook/react/blob/34b78a2897cc208260a88e6b62ecaf9ca2a9dfe4/packages/react-reconciler/src/ReactChildFiber.js#L1169-L1340) | Reconciliation danh sách với match theo key |

## Hạ tầng & cloud

| Pattern | Dự án | Ở đâu | Tác dụng |
|---------|---------|-------|--------------|
| [Retry Backoff](/patterns/retry-backoff/) | Kubernetes | [`backoff.go`](https://github.com/kubernetes/kubernetes/blob/586cc904093af4fe7492e564908a796f0b107f97/staging/src/k8s.io/apimachinery/pkg/util/wait/backoff.go#L30-L50) | Backoff khởi động lại pod, retry API server |
| [Retry Backoff](/patterns/retry-backoff/) | gRPC-Go | [`internal/backoff/backoff.go`](https://github.com/grpc/grpc-go/blob/f1864955bbb48efa131f6652933fa8b2189d9305/internal/backoff/backoff.go#L56-L75) | Backoff kết nối cấp số nhân với jitter |
| [Dependency Graph](/patterns/dependency-graph/) | Terraform | [Resource graph](https://github.com/hashicorp/terraform) | Apply resource song song theo thứ tự DAG |
| [Dependency Graph](/patterns/dependency-graph/) | Bazel | [Action graph](https://github.com/bazelbuild/bazel) | Thực thi topo các target build |
| [Registry](/patterns/registry/) | gRPC-Go | [`server.go`](https://github.com/grpc/grpc-go/blob/f1864955bbb48efa131f6652933fa8b2189d9305/server.go#L154-L170) | `RegisterService` thêm mô tả service vào map service của server để dispatch method RPC |
| [Registry](/patterns/registry/) | TensorFlow | [`op.h`](https://github.com/tensorflow/tensorflow/blob/b4c7e9a660badf8c8c81075fe9f781d23ed6f28a/tensorflow/core/framework/op.h#L258-L290) | Macro `REGISTER_OP` đăng ký operation vào `OpRegistry` toàn cục để xây computation graph |
| [Consistent Hashing](/patterns/consistent-hashing/) | Nginx | [`ngx_http_upstream_hash`](https://github.com/nginx/nginx/blob/d994f5b8220847eb8f7e4400be5f7e6eb4538e46/src/http/modules/ngx_http_upstream_hash_module.c) | Cân bằng tải upstream với hashing ketama |

## Compiler & runtime ngôn ngữ

| Pattern | Dự án | Ở đâu | Tác dụng |
|---------|---------|-------|--------------|
| [Visitor](/patterns/visitor/) | LLVM | [`InstVisitor.h`](https://github.com/llvm/llvm-project/blob/1dc53bacd24fb555dfd2ec030a5ee33f5db3fadf/llvm/include/llvm/IR/InstVisitor.h#L45-L107) | Visitor CRTP dispatch theo opcode lệnh IR cho các pass tối ưu |
| [Visitor](/patterns/visitor/) | Vue.js | [`transforms/vIf.ts`](https://github.com/vuejs/core/blob/48ad452dd61926a59e358da3c74c5ef750ae21c4/packages/compiler-core/src/transforms/vIf.ts#L35-L60) | `transformIf` là một visitor `NodeTransform` đi qua AST template |
| [Vtable](/patterns/vtable/) | CPython | [`object.h`](https://github.com/python/cpython/blob/ff64d8de66ab7f8e56b5d410796a7d76c955280c/Include/cpython/object.h#L250-L340) | Vtable `PyTypeObject` — `tp_repr`, `tp_hash`, `tp_call`, bộ protocol |
| [Interning](/patterns/interning/) | CPython | [`unicodeobject.c`](https://github.com/python/cpython/blob/ff64d8de66ab7f8e56b5d410796a7d76c955280c/Objects/unicodeobject.c#L15575-L15631) | `PyUnicode_InternInPlace` — intern chuỗi identifier cho tra cứu dict O(1) |
| [Interning](/patterns/interning/) | Rust (rustc) | [`symbol.rs`](https://github.com/rust-lang/rust/blob/ab26b175979ee7b2cb3302dce204b99df96f7efb/compiler/rustc_span/src/symbol.rs#L24-L79) | `Symbol` là index `u32` vào interner toàn cục — mọi identifier đều intern |
| [Tagged Union](/patterns/tagged-union/) | Godot Engine | [`variant.h`](https://github.com/godotengine/godot/blob/ec67cbe92628bdaf979b10594359ba6f02cf8838/core/variant/variant.h#L78-L120) | Enum `Variant::Type` + union — mọi giá trị GDScript đều là một `Variant` |
| [Tagged Union](/patterns/tagged-union/) | PyTorch | [`ivalue.h`](https://github.com/pytorch/pytorch/blob/cef26d1e97fcb9dd61b4471f9bd7fa9a32bd42b9/aten/src/ATen/core/ivalue.h#L51-L96) | `IValue` chứa enum `Tag` + union `Payload` cho interpreter TorchScript |

## Đọc thêm

- [PostgreSQL (GitHub)](https://github.com/postgres/postgres) · [Redis (GitHub)](https://github.com/redis/redis) · [LevelDB (GitHub)](https://github.com/google/leveldb)
- [Akka (GitHub)](https://github.com/akka/akka) · [Erlang/OTP (GitHub)](https://github.com/erlang/otp)
- [Kubernetes (GitHub)](https://github.com/kubernetes/kubernetes) · [gRPC (GitHub)](https://github.com/grpc/grpc-go)
