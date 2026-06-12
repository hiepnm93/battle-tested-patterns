---
title: "Các trường hợp sử dụng"
description: "Tìm pattern phù hợp theo kịch bản — web API, database, hệ phân tán, frontend, compiler và hơn thế nữa."
---

# Các trường hợp sử dụng

Tìm pattern theo loại hệ thống bạn đang xây.

## Web API & Microservice

Đang xây service REST/gRPC? Các pattern này giúp nó tin cậy dưới tải.

| Kịch bản | Pattern | Ví dụ thực tế |
|---|---|---|
| Bảo vệ khi downstream gặp sự cố | [Circuit Breaker](/patterns/circuit-breaker/) + [Retry with Backoff](/patterns/retry-backoff/) | Netflix Hystrix bọc mọi cuộc gọi HTTP client |
| Rate limit API | [Rate Limiter](/patterns/rate-limiter/) | Stripe cho phép burst 25, refill ở 25/giây |
| Middleware request (auth, log, tracing) | [Middleware Chain](/patterns/middleware-chain/) | Interceptor gRPC, mô hình hành tây Koa.js |
| Khám phá service | [Registry](/patterns/registry/) | Đăng ký service Consul, etcd |
| Phân tán tải qua các node | [Consistent Hashing](/patterns/consistent-hashing/) | HAProxy, phân tán key groupcache |
| Tránh quá tải | [Backpressure](/patterns/backpressure/) + [Batch Processing](/patterns/batch-processing/) | Pipe stream Node.js, consumer group Kafka |

## Database & lưu trữ

Các pattern đằng sau PostgreSQL, Redis, LevelDB và mọi storage engine nghiêm túc.

| Kịch bản | Pattern | Ví dụ thực tế |
|---|---|---|
| Khôi phục sau crash | [WAL](/patterns/write-ahead-log/) + [Checkpointing](/patterns/checkpointing/) | PostgreSQL: WAL + checkpoint định kỳ |
| Tải nặng ghi | [LSM Tree](/patterns/lsm-tree/) + [Bloom Filter](/patterns/bloom-filter/) | LevelDB/RocksDB: memtable → SSTable + bloom bỏ qua |
| Truy vấn khoảng trên đĩa | [B+ Tree](/patterns/b-plus-tree/) | Chỉ mục btree PostgreSQL, SQLite |
| Đọc/ghi đồng thời | [MVCC](/patterns/mvcc/) | Versioning tuple PostgreSQL, revision etcd |
| Xác minh toàn vẹn dữ liệu | [Merkle Tree](/patterns/merkle-tree/) | Checksum block ZFS, kho object Git |
| Gộp key đã sắp xếp | [Merge Iterator](/patterns/merge-iterator/) + [Min Heap](/patterns/min-heap/) | Compaction LevelDB |
| Xoá không xoá ngay | [Tombstone](/patterns/tombstone/) | Tombstone Cassandra, marker xoá LevelDB |
| Sorted set trong bộ nhớ | [Skip List](/patterns/skip-list/) | Sorted set ZADD/ZRANGE Redis |
| Cache trong bộ nhớ | [LRU Cache](/patterns/lru-cache/) | LRU eviction Redis, Go groupcache |
| Sắp xếp sự kiện không có đồng hồ | [Logical Clock](/patterns/logical-clock/) | Raft log etcd, version vector DynamoDB |

## Frontend & framework UI

React, Vue và browser engine dùng các pattern này mỗi frame.

| Kịch bản | Pattern | Ví dụ thực tế |
|---|---|---|
| Diff virtual DOM | [Diff / Patch](/patterns/diff-patch/) + [Bitmask](/patterns/bitmask/) | Reconciler React: diff cây, áp patch tối thiểu |
| Render phản hồi nhanh | [Cooperative Scheduling](/patterns/cooperative-scheduling/) | React Scheduler: yield mỗi 5ms để giữ dưới 16ms |
| Update state an toàn theo frame | [Double Buffering](/patterns/double-buffering/) | React Fiber: hoán đổi workInProgress ↔ current tree |
| Tránh re-render không cần | [Dirty Flag](/patterns/dirty-flag/) | shouldComponentUpdate React, layout Chromium |
| Quản lý state | [Observer](/patterns/observer/) + [State Machine](/patterns/state-machine/) | subscribe Redux, trạng thái hữu hạn XState |
| Lập lịch task theo ưu tiên | [Min Heap](/patterns/min-heap/) | Queue ưu tiên React Scheduler |

## Hệ phân tán

Pattern cho hệ thống trải qua nhiều máy.

| Kịch bản | Pattern | Ví dụ thực tế |
|---|---|---|
| Log đồng thuận | [WAL](/patterns/write-ahead-log/) + [Logical Clock](/patterns/logical-clock/) | Raft etcd: log append-only với term/index |
| Định tuyến chịu phân vùng | [Consistent Hashing](/patterns/consistent-hashing/) | Amazon DynamoDB, vòng Cassandra |
| State replicated | [State Machine](/patterns/state-machine/) + [WAL](/patterns/write-ahead-log/) | Raft: replicated state machine qua log |
| Replication không xung đột | [Logical Clock](/patterns/logical-clock/) + [Tombstone](/patterns/tombstone/) | CRDT, last-write-wins kiểu Dynamo |
| Đồng bộ dữ liệu | [Merkle Tree](/patterns/merkle-tree/) | Anti-entropy repair Cassandra |
| Kiến trúc hướng thông điệp | [Actor Model](/patterns/actor-model/) + [Backpressure](/patterns/backpressure/) | Cluster Akka, Erlang/OTP |
| Pipeline build/deploy | [Dependency Graph](/patterns/dependency-graph/) + [Batch Processing](/patterns/batch-processing/) | Đồ thị build Cargo, workspace pnpm |

## Runtime & quản lý bộ nhớ

Cách Go, CPython, V8 và game engine quản lý bộ nhớ và thực thi.

| Kịch bản | Pattern | Ví dụ thực tế |
|---|---|---|
| Giảm áp lực GC | [Object Pool](/patterns/object-pool/) + [Free List](/patterns/free-list/) | Go sync.Pool, allocator SLUB Linux |
| Cấp phát theo pha | [Arena Allocator](/patterns/arena-allocator/) | Rust bumpalo, Go arena (thử nghiệm) |
| Dọn dẹp xác định | [Reference Counting](/patterns/reference-counting/) | refcount CPython, Rust Rc/Arc |
| Khử trùng lặp chuỗi | [Interning](/patterns/interning/) + [Flyweight](/patterns/flyweight/) | Symbol interning của Rust compiler, cache số nguyên nhỏ Python |
| Clone hiệu quả | [Copy-on-Write](/patterns/copy-on-write/) | Linux fork(), Rust `Cow<T>` |
| Phân tán việc qua các core | [Work Stealing](/patterns/work-stealing/) | Scheduler P/M/G Go runtime, Tokio |
| Ghép kênh I/O | [Event Loop](/patterns/event-loop/) + [Ring Buffer](/patterns/ring-buffer/) | libuv (Node.js), Redis single-thread |
| Counter thread-safe | [Semaphore](/patterns/semaphore/) | Semaphore kernel Linux, Go x/sync |

## Compiler & công cụ ngôn ngữ

Pattern dùng trong LLVM, V8, rustc và compiler Vue/React.

| Kịch bản | Pattern | Ví dụ thực tế |
|---|---|---|
| Duyệt AST | [Visitor](/patterns/visitor/) | LLVM InstVisitor, biến đổi compiler Vue |
| Dispatch động | [Vtable](/patterns/vtable/) | Slot tp_* CPython, Rust dyn Trait |
| Bảng symbol | [Interning](/patterns/interning/) + [Trie](/patterns/trie/) | Symbol interning rustc |
| Biến đổi IR | [Iterator](/patterns/iterator/) + [Diff / Patch](/patterns/diff-patch/) | Adapter Iterator Rust, edit tree-sitter |
| Biểu diễn kiểu | [Tagged Union](/patterns/tagged-union/) | Con trỏ có tag V8, TensorImpl PyTorch |
| Hệ thống plugin | [Registry](/patterns/registry/) + [Middleware Chain](/patterns/middleware-chain/) | Plugin Babel, loader webpack |

## Mạng & giao thức

| Kịch bản | Pattern | Ví dụ thực tế |
|---|---|---|
| Theo dõi trạng thái kết nối | [State Machine](/patterns/state-machine/) | State machine TCP Linux (SYN_SENT → ESTABLISHED → ...) |
| Định tuyến IP | [Trie](/patterns/trie/) | LC-trie cho FIB IPv4 Linux |
| Đệm gói tin | [Ring Buffer](/patterns/ring-buffer/) | sk_buff Linux, ring DPDK |
| Kiểm soát luồng | [Backpressure](/patterns/backpressure/) + [Rate Limiter](/patterns/rate-limiter/) | Flow control TCP, Nginx limit_req |
| Phân giải DNS | [Trie](/patterns/trie/) + [LRU Cache](/patterns/lru-cache/) | Tra cứu tên miền + cache response |
