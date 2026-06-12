---
title: "Ma trận so sánh các pattern"
description: "So sánh đối đầu giữa các pattern tương tự — khi nào chọn cái này thay vì cái kia."
---

# Ma trận so sánh các pattern

Một số pattern trông giống nhau nhưng phục vụ mục đích khác. Hướng dẫn này so sánh các cặp dễ nhầm lẫn để giúp bạn chọn đúng công cụ.

## Cache vs Pool

| Khía cạnh | [LRU Cache](/patterns/lru-cache/) | [Object Pool](/patterns/object-pool/) |
|-----------|-----------|-------------|
| **Mục đích** | Tăng tốc tra cứu lặp lại | Tránh chi phí cấp phát/GC |
| **Loại bỏ** | Phần tử ít dùng gần nhất bị bỏ | Người dùng trả lại, tái sử dụng |
| **Nội dung** | Giá trị cache chỉ đọc | Object mutable, có thể tái dùng |
| **Tỉ lệ hit** | Phụ thuộc mẫu truy cập | 100% (cấp phát trước) |
| **Ví dụ** | DNS cache, HTTP cache | Pool kết nối DB, thread pool |
| **Khi nhầm lẫn** | Nếu bạn đang "cache" object để dùng lại | → đó là pool |

## Arena Allocator vs Free List

| Khía cạnh | [Arena Allocator](/patterns/arena-allocator/) | [Free List](/patterns/free-list/) |
|-----------|-----------------|-----------|
| **Cấp phát** | O(1) bump pointer | O(1) pop từ chuỗi free |
| **Giải phóng** | Chỉ tất cả một lần | Trả từng cái O(1) |
| **Phân mảnh** | Không (liền kề) | Có thể (không liền kề) |
| **Vòng đời** | Theo pha (parse, render) | Từng object |
| **Ví dụ** | Arena của compiler mỗi query | Tái chế entity game |
| **Khi nhầm lẫn** | Nếu cần giải phóng riêng | → dùng free list |

## Observer vs Actor Model

| Khía cạnh | [Observer](/patterns/observer/) | [Actor Model](/patterns/actor-model/) |
|-----------|----------|-------------|
| **Giao tiếp** | Callback đồng bộ | Thông điệp bất đồng bộ |
| **Liên kết** | Bộ nhớ chung, cùng thread | Trạng thái cô lập, ở bất kỳ vị trí nào |
| **Mở rộng** | Một process | Hệ phân tán |
| **Cô lập lỗi** | Một observer hỏng chặn tất cả | Actor crash độc lập |
| **Ví dụ** | DOM event, React state | Erlang/OTP, Akka |
| **Khi nhầm lẫn** | Nếu observer cần cô lập | → dùng actor |

## Skip List vs B+ Tree

| Khía cạnh | [Skip List](/patterns/skip-list/) | [B+ Tree](/patterns/b-plus-tree/) |
|-----------|-----------|---------|
| **Cân bằng** | Theo xác suất (tầng ngẫu nhiên) | Xác định (split/merge) |
| **Concurrency** | Có thể lock-free | Khoá phức tạp |
| **I/O đĩa** | Kém (đuổi con trỏ) | Xuất sắc (fanout cao) |
| **Triển khai** | Đơn giản (~100 dòng) | Phức tạp (~500+ dòng) |
| **Ví dụ** | Sorted set của Redis, memtable LevelDB | InnoDB của MySQL, chỉ mục filesystem |
| **Khi nhầm lẫn** | Dữ liệu sắp xếp trong bộ nhớ → skip list | Trên đĩa → B+ tree |

## Ring Buffer vs Queue (FIFO)

| Khía cạnh | [Ring Buffer](/patterns/ring-buffer/) | Queue chuẩn |
|-----------|-------------|------|
| **Sức chứa** | Cố định, cấp phát trước | Động, tăng theo nhu cầu |
| **Tràn** | Ghi đè cái cũ nhất (hoặc chặn) | Cấp phát thêm bộ nhớ |
| **Bộ nhớ** | O(sức chứa), không cấp phát | O(n), có thể gây GC |
| **Trường hợp dùng** | Buffer giới hạn, luồng audio | Queue task không giới hạn |
| **Ví dụ** | `io_uring` của Linux, logging | Message queue, BFS |
| **Khi nhầm lẫn** | Nếu biết sức chứa → ring buffer | Nếu không giới hạn → queue |

## Copy-on-Write vs Double Buffering

| Khía cạnh | [Copy-on-Write](/patterns/copy-on-write/) | [Double Buffering](/patterns/double-buffering/) |
|-----------|---------------|-----------------|
| **Số buffer** | 1 (clone khi ghi) | 2 (luôn cấp phát) |
| **Kích hoạt copy** | Khi sửa đổi | Không bao giờ (đổi con trỏ) |
| **Chi phí đọc** | O(1) luôn | O(1) luôn |
| **Chi phí ghi** | O(n) clone ở lần ghi đầu | O(ghi) vào back buffer |
| **Bộ nhớ** | O(n) chỉ khi đã ghi | O(2n) luôn |
| **Ví dụ** | Linux fork(), Rc\<T\> | Render GPU, vòng lặp game |
| **Khi nhầm lẫn** | Nếu ghi hiếm → CoW | Nếu ghi liên tục → double buffer |

## Circuit Breaker vs Rate Limiter

| Khía cạnh | [Circuit Breaker](/patterns/circuit-breaker/) | [Rate Limiter](/patterns/rate-limiter/) |
|-----------|-----------------|-------------|
| **Bảo vệ** | Bên gọi khỏi downstream hỏng | Server khỏi traffic quá tải |
| **Kích hoạt** | Ngưỡng số lần lỗi | Ngưỡng số request |
| **Hướng** | Đi ra (cuộc gọi của bạn tới người khác) | Đi vào (cuộc gọi của người khác tới bạn) |
| **Phục hồi** | Tự khôi phục sau timeout | Refill token theo thời gian |
| **Ví dụ** | Microservice → database | API gateway, login attempt |
| **Khi nhầm lẫn** | Bảo vệ chính mình → circuit breaker | Bảo vệ server → rate limiter |

## State Machine vs Strategy/Vtable

| Khía cạnh | [State Machine](/patterns/state-machine/) | [Vtable](/patterns/vtable/) |
|-----------|---------------|--------|
| **Dispatch theo** | Trạng thái hiện tại | Kiểu object |
| **Chuyển tiếp** | Rõ ràng, có guard | Không áp dụng |
| **Số trạng thái** | Thay đổi lúc runtime | Cố định lúc compile |
| **Kiểm tra** | "Chuyển này có hợp lệ không?" | "Triển khai nào sẽ gọi?" |
| **Ví dụ** | Trạng thái kết nối TCP | Trait object, interface |
| **Khi nhầm lẫn** | Nếu hành vi thay đổi theo thời gian → state machine | Nếu khác theo kiểu → vtable |

## Bloom Filter vs Hash Set

| Khía cạnh | [Bloom Filter](/patterns/bloom-filter/) | Hash Set |
|-----------|-------------|----------|
| **Dương tính giả** | Có (điều chỉnh được) | Không |
| **Âm tính giả** | Không | Không |
| **Bộ nhớ** | ~10 bit/phần tử | ~50+ byte/phần tử |
| **Xoá** | Không hỗ trợ | O(1) |
| **Trường hợp dùng** | Kiểm tra nhanh "chắc chắn không có trong tập" | Kiểm tra thành viên chính xác |
| **Ví dụ** | Chrome Safe Browsing, filter đọc LSM | Khử trùng lặp, URL đã thăm |
| **Khi nhầm lẫn** | Nếu chấp nhận 1% dương tính giả + cần tiết kiệm bộ nhớ | → Bloom filter |

## Write-Ahead Log vs Checkpointing

| Khía cạnh | [Write-Ahead Log](/patterns/write-ahead-log/) | [Checkpointing](/patterns/checkpointing/) |
|-----------|-----------------|---------------|
| **Mức chi tiết** | Mỗi thao tác | Snapshot định kỳ |
| **Khôi phục** | Replay từ checkpoint cuối | Tải snapshot + replay phần WAL còn lại |
| **Dung lượng đĩa** | Tăng không giới hạn (nếu không cắt) | Cố định mỗi snapshot |
| **Chi phí ghi** | O(1) append mỗi thao tác | O(kích thước state) mỗi snapshot |
| **Dùng chung?** | **Có** — WAL đảm bảo bền vững | Checkpoint giới hạn độ dài replay |
| **Ví dụ** | WAL của PostgreSQL, AOF của Redis | Base backup PostgreSQL, RDB Redis |

## Backpressure vs Rate Limiter

| Khía cạnh | [Backpressure](/patterns/backpressure/) | [Rate Limiter](/patterns/rate-limiter/) |
|-----------|---------------|-------------|
| **Hướng** | Producer → Consumer (tín hiệu ngược lên) | Bên ngoài → Server (thi hành tại gateway) |
| **Cơ chế** | Làm chậm/tạm dừng producer | Bỏ hoặc xếp hàng request thừa |
| **Phạm vi** | Kiểm soát luồng nội bộ pipeline | Biên API bên ngoài |
| **Thích nghi** | Động (điều chỉnh theo tốc độ consumer) | Ngưỡng tĩnh (token/giây) |
| **Ví dụ** | Node.js stream `.pipe()`, Reactive Streams | API Stripe 25 req/giây, Nginx `limit_req` |
| **Khi nhầm lẫn** | Nếu bạn kiểm soát producer → backpressure | Nếu không kiểm soát được bên gửi → rate limiter |

## Tombstone vs Dirty Flag

| Khía cạnh | [Tombstone](/patterns/tombstone/) | [Dirty Flag](/patterns/dirty-flag/) |
|-----------|-----------|------------|
| **Đánh dấu** | "Item này đã bị xoá" | "Item này cần tính lại" |
| **Vòng đời** | Vĩnh viễn cho đến khi compaction | Xoá sau khi tính lại |
| **Mục đích** | Hoãn xoá vật lý | Hoãn tính lại tốn kém |
| **Hiển thị** | Reader phải bỏ qua item có tombstone | Reader thấy giá trị cũ-cho-đến-khi-tính-lại |
| **Ví dụ** | Tombstone Cassandra, marker xoá LevelDB | Invalidation layout Chromium, transform game |
| **Khi nhầm lẫn** | Nếu đánh dấu "đã mất" → tombstone | Nếu đánh dấu "cần update" → dirty flag |

## Interning vs Flyweight

| Khía cạnh | [Interning](/patterns/interning/) | [Flyweight](/patterns/flyweight/) |
|-----------|-----------|-----------|
| **Chia sẻ** | Các giá trị giống nhau dùng chung một instance | Trạng thái nội tại chung, trạng thái ngoại tại khác |
| **Tra cứu** | Bảng toàn cục (hash map) | Factory với cache |
| **Định danh** | So sánh bằng con trỏ thay vì so giá trị | Object vẫn so sánh theo giá trị |
| **Khả năng đổi** | Bất biến (bắt buộc) | Nội tại bất biến, ngoại tại có thể đổi |
| **Ví dụ** | `sys.intern()` Python, `Symbol` Rust, string pool Java | Glyph font, sprite tile game, object CSS rule |
| **Khi nhầm lẫn** | Nếu mọi instance đều giống hệt → interning | Nếu các instance chia sẻ trạng thái *một phần* → flyweight |

## Event Loop vs Work Stealing

| Khía cạnh | [Event Loop](/patterns/event-loop/) | [Work Stealing](/patterns/work-stealing/) |
|-----------|------------|---------------|
| **Thread** | Một thread + ghép kênh I/O | Nhiều thread, mỗi cái một deque |
| **Tốt nhất cho** | I/O-bound, nhiều kết nối | CPU-bound, đệ quy/song song |
| **Lập lịch** | Cooperative (callback/promise) | Preemptive lấy trộm từ các deque khác |
| **Độ trễ** | Một callback chậm chặn tất cả | Thread rảnh lấy việc, giữ cân bằng |
| **Ví dụ** | Node.js, Nginx, Redis | Scheduler Go, ForkJoinPool Java, Tokio |
| **Khi nhầm lẫn** | Nếu chủ yếu là I/O + ít CPU → event loop | Nếu nặng CPU + nhiều core → work stealing |

## Visitor vs Middleware Chain

| Khía cạnh | [Visitor](/patterns/visitor/) | [Middleware Chain](/patterns/middleware-chain/) |
|-----------|---------|------------------|
| **Duyệt** | Đi qua cây/đồ thị các node có kiểu | Đi qua pipeline tuyến tính |
| **Dispatch** | Theo kiểu node (double dispatch) | Theo thứ tự đăng ký |
| **Thêm thao tác** | Visitor mới = thao tác mới | Middleware mới = lớp mới |
| **Luồng dữ liệu** | Visitor tích luỹ kết quả | Request/response chảy qua |
| **Ví dụ** | Pass LLVM IR, biến đổi AST | Express.js, Django, interceptor gRPC |
| **Khi nhầm lẫn** | Nếu xử lý cây không đồng nhất → visitor | Nếu xử lý pipeline request/response → middleware |

## Chọn pattern phù hợp: Flowchart quyết định

<DecisionTree variant="pattern-selector" />
