---
description: "Duyệt toàn bộ 46 pattern lập trình đã được kiểm chứng theo nhóm: cấu trúc dữ liệu, concurrency, hệ thống, bộ nhớ và hành vi."
---

# Tất cả các Pattern

46 pattern đã được chứng minh trong production, phân theo nhóm. Mỗi cái đều có trực quan hoá tương tác, triển khai đa ngôn ngữ, bài tập và liên kết nguồn chính xác.

## Cấu trúc dữ liệu

| Pattern | Mô tả ngắn | Nguồn |
|---------|-----------|---------|
| [Bitmask](./bitmask/) | Nhồi N flag vào một số nguyên, kiểm tra mọi tổ hợp O(1) | React, Linux |
| [Min Heap](./min-heap/) | Peek phần tử ưu tiên cao nhất O(1), push/pop O(log n) | React, Linux CFS |
| [Ring Buffer](./ring-buffer/) | FIFO kích thước cố định, vòng quanh, không cấp phát | LMAX, Linux |
| [Trie](./trie/) | Tra cứu prefix O(k), các prefix chung dùng chung node | Linux FIB, Redis |
| [Skip List](./skip-list/) | Cấu trúc sắp xếp O(log n) theo xác suất | Redis, LevelDB |
| [Bloom Filter](./bloom-filter/) | Thành viên tập theo xác suất, không âm tính giả | LevelDB, Chromium |
| [LRU Cache](./lru-cache/) | Loại bỏ cái ít dùng nhất, get/put O(1) | groupcache, Linux |
| [B+ Tree](./b-plus-tree/) | Cây branching cao, lá liên kết để quét theo khoảng | PostgreSQL, SQLite |
| [Tagged Union](./tagged-union/) | Tag kiểu + union cho dispatch đa kiểu an toàn | Godot, PyTorch |
| [Merkle Tree](./merkle-tree/) | Hash lên trên cho bằng chứng toàn vẹn O(log n) | Git, ZFS |
| [Merge Iterator](./merge-iterator/) | Gộp K-luồng qua min-heap | LevelDB, RocksDB |

## Concurrency

| Pattern | Mô tả ngắn | Nguồn |
|---------|-----------|---------|
| [Semaphore](./semaphore/) | Bộ đếm giới hạn truy cập đồng thời | Linux, Go |
| [Actor Model](./actor-model/) | State riêng + mailbox, không bộ nhớ chung | Akka, Erlang |
| [Work Stealing](./work-stealing/) | Thread rảnh lấy việc từ queue bận | Go, Tokio |
| [MVCC](./mvcc/) | Row có phiên bản giúp reader không bao giờ chặn writer | PostgreSQL, etcd |
| [Cooperative Scheduling](./cooperative-scheduling/) | Yield giữa các khối để giữ phản hồi nhanh | React, Go |
| [Double Buffering](./double-buffering/) | Hoán đổi hai bản sao để cập nhật nguyên tử | React Fiber, GPU |
| [Backpressure](./backpressure/) | Làm chậm producer khi consumer không theo kịp | Node.js, Reactive |
| [Event Loop](./event-loop/) | Ghép kênh I/O đơn luồng | libuv, Redis |
| [Logical Clock](./logical-clock/) | Sắp xếp sự kiện không cần wall-clock | etcd, LevelDB |

## Hệ thống

| Pattern | Mô tả ngắn | Nguồn |
|---------|-----------|---------|
| [Circuit Breaker](./circuit-breaker/) | Ngừng gọi service đang lỗi, fail nhanh | Hystrix, gobreaker |
| [Rate Limiter](./rate-limiter/) | Token bucket điều tiết throughput | Go, Nginx |
| [Retry with Backoff](./retry-backoff/) | Delay cấp số nhân + jitter khi thất bại | K8s, gRPC |
| [Write-Ahead Log](./write-ahead-log/) | Log thay đổi trước khi áp dụng, an toàn khi crash | etcd, PostgreSQL |
| [Batch Processing](./batch-processing/) | Gom thao tác, thực thi theo nhóm | Kafka, React |
| [Consistent Hashing](./consistent-hashing/) | Thêm/bớt node chỉ remap ~1/n key | groupcache, HAProxy |
| [Dependency Graph](./dependency-graph/) | DAG + sắp xếp topo | Cargo, pnpm |
| [Middleware Chain](./middleware-chain/) | Handler trước/sau có thể ghép | gRPC, Koa |
| [Registry](./registry/) | Tự đăng ký theo tên, khám phá lúc runtime | TensorFlow, gRPC |
| [Dirty Flag](./dirty-flag/) | Chỉ tính lại khi được đánh dấu đã đổi | Chromium, React |
| [LSM Tree](./lsm-tree/) | Đệm ghi trong bộ nhớ, flush sắp xếp ra đĩa | LevelDB, RocksDB |
| [Checkpointing](./checkpointing/) | Snapshot định kỳ, khôi phục từ checkpoint | PostgreSQL, Redis |

## Bộ nhớ

| Pattern | Mô tả ngắn | Nguồn |
|---------|-----------|---------|
| [Object Pool](./object-pool/) | Cấp phát trước và tái dùng để bỏ qua GC | Go sync.Pool, Godot |
| [Flyweight](./flyweight/) | Chia sẻ các object bất biến giống nhau | Cache int Python, V8 |
| [Arena Allocator](./arena-allocator/) | Cấp phát bump trong vùng, giải phóng tất cả một lần | bumpalo, Go |
| [Free List](./free-list/) | Cấp/giải phóng O(1) qua slot đã giải phóng liên kết | Go runtime, Linux |
| [Copy-on-Write](./copy-on-write/) | Chia sẻ qua tham chiếu, copy khi sửa | Git, Rust Cow |
| [Reference Counting](./reference-counting/) | Tự dọn dẹp khi không còn chủ sở hữu | CPython, Rust Arc |
| [Tombstone](./tombstone/) | Đánh dấu đã xoá, thu hồi sau | LevelDB, Cassandra |
| [Interning](./interning/) | Khử trùng lặp giá trị bất biến, so sánh bằng con trỏ | Compiler Rust, CPython |

## Hành vi

| Pattern | Mô tả ngắn | Nguồn |
|---------|-----------|---------|
| [State Machine](./state-machine/) | Trạng thái rõ ràng, chuyển tiếp bất hợp lệ không biểu diễn được | XState, Linux TCP |
| [Observer](./observer/) | Đăng ký sự kiện, tách rời producer/consumer | EventEmitter, Redux |
| [Iterator](./iterator/) | Chuỗi lười, không cấp phát trung gian | Rust, Python |
| [Diff / Patch](./diff-patch/) | Tính thay đổi tối thiểu giữa hai state | React, Git |
| [Vtable](./vtable/) | Struct con trỏ hàm cho đa hình | Nhân Linux, CPython |
| [Visitor](./visitor/) | Dispatch callback đặc thù kiểu trên node cây | LLVM, Vue |
