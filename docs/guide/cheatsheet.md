---
title: "Cheat Sheet"
description: "Thẻ tham chiếu nhanh cho cả 46 pattern đã kiểm chứng — độ phức tạp, khi nào dùng và chỉ dẫn chọn theo bài toán."
---

# Cheat Sheet

Tham chiếu một trang cho cả 46 pattern. In ra, đánh dấu, hoặc ctrl-F để tìm trong đây.

## Chọn theo bài toán

Chưa rõ cần pattern nào? Bắt đầu từ đây.

| Tôi cần... | Hãy dùng | Vì sao |
|---|---|---|
| Giới hạn truy cập đồng thời | [Semaphore](/patterns/semaphore/) | Dùng bộ đếm, đã chứng minh trong kernel OS |
| Xử lý consumer chậm | [Backpressure](/patterns/backpressure/) | Đừng bỏ — đẩy ngược lại |
| Cache có loại bỏ | [LRU Cache](/patterns/lru-cache/) | get/put O(1), tự loại cái nguội nhất |
| Tra cứu tiền tố nhanh | [Trie](/patterns/trie/) | O(k) theo độ dài key, không phụ thuộc kích thước tập |
| Kiểm tra có-thể-thuộc-tập | [Bloom Filter](/patterns/bloom-filter/) | Không âm tính giả, ít bộ nhớ |
| Truy vấn khoảng đã sắp xếp | [B+ Tree](/patterns/b-plus-tree/) hoặc [Skip List](/patterns/skip-list/) | B+ Tree cho đĩa, Skip List cho bộ nhớ |
| Ghi an toàn khi crash | [WAL](/patterns/write-ahead-log/) + [Checkpointing](/patterns/checkpointing/) | Log-trước-rồi-apply + snapshot định kỳ |
| Chặn lỗi lan truyền | [Circuit Breaker](/patterns/circuit-breaker/) | Fail nhanh, khôi phục dần |
| Retry cuộc gọi thất bại | [Retry with Backoff](/patterns/retry-backoff/) | Delay theo cấp số nhân + jitter |
| Kiểm soát throughput | [Rate Limiter](/patterns/rate-limiter/) | Token bucket, refill đều |
| Xác minh toàn vẹn dữ liệu | [Merkle Tree](/patterns/merkle-tree/) | Bằng chứng O(log n) qua chuỗi hash |
| Giảm bộ nhớ qua chia sẻ | [Flyweight](/patterns/flyweight/) hoặc [Interning](/patterns/interning/) | Chia sẻ giá trị bất biến |
| Tránh áp lực GC | [Object Pool](/patterns/object-pool/) hoặc [Arena](/patterns/arena-allocator/) | Tái sử dụng hoặc giải phóng hàng loạt |
| Phát hiện thay đổi rẻ | [Dirty Flag](/patterns/dirty-flag/) | Bỏ qua tính lại nếu sạch |
| Sắp xếp sự kiện phân tán | [Logical Clock](/patterns/logical-clock/) | Lamport hoặc vector clock |
| Đánh giá lười | [Iterator](/patterns/iterator/) | Kiểu pull, không cấp phát trung gian |
| Xử lý nhiều kiểu | [Tagged Union](/patterns/tagged-union/) hoặc [Vtable](/patterns/vtable/) | Tag cho tập đóng, vtable cho tập mở |
| Tải nặng ghi | [LSM Tree](/patterns/lsm-tree/) | Buffer → flush → merge |
| Ghép middleware | [Middleware Chain](/patterns/middleware-chain/) | Mô hình hành tây, mỗi handler bọc cái kế |
| Cân bằng việc giữa các thread | [Work Stealing](/patterns/work-stealing/) | Rảnh lấy trộm từ bận |
| Theo dõi nhiều flag | [Bitmask](/patterns/bitmask/) | N flag trong một số nguyên |
| Lập lịch theo ưu tiên | [Min Heap](/patterns/min-heap/) | Peek O(1), push/pop O(log n) |
| FIFO kích thước cố định | [Ring Buffer](/patterns/ring-buffer/) | Vòng quanh, không cấp phát |
| Diff tối thiểu giữa hai trạng thái | [Diff / Patch](/patterns/diff-patch/) | Tính + áp dụng thay đổi |
| Tách producer/consumer | [Observer](/patterns/observer/) | Mô hình subscribe |
| Phân bố key qua các node | [Consistent Hashing](/patterns/consistent-hashing/) | Thêm/bớt node remap ~1/n |
| Thứ tự build từ dependency | [Dependency Graph](/patterns/dependency-graph/) | DAG + sắp xếp topo |
| Chuyển trạng thái nguyên tử | [State Machine](/patterns/state-machine/) | Trạng thái rõ ràng, chuyển bất hợp lệ không biểu diễn được |
| Xoá mềm và dọn sau | [Tombstone](/patterns/tombstone/) | Đánh dấu đã xoá, dồn nén sau |
| Chia sẻ với copy khi đổi | [Copy-on-Write](/patterns/copy-on-write/) | Chia sẻ cho đến khi có người ghi |
| Dọn dẹp xác định | [Reference Counting](/patterns/reference-counting/) | Giải phóng khi rc=0, không tạm dừng GC |
| Đăng ký/khám phá service | [Registry](/patterns/registry/) | Map name → handler |
| Hoán đổi trạng thái nguyên tử | [Double Buffering](/patterns/double-buffering/) | Ghi vào back, hoán đổi sang front |
| Đọc không block | [MVCC](/patterns/mvcc/) | Snapshot có phiên bản |
| Main thread phản hồi nhanh | [Cooperative Scheduling](/patterns/cooperative-scheduling/) | Yield giữa các khối |
| I/O đơn luồng | [Event Loop](/patterns/event-loop/) | Ghép kênh không cần thread |
| Tích luỹ rồi flush | [Batch Processing](/patterns/batch-processing/) | Phân bổ chi phí mỗi thao tác |
| Cô lập kiểu actor | [Actor Model](/patterns/actor-model/) | State riêng + truyền thông điệp |
| Dispatch khi duyệt cây | [Visitor](/patterns/visitor/) | Callback đặc thù theo kiểu |
| Cấp phát O(1) từ slot đã giải phóng | [Free List](/patterns/free-list/) | Linked list các block tự do |
| Gộp các luồng đã sắp xếp | [Merge Iterator](/patterns/merge-iterator/) | Gộp k-luồng qua min-heap |

## Tham chiếu độ phức tạp

### Cấu trúc dữ liệu

| Pattern | Thêm | Tra | Xoá | Bộ nhớ | Đánh đổi chính |
|---|---|---|---|---|---|
| [Bitmask](/patterns/bitmask/) | O(1) | O(1) | O(1) | O(1) | Giới hạn số flag bằng độ rộng word |
| [Min Heap](/patterns/min-heap/) | O(log n) | O(1) peek | O(log n) | O(n) | Chỉ peek-min là nhanh |
| [Ring Buffer](/patterns/ring-buffer/) | O(1) | O(1) | O(1) | O(n) cố định | Sức chứa cố định |
| [Trie](/patterns/trie/) | O(k) | O(k) | O(k) | O(SIGMA * n) | Tốn bộ nhớ với key thưa |
| [Skip List](/patterns/skip-list/) | O(log n) trung bình | O(log n) trung bình | O(log n) trung bình | O(n) trung bình | Theo xác suất, đơn giản hơn cây |
| [Bloom Filter](/patterns/bloom-filter/) | O(k) | O(k) | N/A | O(m) bit | Có thể có dương tính giả |
| [LRU Cache](/patterns/lru-cache/) | O(1) | O(1) | O(1) | O(n) | Loại bỏ khi đầy |
| [B+ Tree](/patterns/b-plus-tree/) | O(log n) | O(log n) | O(log n) | O(n) | Tối ưu cho đĩa, fanout cao |
| [Tagged Union](/patterns/tagged-union/) | N/A | O(1) dispatch | N/A | O(variant lớn nhất) | Tập kiểu đóng |
| [Merkle Tree](/patterns/merkle-tree/) | O(log n) | O(log n) | O(log n) | O(n) | Để xác minh, không phải tìm kiếm |
| [Merge Iterator](/patterns/merge-iterator/) | N/A | O(log k) next | N/A | O(k) | k = số luồng |

### Pattern hệ thống

| Pattern | Throughput | Độ trễ | Cách lỗi |
|---|---|---|---|
| [Circuit Breaker](/patterns/circuit-breaker/) | Bình thường khi đóng | +0 đóng, fail-fast khi mở | Chặn mọi cuộc gọi khi mở |
| [Rate Limiter](/patterns/rate-limiter/) | Bị chặn ở tốc độ token | +0 nếu có token | Từ chối quá tải (429) |
| [Retry with Backoff](/patterns/retry-backoff/) | Giảm khi retry | Tăng theo cấp số nhân | Khuếch đại nếu không có jitter |
| [WAL](/patterns/write-ahead-log/) | Tốc độ ghi tuần tự | +1 ghi (log trước) | An toàn — replay từ log |
| [Batch Processing](/patterns/batch-processing/) | Cao hơn (phân bổ) | Cao hơn (chờ lô) | Mất lô khi crash |
| [Consistent Hashing](/patterns/consistent-hashing/) | Như nền bên dưới | +chi phí hash | ~1/n key remap khi đổi node |

### Pattern bộ nhớ

| Pattern | Cấp phát | Giải phóng | Overhead | Tốt nhất cho |
|---|---|---|---|---|
| [Object Pool](/patterns/object-pool/) | O(1) phân bổ | O(1) trả về | Kích thước pool | Object cùng kiểu thay đổi nhiều |
| [Arena Allocator](/patterns/arena-allocator/) | O(1) bump | O(1) hàng loạt | Phí canh chỉnh | Vòng đời theo pha |
| [Free List](/patterns/free-list/) | O(1) | O(1) | Con trỏ next mỗi slot | Block kích thước cố định |
| [Flyweight](/patterns/flyweight/) | O(1) tra | Chia sẻ, không giải phóng | Bảng tra | Nhiều object nhỏ giống nhau |
| [Copy-on-Write](/patterns/copy-on-write/) | O(1) chia sẻ | O(n) khi ghi đầu | Ref count mỗi page | Dữ liệu chia sẻ nặng đọc |
| [Reference Counting](/patterns/reference-counting/) | O(1) clone | O(1) khi rc=0 | Bộ đếm mỗi object | Dọn dẹp xác định |
| [Interning](/patterns/interning/) | O(k) lần đầu, O(1) sau | Pool | Hash table | Khử trùng lặp chuỗi/symbol |

## Bộ combo pattern

Các pattern hiếm khi xuất hiện đơn lẻ. Đây là các combo production phổ biến nhất:

| Combo | Dùng trong | Vì sao kết hợp |
|---|---|---|
| WAL + Checkpointing | PostgreSQL, etcd | WAL cho an toàn, checkpoint giới hạn replay |
| Bloom Filter + LSM Tree | LevelDB, RocksDB | Bỏ qua đọc đĩa không cần |
| Min Heap + Merge Iterator | Compaction LevelDB | Gộp hiệu quả K luồng đã sắp xếp |
| Circuit Breaker + Retry | gRPC, Hystrix | Retry lỗi thoáng qua, ngắt khi kéo dài |
| Rate Limiter + Backpressure | API gateway | Giới hạn đầu vào, tín hiệu quá tải |
| Ring Buffer + Event Loop | libuv, io_uring | Queue kích thước cố định cho event I/O |
| Object Pool + Free List | Go runtime | Pool quản lý slab, free list theo dõi slot |
| MVCC + B+ Tree | PostgreSQL | Row có phiên bản trong index tối ưu cho đĩa |
| Dirty Flag + Double Buffering | React Fiber | Đánh dấu dirty, gom vào frame tiếp theo |
| Bitmask + State Machine | Reconciler React | Flag mã hoá state, chuyển tiếp qua phép bitwise |
| Consistent Hashing + Registry | Service mesh | Hash để định vị, registry để khám phá |
| Trie + Interning | Compiler | Intern chuỗi, tra theo prefix |

## Cây quyết định

### "Cache nào?"

<DecisionTree variant="which-cache" />

### "Chiến lược bộ nhớ nào?"

<DecisionTree variant="which-memory" />

### "Mô hình concurrency nào?"

<DecisionTree variant="which-concurrency" />
