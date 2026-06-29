# Kế hoạch học tập

> **Fork repo này** và đánh dấu các pattern khi bạn hoàn thành. Tiến độ của bạn được lưu trong fork.
>
> Với mỗi pattern: đọc tài liệu → thử trực quan hoá → làm bài tập → trả lời câu hỏi thử thách.
>
> Xem trang [Lộ trình học](https://github.hetsach.com/battle-tested-patterns/guide/learning-paths) để biết thứ tự khuyến nghị và mẹo học.

## Track 1: Nền tảng cấu trúc dữ liệu

- [ ] [Bitmask](https://github.hetsach.com/battle-tested-patterns/patterns/bitmask/) — Nhồi N flag vào một số nguyên
- [ ] [Ring Buffer](https://github.hetsach.com/battle-tested-patterns/patterns/ring-buffer/) — FIFO kích thước cố định, không cấp phát
- [ ] [Tagged Union](https://github.hetsach.com/battle-tested-patterns/patterns/tagged-union/) — Tag kiểu cho dispatch an toàn
- [ ] [Min Heap](https://github.hetsach.com/battle-tested-patterns/patterns/min-heap/) — Truy cập phần tử ưu tiên cao nhất O(1)
- [ ] [Trie](https://github.hetsach.com/battle-tested-patterns/patterns/trie/) — Tra cứu O(k) theo độ dài key
- [ ] [Bloom Filter](https://github.hetsach.com/battle-tested-patterns/patterns/bloom-filter/) — Kiểm tra thành viên theo xác suất
- [ ] [LRU Cache](https://github.hetsach.com/battle-tested-patterns/patterns/lru-cache/) — Kết hợp hash map + linked list
- [ ] [Skip List](https://github.hetsach.com/battle-tested-patterns/patterns/skip-list/) — Cấu trúc sắp xếp theo xác suất
- [ ] [B+ Tree](https://github.hetsach.com/battle-tested-patterns/patterns/b-plus-tree/) — Cây cân bằng tối ưu cho đĩa
- [ ] [Merkle Tree](https://github.hetsach.com/battle-tested-patterns/patterns/merkle-tree/) — Chuỗi hash cho bằng chứng toàn vẹn
- [ ] [Visitor](https://github.hetsach.com/battle-tested-patterns/patterns/visitor/) — Tách việc duyệt khỏi thao tác

## Track 2: Concurrency & lập lịch

- [ ] [Semaphore](https://github.hetsach.com/battle-tested-patterns/patterns/semaphore/) — Giới hạn concurrency bằng bộ đếm
- [ ] [Double Buffering](https://github.hetsach.com/battle-tested-patterns/patterns/double-buffering/) — Hoán đổi nguyên tử hai buffer
- [ ] [Observer](https://github.hetsach.com/battle-tested-patterns/patterns/observer/) — Tách rời subscribe/notify
- [ ] [Event Loop](https://github.hetsach.com/battle-tested-patterns/patterns/event-loop/) — Ghép kênh I/O đơn luồng
- [ ] [Backpressure](https://github.hetsach.com/battle-tested-patterns/patterns/backpressure/) — Kiểm soát luồng giữa producer/consumer
- [ ] [Copy-on-Write](https://github.hetsach.com/battle-tested-patterns/patterns/copy-on-write/) — Chia sẻ cho đến khi sửa đổi
- [ ] [Cooperative Scheduling](https://github.hetsach.com/battle-tested-patterns/patterns/cooperative-scheduling/) — Điểm yield để giữ phản hồi
- [ ] [MVCC](https://github.hetsach.com/battle-tested-patterns/patterns/mvcc/) — Reader có phiên bản không bao giờ chặn writer
- [ ] [Work Stealing](https://github.hetsach.com/battle-tested-patterns/patterns/work-stealing/) — Thread rảnh lấy việc từ queue bận
- [ ] [Actor Model](https://github.hetsach.com/battle-tested-patterns/patterns/actor-model/) — Trạng thái cô lập + truyền thông điệp

## Track 3: Độ tin cậy hệ thống

- [ ] [Retry with Backoff](https://github.hetsach.com/battle-tested-patterns/patterns/retry-backoff/) — Delay theo cấp số nhân + jitter
- [ ] [Batch Processing](https://github.hetsach.com/battle-tested-patterns/patterns/batch-processing/) — Phân bổ chi phí mỗi thao tác
- [ ] [State Machine](https://github.hetsach.com/battle-tested-patterns/patterns/state-machine/) — Trạng thái rõ ràng, chuyển tiếp bất hợp lệ bị chặn
- [ ] [Circuit Breaker](https://github.hetsach.com/battle-tested-patterns/patterns/circuit-breaker/) — Fail nhanh khi service bị sập
- [ ] [Rate Limiter](https://github.hetsach.com/battle-tested-patterns/patterns/rate-limiter/) — Token bucket điều tiết throughput
- [ ] [Middleware Chain](https://github.hetsach.com/battle-tested-patterns/patterns/middleware-chain/) — Handler request có thể ghép
- [ ] [Dependency Graph](https://github.hetsach.com/battle-tested-patterns/patterns/dependency-graph/) — DAG + sắp xếp topo
- [ ] [Registry](https://github.hetsach.com/battle-tested-patterns/patterns/registry/) — Tự đăng ký để khám phá plugin
- [ ] [Consistent Hashing](https://github.hetsach.com/battle-tested-patterns/patterns/consistent-hashing/) — Remap tối thiểu khi đổi node
- [ ] [Logical Clock](https://github.hetsach.com/battle-tested-patterns/patterns/logical-clock/) — Xếp thứ tự nhân quả không cần wall clock

## Track 4: Nội tại storage engine

- [ ] [Tombstone](https://github.hetsach.com/battle-tested-patterns/patterns/tombstone/) — Đánh dấu đã xoá, dồn nén sau
- [ ] [Dirty Flag](https://github.hetsach.com/battle-tested-patterns/patterns/dirty-flag/) — Bỏ qua tính lại nếu không đổi
- [ ] [Iterator](https://github.hetsach.com/battle-tested-patterns/patterns/iterator/) — Duyệt lười kiểu pull
- [ ] [Write-Ahead Log](https://github.hetsach.com/battle-tested-patterns/patterns/write-ahead-log/) — Log trước khi áp dụng để an toàn khi crash
- [ ] [Checkpointing](https://github.hetsach.com/battle-tested-patterns/patterns/checkpointing/) — Snapshot trạng thái định kỳ
- [ ] [Diff / Patch](https://github.hetsach.com/battle-tested-patterns/patterns/diff-patch/) — Tính toán thay đổi tối thiểu
- [ ] [LSM Tree](https://github.hetsach.com/battle-tested-patterns/patterns/lsm-tree/) — Lưu trữ trên đĩa tối ưu cho ghi
- [ ] [Merge Iterator](https://github.hetsach.com/battle-tested-patterns/patterns/merge-iterator/) — Gộp k luồng đã sắp xếp

## Bonus: Quản lý bộ nhớ

- [ ] [Reference Counting](https://github.hetsach.com/battle-tested-patterns/patterns/reference-counting/) — Dọn dẹp xác định khi rc=0
- [ ] [Object Pool](https://github.hetsach.com/battle-tested-patterns/patterns/object-pool/) — Cấp phát trước và tái sử dụng
- [ ] [Flyweight](https://github.hetsach.com/battle-tested-patterns/patterns/flyweight/) — Chia sẻ các instance giống nhau
- [ ] [Interning](https://github.hetsach.com/battle-tested-patterns/patterns/interning/) — Khử trùng lặp dựa trên hash
- [ ] [Free List](https://github.hetsach.com/battle-tested-patterns/patterns/free-list/) — Cấp phát O(1) từ slot đã giải phóng
- [ ] [Arena Allocator](https://github.hetsach.com/battle-tested-patterns/patterns/arena-allocator/) — Cấp phát bump, giải phóng hàng loạt
- [ ] [Vtable](https://github.hetsach.com/battle-tested-patterns/patterns/vtable/) — Con trỏ hàm cho đa hình lúc runtime

---

**Tiến độ**: 0 / 46 pattern đã hoàn thành

> **Mẹo**: Sau khi hoàn thành tất cả bài tập trong một track, ghé lại trang [Liên kết giữa các pattern](https://github.hetsach.com/battle-tested-patterns/guide/pattern-connections) để xem các pattern đã học phối hợp với nhau như thế nào trong hệ thống production.
