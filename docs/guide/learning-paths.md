---
title: "Lộ trình học"
description: "Bốn lộ trình học được tuyển chọn để dẫn bạn qua 46 pattern — từ cấu trúc dữ liệu dễ tiếp cận cho người mới đến hệ phân tán nâng cao."
---

# Lộ trình học

Chưa biết bắt đầu từ đâu? Chọn một track phù hợp với mục tiêu. Mỗi track được sắp xếp sao cho các pattern đầu làm nền tảng cho các pattern sau.

## Cách hiểu mức độ khó

Mỗi pattern được gắn nhãn theo cấp độ:

- **Beginner** — một cơ chế cốt lõi, ít yêu cầu nền tảng
- **Intermediate** — kết hợp 2-3 khái niệm, cần một chút nền tảng
- **Advanced** — hệ thống đa thành phần phức tạp, yêu cầu nền tảng vững

## Track 1: Nền tảng cấu trúc dữ liệu

Đi từ container kích thước cố định đơn giản đến cây tự cân bằng.

| # | Pattern | Độ khó | Ý chính | 
|---|---------|-----------|--------------|
| 1 | [Bitmask](/patterns/bitmask/) | Beginner | Nhồi N flag vào một số nguyên |
| 2 | [Ring Buffer](/patterns/ring-buffer/) | Beginner | FIFO kích thước cố định, không cấp phát |
| 3 | [Tagged Union](/patterns/tagged-union/) | Beginner | Tag kiểu để dispatch an toàn |
| 4 | [Min Heap](/patterns/min-heap/) | Intermediate | Truy cập phần tử ưu tiên cao nhất O(1) |
| 5 | [Trie](/patterns/trie/) | Intermediate | Tra cứu O(k) theo độ dài key |
| 6 | [Bloom Filter](/patterns/bloom-filter/) | Intermediate | Kiểm tra thành viên tập theo xác suất |
| 7 | [LRU Cache](/patterns/lru-cache/) | Intermediate | Kết hợp hash map + linked list |
| 8 | [Skip List](/patterns/skip-list/) | Advanced | Cấu trúc sắp xếp theo xác suất |
| 9 | [B+ Tree](/patterns/b-plus-tree/) | Advanced | Cây cân bằng tối ưu cho đĩa |
| 10 | [Merkle Tree](/patterns/merkle-tree/) | Advanced | Chuỗi hash cho bằng chứng toàn vẹn |
| 11 | [Visitor](/patterns/visitor/) | Advanced | Tách việc duyệt khỏi thao tác |

**Sau track này**, bạn sẽ hiểu các cấu trúc dữ liệu cốt lõi đằng sau database (B+ Tree), cache (LRU) và blockchain (Merkle Tree).

## Track 2: Concurrency & lập lịch

Từ các primitive khoá cơ bản đến phân phối công việc cấp production.

| # | Pattern | Độ khó | Ý chính |
|---|---------|-----------|--------------|
| 1 | [Semaphore](/patterns/semaphore/) | Beginner | Giới hạn concurrency bằng bộ đếm |
| 2 | [Double Buffering](/patterns/double-buffering/) | Beginner | Hoán đổi nguyên tử hai buffer |
| 3 | [Observer](/patterns/observer/) | Beginner | Tách rời subscribe/notify |
| 4 | [Event Loop](/patterns/event-loop/) | Intermediate | Ghép kênh I/O đơn luồng |
| 5 | [Backpressure](/patterns/backpressure/) | Intermediate | Kiểm soát luồng giữa producer/consumer |
| 6 | [Copy-on-Write](/patterns/copy-on-write/) | Intermediate | Chia sẻ cho đến khi sửa đổi |
| 7 | [Cooperative Scheduling](/patterns/cooperative-scheduling/) | Advanced | Điểm yield để giữ phản hồi |
| 8 | [MVCC](/patterns/mvcc/) | Advanced | Reader có phiên bản không bao giờ chặn writer |
| 9 | [Work Stealing](/patterns/work-stealing/) | Advanced | Thread rảnh lấy việc từ queue bận |
| 10 | [Actor Model](/patterns/actor-model/) | Advanced | Trạng thái cô lập + truyền thông điệp |

**Sau track này**, bạn sẽ hiểu cách React giữ phản hồi nhanh (Cooperative Scheduling), cách database xử lý transaction đồng thời (MVCC) và cách Go/Tokio lên lịch goroutine (Work Stealing).

## Track 3: Độ tin cậy hệ thống

Xây dựng service kiên cường, xử lý lỗi một cách mượt mà.

| # | Pattern | Độ khó | Ý chính |
|---|---------|-----------|--------------|
| 1 | [Retry with Backoff](/patterns/retry-backoff/) | Beginner | Delay theo cấp số nhân + jitter |
| 2 | [Batch Processing](/patterns/batch-processing/) | Beginner | Phân bổ chi phí mỗi thao tác |
| 3 | [State Machine](/patterns/state-machine/) | Beginner | Trạng thái rõ ràng, chuyển tiếp bất hợp lệ bị chặn |
| 4 | [Circuit Breaker](/patterns/circuit-breaker/) | Intermediate | Fail nhanh khi service bị sập |
| 5 | [Rate Limiter](/patterns/rate-limiter/) | Intermediate | Token bucket điều tiết throughput |
| 6 | [Middleware Chain](/patterns/middleware-chain/) | Intermediate | Handler request có thể ghép |
| 7 | [Dependency Graph](/patterns/dependency-graph/) | Intermediate | DAG + sắp xếp topo |
| 8 | [Registry](/patterns/registry/) | Beginner | Tự đăng ký để khám phá plugin |
| 9 | [Consistent Hashing](/patterns/consistent-hashing/) | Advanced | Remap tối thiểu khi đổi node |
| 10 | [Logical Clock](/patterns/logical-clock/) | Advanced | Sắp xếp nhân quả không cần wall clock |

**Sau track này**, bạn sẽ thiết kế được API gateway kiên cường, service mesh và scheduler phân tán.

## Track 4: Nội tại storage engine

Hiểu cách database và storage engine hoạt động bên trong.

| # | Pattern | Độ khó | Ý chính |
|---|---------|-----------|--------------|
| 1 | [Tombstone](/patterns/tombstone/) | Beginner | Đánh dấu đã xoá, dồn nén sau |
| 2 | [Dirty Flag](/patterns/dirty-flag/) | Beginner | Bỏ qua tính lại nếu không đổi |
| 3 | [Iterator](/patterns/iterator/) | Beginner | Duyệt lười kiểu pull |
| 4 | [Write-Ahead Log](/patterns/write-ahead-log/) | Intermediate | Log trước khi áp dụng để an toàn khi crash |
| 5 | [Checkpointing](/patterns/checkpointing/) | Intermediate | Snapshot trạng thái định kỳ |
| 6 | [Diff / Patch](/patterns/diff-patch/) | Intermediate | Tính toán thay đổi tối thiểu |
| 7 | [LSM Tree](/patterns/lsm-tree/) | Advanced | Lưu trữ trên đĩa tối ưu cho ghi |
| 8 | [Merge Iterator](/patterns/merge-iterator/) | Advanced | Gộp k luồng đã sắp xếp |

**Sau track này**, bạn sẽ hiểu kiến trúc của LevelDB/RocksDB (LSM Tree + WAL + Checkpointing) và cách Git theo dõi thay đổi (Diff/Patch + Merkle Tree).

## Track quản lý bộ nhớ (Bonus)

Dành cho lập trình viên hệ thống muốn hiểu allocator và các giải pháp thay thế GC.

| # | Pattern | Độ khó | Ý chính |
|---|---------|-----------|--------------|
| 1 | [Reference Counting](/patterns/reference-counting/) | Beginner | Dọn dẹp xác định khi rc=0 |
| 2 | [Object Pool](/patterns/object-pool/) | Beginner | Cấp phát trước và tái sử dụng |
| 3 | [Flyweight](/patterns/flyweight/) | Beginner | Chia sẻ các instance giống nhau |
| 4 | [Interning](/patterns/interning/) | Intermediate | Khử trùng lặp dựa trên hash |
| 5 | [Free List](/patterns/free-list/) | Intermediate | Cấp phát O(1) từ slot đã giải phóng |
| 6 | [Arena Allocator](/patterns/arena-allocator/) | Intermediate | Cấp phát bump, giải phóng hàng loạt |
| 7 | [Vtable](/patterns/vtable/) | Advanced | Con trỏ hàm cho đa hình lúc runtime |

**Sau track này**, bạn sẽ hiểu cách `sync.Pool` của Go, `bumpalo` của Rust và allocator object nhỏ của CPython hoạt động.

## Lịch học gợi ý

| Nhịp | Thời gian/ngày | Hoàn thành đầy đủ |
|------|-----------|-----------------|
| Thư giãn | 30 phút/ngày | ~8 tuần |
| Vừa phải | 1 tiếng/ngày | ~4 tuần |
| Cường độ cao | 2 tiếng/ngày | ~2 tuần |

Với mỗi pattern: đọc tài liệu (10 phút) → chạy trực quan hoá (5 phút) → làm bài tập bằng một ngôn ngữ (15-30 phút) → thử các câu hỏi thử thách (5 phút).

> **Mẹo**: Fork repo và dùng [Kế hoạch học](https://github.com/Totoro-jam/battle-tested-patterns/blob/e758be266d38db94723be233863e6f3effbf46cc/STUDY_PLAN.md) để theo dõi tiến độ bằng các checkbox.
