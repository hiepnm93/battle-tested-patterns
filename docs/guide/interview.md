---
title: "Cẩm nang phỏng vấn"
description: "Vượt qua các buổi phỏng vấn system design và coding — 46 pattern ánh xạ tới các chủ đề phỏng vấn kèm câu hỏi mẫu và những thứ người phỏng vấn tìm kiếm."
---

# Cẩm nang phỏng vấn

Các pattern này xuất hiện liên tục trong phỏng vấn system design và coding. Trang này ánh xạ chúng với những câu hỏi bạn thực sự sẽ được hỏi.

## Cách dùng trang này

1. **Tìm chủ đề phỏng vấn** bạn đang chuẩn bị
2. **Đọc các trang pattern** được liên kết trong từng phần (hiểu cơ chế, không chỉ tên gọi)
3. **Chạy trực quan hoá tương tác** — người phỏng vấn rất thích ứng viên biết vẽ và giải thích
4. **Thử các bài tập** — chúng được cấu trúc giống bài coding interview

## Phỏng vấn System Design

### "Thiết kế một Rate Limiter"

Đây là câu hỏi system design phổ biến nhất. Bạn cần:

| Khái niệm | Pattern | Câu nên nói |
|---|---|---|
| Thuật toán token bucket | [Rate Limiter](/patterns/rate-limiter/) | "Tôi sẽ dùng token bucket — nó xử lý burst tới sức chứa trong khi giữ tốc độ refill đều" |
| Rate limit phân tán | [Consistent Hashing](/patterns/consistent-hashing/) | "Với nhiều node, tôi hash IP client tới các instance rate limiter cụ thể để tránh phối hợp giữa các node" |
| Cửa sổ trượt dự phòng | [Ring Buffer](/patterns/ring-buffer/) | "Ring buffer có thể theo dõi timestamp request trong biến thể cửa sổ trượt" |

### "Thiết kế một Cache"

| Khái niệm | Pattern | Câu nên nói |
|---|---|---|
| Chính sách loại bỏ | [LRU Cache](/patterns/lru-cache/) | "LRU với linked list hai chiều + hash map cho get/put/evict O(1)" |
| Chống cache stampede | [Semaphore](/patterns/semaphore/) | "Dùng semaphore để chỉ một request tính giá trị, các request khác chờ" |
| Định tuyến cache phân tán | [Consistent Hashing](/patterns/consistent-hashing/) | "Consistent hashing cho phép thêm/bớt node cache mà không phải tái phân phối toàn bộ" |
| Negative cache | [Bloom Filter](/patterns/bloom-filter/) | "Một Bloom filter ở phía trước tránh tra cache với các key chắc chắn không tồn tại" |

### "Thiết kế một Key-Value Store"

| Khái niệm | Pattern | Câu nên nói |
|---|---|---|
| Đường ghi | [LSM Tree](/patterns/lsm-tree/) | "Ghi vào WAL, rồi memtable. Khi memtable đầy, flush thành SSTable đã sắp xếp trên đĩa" |
| Tối ưu đọc | [Bloom Filter](/patterns/bloom-filter/) | "Mỗi SSTable có một Bloom filter — bỏ qua file chắc chắn không chứa key" |
| Khôi phục sau crash | [WAL](/patterns/write-ahead-log/) + [Checkpointing](/patterns/checkpointing/) | "WAL đảm bảo bền vững. Checkpoint định kỳ giới hạn thời gian khôi phục" |
| Compaction | [Merge Iterator](/patterns/merge-iterator/) | "Gộp k SSTable đã sắp xếp bằng min-heap" |
| Xoá | [Tombstone](/patterns/tombstone/) | "Không thể xoá khỏi SSTable bất biến — ghi một tombstone, dồn nén sau" |

### "Thiết kế một Database phân tán"

| Khái niệm | Pattern | Câu nên nói |
|---|---|---|
| Replication | [WAL](/patterns/write-ahead-log/) + [State Machine](/patterns/state-machine/) | "Raft: replicate các entry WAL, áp vào state machine theo thứ tự" |
| Consistency | [Logical Clock](/patterns/logical-clock/) | "Lamport timestamp cho thứ tự tổng quát, vector clock cho consistency nhân quả" |
| Phân vùng | [Consistent Hashing](/patterns/consistent-hashing/) | "Consistent hashing với virtual node để phân bố đều" |
| Anti-entropy | [Merkle Tree](/patterns/merkle-tree/) | "So sánh root Merkle giữa các replica để tìm điểm khác biệt trong O(log n)" |
| Đọc đồng thời | [MVCC](/patterns/mvcc/) | "Mỗi transaction thấy một snapshot nhất quán — reader không bao giờ chặn writer" |
| Giải quyết xung đột | [Tombstone](/patterns/tombstone/) + [Logical Clock](/patterns/logical-clock/) | "Last-write-wins bằng so sánh vector clock, tombstone cho việc xoá" |

### "Thiết kế một Task Scheduler"

| Khái niệm | Pattern | Câu nên nói |
|---|---|---|
| Hàng đợi ưu tiên | [Min Heap](/patterns/min-heap/) | "Min-heap theo deadline/priority — peek O(1), insert O(log n)" |
| Lập lịch công bằng | [Work Stealing](/patterns/work-stealing/) | "Worker rảnh lấy việc từ queue bận — Go runtime làm đúng như vậy" |
| Cắt thời gian | [Cooperative Scheduling](/patterns/cooperative-scheduling/) | "Mỗi task yield sau một time slice — React Scheduler làm vậy để giữ dưới 16ms" |
| Giới hạn concurrency | [Semaphore](/patterns/semaphore/) | "Semaphore với N permit giới hạn số task chạy đồng thời" |
| Phụ thuộc task | [Dependency Graph](/patterns/dependency-graph/) | "DAG các task, thực thi theo thứ tự topo" |

### "Thiết kế một Message Queue"

| Khái niệm | Pattern | Câu nên nói |
|---|---|---|
| Buffer phía producer | [Ring Buffer](/patterns/ring-buffer/) | "Ring buffer kích thước cố định để enqueue/dequeue không cấp phát" |
| Kiểm soát luồng phía consumer | [Backpressure](/patterns/backpressure/) | "Nếu consumer chậm, tín hiệu cho producer giảm tốc — không bỏ thông điệp" |
| Giao hàng theo thứ tự | [Logical Clock](/patterns/logical-clock/) | "Lamport timestamp đảm bảo thứ tự nhân quả giữa các partition" |
| Ghi theo lô | [Batch Processing](/patterns/batch-processing/) | "Gom thông điệp, fsync theo lô — Kafka làm vậy để có throughput" |
| Bền vững | [WAL](/patterns/write-ahead-log/) | "Log append-only trên đĩa — replay để khôi phục" |

### "Thiết kế một API Gateway"

| Khái niệm | Pattern | Câu nên nói |
|---|---|---|
| Rate limiting | [Rate Limiter](/patterns/rate-limiter/) | "Token bucket theo client, theo endpoint" |
| Circuit breaking | [Circuit Breaker](/patterns/circuit-breaker/) | "Nếu tỉ lệ lỗi backend vượt ngưỡng, mở mạch và fail nhanh" |
| Chính sách retry | [Retry with Backoff](/patterns/retry-backoff/) | "Backoff theo cấp số nhân với jitter để tránh thundering herd" |
| Pipeline request | [Middleware Chain](/patterns/middleware-chain/) | "Auth → rate limit → transform → route → response — các handler có thể ghép" |
| Khám phá service | [Registry](/patterns/registry/) | "Service tự đăng ký, gateway tra cứu theo tên" |

## Phỏng vấn Coding

### Thiết kế cấu trúc dữ liệu

| Câu hỏi | Pattern cốt lõi | Insight chính |
|---|---|---|
| "Implement một LRU cache" | [LRU Cache](/patterns/lru-cache/) | Hash map + linked list hai chiều, mọi thao tác O(1) |
| "Thiết kế trie với insert/search/startsWith" | [Trie](/patterns/trie/) | Map con đệ quy, cờ isEnd |
| "Implement min-heap" | [Min Heap](/patterns/min-heap/) | Dựa trên mảng, siftUp khi insert, siftDown khi extract |
| "Thiết kế skip list" | [Skip List](/patterns/skip-list/) | Tầng ngẫu nhiên, tìm kiếm từ tầng cao xuống thấp |
| "Implement Bloom filter" | [Bloom Filter](/patterns/bloom-filter/) | k hàm hash, mảng bit, không âm tính giả |
| "Thiết kế object pool thread-safe" | [Object Pool](/patterns/object-pool/) | Acquire/release với mutex hoặc CAS |

### Bài toán thuật toán

| Câu hỏi | Pattern cốt lõi | Insight chính |
|---|---|---|
| "Gộp K danh sách đã sắp xếp" | [Merge Iterator](/patterns/merge-iterator/) | Min-heap chứa k đầu danh sách, extract-min và tiến |
| "Tìm trung vị trong luồng" | [Min Heap](/patterns/min-heap/) | Hai heap: max-heap cho nửa dưới, min-heap cho nửa trên |
| "Implement iterator làm phẳng danh sách lồng" | [Iterator](/patterns/iterator/) | Duyệt lười dựa trên stack |
| "Phát hiện chu trình trong linked list" | [Reference Counting](/patterns/reference-counting/) | Hai con trỏ Floyd là cách giải chuẩn — nhưng chu trình làm vỡ ref counting, hiểu được vì sao giúp bạn nổi bật |
| "Serialize/deserialize cây" | [Visitor](/patterns/visitor/) | Duyệt pre-order để serialize, xây lại đệ quy để deserialize |
| "Tính khoảng cách chỉnh sửa tối thiểu" | [Diff / Patch](/patterns/diff-patch/) | Quy hoạch động trên hai chuỗi |

### Bài toán concurrency

| Câu hỏi | Pattern cốt lõi | Insight chính |
|---|---|---|
| "Implement semaphore" | [Semaphore](/patterns/semaphore/) | Bộ đếm + mutex + condition variable |
| "Thiết kế thread pool" | [Work Stealing](/patterns/work-stealing/) | Deque mỗi thread, lấy trộm từ đuôi |
| "Implement read-write lock" | [Semaphore](/patterns/semaphore/) | Counting semaphore cho reader chia sẻ, mutex cho writer độc quyền |
| "Bài toán producer-consumer" | [Ring Buffer](/patterns/ring-buffer/) + [Backpressure](/patterns/backpressure/) | Buffer giới hạn với wait/signal |
| "Bài toán bữa ăn triết gia" | [Semaphore](/patterns/semaphore/) | Sắp thứ tự tài nguyên để chống deadlock |

## Người phỏng vấn thực sự tìm kiếm điều gì

Không phải về việc thuộc lòng pattern. Đây là điều phân biệt ứng viên xuất sắc:

### 1. Nhận thức về đánh đổi

Đừng chỉ nói "tôi sẽ dùng Bloom filter." Hãy nói:

> "Bloom filter cho phép lookup O(k) trong O(m) bit bộ nhớ, với tỉ lệ dương tính giả có thể điều chỉnh. Đánh đổi là không xoá được — cho việc đó cần counting Bloom filter, dùng gấp 4 lần bộ nhớ."

Mỗi pattern trong bộ này đều có phần **Khi không nên dùng** — hãy đọc chúng.

### 2. Bối cảnh production

Đừng nói "tôi sẽ dùng một queue." Hãy nói:

> "Tôi sẽ dùng ring buffer giống LMAX Disruptor — kích thước cố định, không cấp phát, và producer/consumer có thể ở các core khác nhau mà không bị tranh chấp cache-line vì chúng truy cập index khác nhau."

Phần **Bằng chứng từ production** của mỗi pattern cho bạn các tham chiếu này.

### 3. Kết hợp

Hệ thống thật kết hợp nhiều pattern. Khi thiết kế KV store, đừng chỉ nói "LSM tree." Đi qua toàn bộ stack:

> "Ghi vào WAL để bền vững, rồi memtable (sắp xếp trong bộ nhớ). Khi đầy, flush thành SSTable. Mỗi SSTable có một Bloom filter để tối ưu đọc. Compaction dùng merge iterator để gộp các SSTable. Xoá dùng tombstone."

[Cheat Sheet](/guide/cheatsheet) có phần **Pattern Combos** cho việc này.

### 4. Vẽ

Nếu bạn có thể vẽ cơ chế của pattern lên bảng, bạn đã hiểu nó. Nếu không, bạn mới chỉ thuộc tên. Trực quan hoá tương tác của mỗi pattern dạy bạn cần vẽ những gì.

## Kế hoạch học

### Sprint 1 tuần

| Ngày | Trọng tâm | Pattern |
|---|---|---|
| 1 | Caching & tra cứu | LRU Cache, Bloom Filter, Trie |
| 2 | Storage engine | WAL, LSM Tree, B+ Tree, Checkpointing |
| 3 | Độ tin cậy | Circuit Breaker, Rate Limiter, Retry with Backoff |
| 4 | Concurrency | Semaphore, MVCC, Work Stealing |
| 5 | Phân tán | Consistent Hashing, Logical Clock, Merkle Tree |
| 6 | Bộ nhớ & runtime | Object Pool, Arena, Reference Counting, Copy-on-Write |
| 7 | Ôn tập | Chạy tất cả bài tập, luyện vẽ cơ chế |

### Khoá tốc lực cuối tuần

Tập trung vào 10 pattern chiếm 80% các buổi phỏng vấn system design:

1. [LRU Cache](/patterns/lru-cache/) — mọi câu hỏi về cache
2. [Rate Limiter](/patterns/rate-limiter/) — câu hỏi phỏng vấn riêng + dùng trong API gateway
3. [Consistent Hashing](/patterns/consistent-hashing/) — mọi câu hỏi phân tán
4. [WAL](/patterns/write-ahead-log/) — mọi câu hỏi storage/database
5. [LSM Tree](/patterns/lsm-tree/) — thiết kế KV store
6. [Bloom Filter](/patterns/bloom-filter/) — tối ưu đọc, kiểm tra thành viên tập
7. [Circuit Breaker](/patterns/circuit-breaker/) — API gateway, microservice
8. [MVCC](/patterns/mvcc/) — concurrency database
9. [Min Heap](/patterns/min-heap/) — scheduler, gộp k, trung vị
10. [Merkle Tree](/patterns/merkle-tree/) — toàn vẹn dữ liệu, anti-entropy
