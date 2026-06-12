---
title: "Bảng tra độ phức tạp"
description: "Tham chiếu độ phức tạp Big-O cho toàn bộ 46 pattern — các thao tác chính, thời gian & bộ nhớ ở dạng tra nhanh."
---

# Bảng tra độ phức tạp

Tham chiếu nhanh độ phức tạp thời gian và không gian cho các thao tác chính của mỗi pattern. Dùng nó để so sánh đánh đổi trước khi chọn pattern.

## Cách đọc bảng

- **n** = số phần tử / item
- **k** = độ dài key (cho cấu trúc đánh key bằng chuỗi)
- **m** = số hàm hash (Bloom filter)
- **L** = số tầng (skip list, LSM tree)
- Chi phí phân bổ trung bình ghi **(phân bổ)**

## Cấu trúc dữ liệu

| Pattern | Thêm | Tra | Xoá | Bộ nhớ | Ghi chú |
|---------|--------|--------|--------|-------|-------|
| [Bitmask](/patterns/bitmask/) | O(1) | O(1) | O(1) | O(1) | Kích thước cố định; giới hạn theo độ rộng word (32/64 flag) |
| [Ring Buffer](/patterns/ring-buffer/) | O(1) | O(1) | O(1) | O(n) | Sức chứa cố định; ghi đè lên cái cũ nhất khi đầy |
| [Tagged Union](/patterns/tagged-union/) | — | O(1) | — | O(variant lớn nhất) | Dispatch theo tag; không cấp phát động |
| [Min Heap](/patterns/min-heap/) | O(log n) | O(1) peek | O(log n) | O(n) | Truy cập min O(1); dùng cho hàng đợi ưu tiên |
| [Trie](/patterns/trie/) | O(k) | O(k) | O(k) | O(n × k) | Không phụ thuộc tổng số entry; truy vấn prefix O(k + kết quả) |
| [Bloom Filter](/patterns/bloom-filter/) | O(m) | O(m) | ✗ | O(n) | Theo xác suất; có thể có dương tính giả, không có âm tính giả |
| [LRU Cache](/patterns/lru-cache/) | O(1) | O(1) | O(1) | O(n) | Hash map + linked list hai chiều |
| [Skip List](/patterns/skip-list/) | O(log n) trung bình | O(log n) trung bình | O(log n) trung bình | O(n) | Cân bằng theo xác suất; hỗ trợ truy vấn khoảng |
| [B+ Tree](/patterns/b-plus-tree/) | O(log n) | O(log n) | O(log n) | O(n) | Tối ưu cho đĩa; fanout cao giảm thiểu I/O |
| [Merkle Tree](/patterns/merkle-tree/) | O(log n) | O(log n) | O(log n) | O(n) | Bằng chứng xác minh O(log n) |
| [Merge Iterator](/patterns/merge-iterator/) | — | O(log k) next | — | O(k) | k = số luồng; gộp dựa trên heap |

## Concurrency

| Pattern | Thao tác chính | Chi phí | Bộ nhớ | Ghi chú |
|---------|--------------|------|-------|-------|
| [Semaphore](/patterns/semaphore/) | acquire / release | O(1) | O(1) | Dùng bộ đếm; có thể chặn khi tranh chấp |
| [Double Buffering](/patterns/double-buffering/) | swap | O(1) | O(2n) | Đổi con trỏ; không copy |
| [Event Loop](/patterns/event-loop/) | enqueue / dequeue | O(1) | O(queue) | Đơn luồng; ghép kênh I/O |
| [Backpressure](/patterns/backpressure/) | signal / check | O(1) | O(1) | Kiểm soát luồng; thường ghép vào channel có sẵn |
| [Copy-on-Write](/patterns/copy-on-write/) | đọc | O(1) | O(n) mỗi snapshot | Ghi kích hoạt clone O(n); đọc không bao giờ chặn |
| [Cooperative Scheduling](/patterns/cooperative-scheduling/) | yield | O(1) | O(số task) | Cần điểm yield tự nguyện |
| [MVCC](/patterns/mvcc/) | đọc / ghi | O(1) + GC | O(n × phiên bản) | Đọc không bao giờ chặn; chi phí GC phân bổ |
| [Work Stealing](/patterns/work-stealing/) | push / steal | O(1) phân bổ | O(số task) | Deque lock-free; theo dõi cache-line |
| [Actor Model](/patterns/actor-model/) | gửi thông điệp | O(1) | O(số actor × mailbox) | Trạng thái cô lập; không bộ nhớ chung |
| [Logical Clock](/patterns/logical-clock/) | tick / merge | O(1) Lamport, O(n) Vector | O(1) / O(n) | Vector clock tăng theo số node |

## Hệ thống

| Pattern | Thao tác chính | Chi phí | Bộ nhớ | Ghi chú |
|---------|--------------|------|-------|-------|
| [State Machine](/patterns/state-machine/) | chuyển trạng thái | O(1) | O(số trạng thái) | Dispatch thời gian hằng; trạng thái rõ ràng |
| [Circuit Breaker](/patterns/circuit-breaker/) | call / check | O(1) | O(1) | Bộ đếm + timer; 3 trạng thái |
| [Rate Limiter](/patterns/rate-limiter/) | allow? | O(1) | O(1) mỗi limiter | Token bucket hoặc cửa sổ trượt |
| [Retry with Backoff](/patterns/retry-backoff/) | retry | O(số lần thử) tổng | O(1) | Delay theo cấp số nhân + jitter |
| [Batch Processing](/patterns/batch-processing/) | flush | O(batch) | O(batch) | Phân bổ chi phí trên mỗi item |
| [Middleware Chain](/patterns/middleware-chain/) | execute | O(số middleware) | O(số middleware) | Pipeline tuyến tính; mỗi handler O(1) |
| [Registry](/patterns/registry/) | register / lookup | O(1) hash | O(n) | Service locator đánh key bằng chuỗi |
| [Dirty Flag](/patterns/dirty-flag/) | check / mark | O(1) | O(1) | Cờ boolean; bỏ qua nếu không đổi |
| [Dependency Graph](/patterns/dependency-graph/) | sắp xếp topo | O(V + E) | O(V + E) | DAG; phát hiện chu trình |
| [Consistent Hashing](/patterns/consistent-hashing/) | tra node | O(log n) | O(n × vnode) | Tìm nhị phân trên vòng; xáo trộn tối thiểu |
| [Write-Ahead Log](/patterns/write-ahead-log/) | append | O(1) phân bổ | O(log size) | Ghi tuần tự; fsync để bền vững |
| [Checkpointing](/patterns/checkpointing/) | snapshot | O(kích thước state) | O(kích thước state) | Định kỳ; cắt bớt WAL |
| [LSM Tree](/patterns/lsm-tree/) | write / read | O(1) write, O(L) read | O(n) | Tối ưu cho ghi; compaction ở background |

## Bộ nhớ

| Pattern | Cấp phát | Giải phóng | Tra | Bộ nhớ | Ghi chú |
|---------|----------|------|--------|-------|-------|
| [Object Pool](/patterns/object-pool/) | O(1) | O(1) | — | O(kích thước pool) | Cấp phát trước; tránh áp lực GC |
| [Flyweight](/patterns/flyweight/) | — | — | O(1) | O(số instance duy nhất) | Chia sẻ các instance giống nhau |
| [Arena Allocator](/patterns/arena-allocator/) | O(1) bump | O(1) hàng loạt | — | O(kích thước arena) | Bump pointer; giải phóng tất cả một lần |
| [Free List](/patterns/free-list/) | O(1) | O(1) | — | O(n) | Linked list của các slot đã giải phóng |
| [Copy-on-Write](/patterns/copy-on-write/) | O(1) chia sẻ | O(n) khi ghi | O(1) | O(n) mỗi snapshot | Hoãn copy |
| [Reference Counting](/patterns/reference-counting/) | O(1) clone | O(1) drop | — | O(1) mỗi ref | Xác định; không tự xử lý chu trình |
| [Tombstone](/patterns/tombstone/) | — | O(1) đánh dấu | O(1) | O(n + đã xoá) | Xoá mềm; dồn nén sau |
| [Interning](/patterns/interning/) | O(k) lần đầu, O(1) các lần sau | — | O(1) | O(số duy nhất × k) | Khử trùng lặp dựa trên hash; so sánh bằng con trỏ |

## Hành vi

| Pattern | Thao tác chính | Chi phí | Bộ nhớ | Ghi chú |
|---------|--------------|------|-------|-------|
| [Observer](/patterns/observer/) | notify | O(số subscriber) | O(số subscriber) | Fan-out; thứ tự có thể khác |
| [Iterator](/patterns/iterator/) | next | O(1) mỗi bước | O(1) | Đánh giá lười; kiểu pull |
| [Diff / Patch](/patterns/diff-patch/) | diff | O(n × m) Myers | O(n + m) | Khoảng cách chỉnh sửa tối thiểu |
| [Vtable](/patterns/vtable/) | dispatch | O(1) | O(số method) | Gián tiếp qua con trỏ; phân giải tĩnh |
| [Visitor](/patterns/visitor/) | visit | O(số node) | O(độ sâu cây) | Double dispatch; duyệt + thao tác |

## Tóm tắt đánh đổi chính

| Nếu bạn cần... | Chọn | Đánh đổi |
|---------------|--------|-----------|
| Tra O(1) + loại bỏ O(1) | [LRU Cache](/patterns/lru-cache/) | Thêm bộ nhớ cho linked list hai chiều |
| Ghi O(1) ở quy mô lớn | [LSM Tree](/patterns/lsm-tree/) | Read amplification (nhiều tầng) |
| Kiểm tra thành viên O(1) | [Bloom Filter](/patterns/bloom-filter/) | Dương tính giả (không âm tính giả) |
| Cấp phát O(1) | [Arena](/patterns/arena-allocator/) hoặc [Free List](/patterns/free-list/) | Không giải phóng từng phần (arena) hoặc phân mảnh (free list) |
| Truy cập sắp xếp O(log n) | [Skip List](/patterns/skip-list/) hoặc [B+ Tree](/patterns/b-plus-tree/) | Skip list đơn giản hơn, B+ tree tối ưu cho đĩa |
| Đọc không copy | [Copy-on-Write](/patterns/copy-on-write/) hoặc [MVCC](/patterns/mvcc/) | Write amplification khi sửa đổi |
| Rehash tối thiểu khi mở rộng | [Consistent Hashing](/patterns/consistent-hashing/) | Virtual node thêm chi phí bộ nhớ |
