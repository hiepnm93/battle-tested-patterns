---
title: "Các pattern liên kết với nhau như thế nào"
description: "Cách 46 pattern liên kết: chuỗi kết hợp, các khối xây dựng chung và các tổ hợp pattern trong thực tế."
---

# Các pattern liên kết với nhau như thế nào

Các pattern này không tồn tại đơn lẻ. Insight thú vị nhất là cách các hệ thống production **kết hợp** chúng lại với nhau.

**Khám phá tương tác** — click vào hệ thống bất kỳ để xem nó dùng pattern nào và vì sao:

<PatternConnectionsViz />

## Chuỗi kết hợp

Insight mạnh nhất không phải là pattern nào tồn tại — mà là cách chúng **móc nối** trong các hệ thống thực.

### React Reconciler: Từ Flag tới Frame

```text
Bitmask          → flag mã hoá việc cần làm
    ↓
Dirty Flag       → bỏ qua subtree không đổi
    ↓
Min Heap         → chọn việc ưu tiên cao nhất trước
    ↓
Cooperative Scheduling → yield mỗi 5ms để tránh giật
    ↓
Diff / Patch     → tính thay đổi cây tối thiểu
    ↓
Double Buffering → xây workInProgress tree, hoán đổi nguyên tử
    ↓
Batch Processing → flush mọi update state trong một commit
```

### PostgreSQL: Từ ghi tới khôi phục

```text
Write-Ahead Log  → mọi thay đổi được log trước khi áp dụng
    ↓
Checkpointing    → snapshot định kỳ giới hạn replay khi crash
    ↓
B+ Tree          → index tối ưu cho đĩa cho truy vấn khoảng
    ↓
MVCC             → reader thấy snapshot nhất quán, không bao giờ chặn writer
    ↓
LRU Cache        → buffer pool giữ page nóng trong bộ nhớ
    ↓
Bloom Filter     → bỏ qua tra index với key không có
```

### Kafka Broker: Từ Producer tới Consumer

```text
Batch Processing → gom thông điệp, fsync theo nhóm
    ↓
Write-Ahead Log  → segment log append-only trên đĩa
    ↓
Ring Buffer      → queue event I/O kích thước cố định
    ↓
Backpressure     → consumer chậm tín hiệu cho producer điều tiết
    ↓
Consistent Hashing → gán partition qua các broker
    ↓
Tombstone        → compaction log loại bỏ bản ghi lỗi thời
```

### Go Runtime: Lập lịch + Bộ nhớ

```text
Work Stealing    → P rảnh lấy goroutine từ queue của P bận
    ↓
Semaphore        → GOMAXPROCS giới hạn số thread OS đồng thời
    ↓
Object Pool      → sync.Pool tái chế object hay cấp phát
    ↓
Free List        → mspan theo dõi slot tự do trong size class
    ↓
Arena Allocator  → stack frame cấp phát kiểu bump pointer
    ↓
Copy-on-Write    → slice append chỉ copy khi vượt capacity
```

## Bức tranh lớn hơn

Hiểu từng pattern riêng lẻ là hữu ích. Hiểu cách chúng **kết hợp** là điều phân biệt kỹ sư senior với junior.

Khi gặp vấn đề hiệu năng, bạn không nghĩ "tôi cần một bitmask." Bạn nghĩ "tôi cần theo dõi nhiều trạng thái với chi phí thấp (bitmask), bỏ qua việc không đổi (flag cho subtree), xử lý việc tăng dần (cooperative scheduling), ưu tiên việc gấp (min heap) và tránh cấp phát trên hot path (double buffering)."

Đó là cái mà team React đã xây. Đó là điều Redis, Go, Linux, PostgreSQL và Kafka đều thể hiện. Cùng những pattern đó kết hợp lại theo các cấu hình khác nhau để giải các bài toán khác nhau.

## Tóm tắt: Pattern xuyên các hệ thống

| Pattern | React | Redis | Go Runtime | Linux | PostgreSQL | Kafka |
|---------|:-----:|:-----:|:----------:|:-----:|:----------:|:-----:|
| [**Bitmask**](/patterns/bitmask/) | ✅ | | ✅ | ✅ | | |
| [**Min Heap**](/patterns/min-heap/) | ✅ | | ✅ | ✅ | | |
| [**Cooperative Scheduling**](/patterns/cooperative-scheduling/) | ✅ | | ✅ | | | |
| [**Diff / Patch**](/patterns/diff-patch/) | ✅ | | | | | |
| [**Double Buffering**](/patterns/double-buffering/) | ✅ | | | | | |
| [**Batch Processing**](/patterns/batch-processing/) | ✅ | ✅ | | ✅ | | ✅ |
| [**Dirty Flag**](/patterns/dirty-flag/) | ✅ | | | | | |
| [**Observer**](/patterns/observer/) | ✅ | | | | | |
| [**Skip List**](/patterns/skip-list/) | | ✅ | | | | |
| [**LRU Cache**](/patterns/lru-cache/) | | ✅ | ✅ | | ✅ | |
| [**Trie**](/patterns/trie/) | | ✅ | | ✅ | | |
| [**Bloom Filter**](/patterns/bloom-filter/) | | | | | ✅ | |
| [**Work Stealing**](/patterns/work-stealing/) | | | ✅ | | | |
| [**Free List**](/patterns/free-list/) | | | ✅ | ✅ | | |
| [**Semaphore**](/patterns/semaphore/) | | | ✅ | ✅ | | |
| [**Object Pool**](/patterns/object-pool/) | | | ✅ | | | |
| [**Flyweight**](/patterns/flyweight/) | | | ✅ | | | |
| [**Rate Limiter**](/patterns/rate-limiter/) | | | ✅ | ✅ | | |
| [**Arena Allocator**](/patterns/arena-allocator/) | | | ✅ | | | |
| [**State Machine**](/patterns/state-machine/) | | | | ✅ | | |
| [**Ring Buffer**](/patterns/ring-buffer/) | | | | ✅ | | ✅ |
| [**Backpressure**](/patterns/backpressure/) | | | | ✅ | | ✅ |
| [**Vtable**](/patterns/vtable/) | | | | ✅ | | |
| [**Reference Counting**](/patterns/reference-counting/) | | | | ✅ | | |
| [**Copy-on-Write**](/patterns/copy-on-write/) | | ✅ | ✅ | ✅ | | |
| [**Tombstone**](/patterns/tombstone/) | | | | | | ✅ |
| [**MVCC**](/patterns/mvcc/) | | | | | ✅ | |
| [**Write-Ahead Log**](/patterns/write-ahead-log/) | | | | | ✅ | ✅ |
| [**B+ Tree**](/patterns/b-plus-tree/) | | | | ✅ | ✅ | |
| [**Checkpointing**](/patterns/checkpointing/) | | ✅ | | | ✅ | |
| [**Event Loop**](/patterns/event-loop/) | | ✅ | ✅ | ✅ | | |
| [**Iterator**](/patterns/iterator/) | ✅ | | ✅ | | | |
| [**Tagged Union**](/patterns/tagged-union/) | ✅ | | ✅ | | | |
| [**Retry Backoff**](/patterns/retry-backoff/) | | | | | | ✅ |
| [**Consistent Hashing**](/patterns/consistent-hashing/) | | | ✅ | | | ✅ |

### Pattern neo trong các hệ thống khác

11 pattern còn lại sống chủ yếu trong các hệ thống ngoài sáu cái phía trên:

| Pattern | Hệ thống chính |
|---------|----------------|
| [**LSM Tree**](/patterns/lsm-tree/) | LevelDB, RocksDB — engine ghi cốt lõi cho các KV store hiện đại |
| [**Merge Iterator**](/patterns/merge-iterator/) | LevelDB, RocksDB — gộp K-luồng trong compaction |
| [**Logical Clock**](/patterns/logical-clock/) | etcd (term/index Raft), LevelDB (sequence number) |
| [**Merkle Tree**](/patterns/merkle-tree/) | Git (toàn vẹn object), ZFS (checksum block) |
| [**Actor Model**](/patterns/actor-model/) | Erlang/OTP, Akka — concurrency truyền thông điệp |
| [**Circuit Breaker**](/patterns/circuit-breaker/) | Netflix Hystrix, gobreaker — phục hồi trong microservice |
| [**Middleware Chain**](/patterns/middleware-chain/) | Interceptor gRPC-Go, mô hình hành tây Koa.js |
| [**Registry**](/patterns/registry/) | TensorFlow (op registry), gRPC-Go (đăng ký service) |
| [**Dependency Graph**](/patterns/dependency-graph/) | Cargo (phân giải build), pnpm (lập lịch workspace) |
| [**Visitor**](/patterns/visitor/) | LLVM (InstVisitor), compiler Vue (biến đổi AST) |
| [**Interning**](/patterns/interning/) | rustc (interning symbol), CPython (cache string/int) |
