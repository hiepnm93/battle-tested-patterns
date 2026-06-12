---
title: "Dòng thời gian của các Pattern"
description: "Dòng thời gian các pattern lập trình: 80 năm lịch sử ngành điện toán, từ von Neumann tới các hệ phân tán hiện đại."
---

# Dòng thời gian của các Pattern

Các pattern này trải dài trên 80+ năm lịch sử điện toán — từ những máy tính chương trình-lưu-trữ đầu tiên đến hệ phân tán hiện đại.

**Khám phá tương tác** — lọc theo nhóm, click vào card bất kỳ để nhảy tới pattern:

<PatternTimelineViz />

## Bảng đầy đủ

| Năm | Pattern | Nguồn gốc |
|------|---------|--------|
| ~1943 | [State Machine](/patterns/state-machine/) | McCulloch & Pitts mô hình hoá nơ-ron như automat hữu hạn; Mealy (1955) và Moore (1956) hình thức hoá hai kiểu chuẩn |
| ~1945 | [Bitmask](/patterns/bitmask/) | Vốn có trong máy tính chương trình-lưu-trữ; báo cáo EDVAC của von Neumann mô tả thao tác cấp bit |
| ~1953 | [Double Buffering](/patterns/double-buffering/) | Dùng trong subsystem I/O của IBM 701/709 để chồng lấp tính toán với truyền dữ liệu |
| ~1956 | [Batch Processing](/patterns/batch-processing/) | GM-NAA I/O monitor cho IBM 704 — hệ thống batch processing được tài liệu hoá đầu tiên |
| 1958 | [Free List](/patterns/free-list/) | LISP của McCarthy dùng free list để quản lý cấp phát cons cell |
| 1958 | [Cooperative Scheduling](/patterns/cooperative-scheduling/) | Melvin Conway mô tả coroutine (xuất bản 1963), hình thức hoá yield tự nguyện |
| 1959 | [Trie](/patterns/trie/) | Rene de la Briandais mô tả trie; Fredkin đặt tên "trie" (từ retrieval) năm 1960 |
| ~1960 | [Ring Buffer](/patterns/ring-buffer/) | Dùng trong viễn thông và hệ I/O thời gian thực; không có người phát minh duy nhất |
| ~1960 | [Arena Allocator](/patterns/arena-allocator/) | Cấp phát theo vùng trong compiler; Knuth bàn về pool allocation trong TAOCP (1968) |
| 1960 | [Reference Counting](/patterns/reference-counting/) | George Collins mô tả reference counting để tự thu hồi bộ nhớ |
| ~1960 | [Interning](/patterns/interning/) | LISP intern symbol từ những bản triển khai đầu tiên; kỹ thuật có trước cả tên gọi |
| 1962 | [Dependency Graph](/patterns/dependency-graph/) | Kahn xuất bản "Topological sorting of large networks" trong CACM |
| 1964 | [Min Heap](/patterns/min-heap/) | Williams phát minh binary heap cho heapsort; Floyd cải tiến cùng năm |
| 1965 | [Semaphore](/patterns/semaphore/) | Dijkstra phát minh P() và V() cho hệ điều hành THE |
| ~1965 | [Dirty Flag](/patterns/dirty-flag/) | Hệ thống bộ nhớ ảo dùng "dirty bit" để theo dõi page đã đổi; pattern tổng quát hoá cho mọi tính toán trì hoãn |
| 1966 | [LRU Cache](/patterns/lru-cache/) | "A study of replacement algorithms for virtual-storage computers" của Belady (IBM Systems Journal) |
| ~1966 | [Tagged Union](/patterns/tagged-union/) | Algol 68 hình thức hoá discriminated union; lập trình viên assembly trước đó đã dùng type tag không chính thức |
| 1967 | [Vtable](/patterns/vtable/) | Simula 67 giới thiệu virtual method dispatch qua bảng method; C++ sau này phổ biến tên "vtable" |
| ~1967 | [Event Loop](/patterns/event-loop/) | Hệ thống tương tác sớm dùng dispatch hướng sự kiện; được Smalltalk (1980) và X Window System (1984) phổ biến |
| 1970 | [Bloom Filter](/patterns/bloom-filter/) | Burton Bloom xuất bản "Space/Time Trade-offs in Hash Coding with Allowable Errors" (CACM) |
| ~1970 | [B+ Tree](/patterns/b-plus-tree/) | Bayer & McCreight phát minh B-tree (1970); biến thể B+ với page lá liên kết xuất hiện khoảng 1972 cho index database |
| ~1971 | [Copy-on-Write](/patterns/copy-on-write/) | Bộ nhớ ảo IBM VM/370; sau được BSD Unix dùng cho fork() |
| 1973 | [Actor Model](/patterns/actor-model/) | Hewitt, Bishop, Steiger: "A Universal Modular Actor Formalism for AI" |
| 1973 | [Retry with Backoff](/patterns/retry-backoff/) | Ethernet của Metcalfe giới thiệu truncated binary exponential backoff cho CSMA/CD |
| 1974 | [Diff / Patch](/patterns/diff-patch/) | McIlroy tạo diff cho Unix V5 tại Bell Labs |
| ~1974 | [Backpressure](/patterns/backpressure/) | TCP flow control (Cerf & Kahn) — dạng backpressure production sớm nhất |
| 1975 | [Iterator](/patterns/iterator/) | Ngôn ngữ CLU của Liskov giới thiệu iterator như khái niệm first-class |
| ~1975 | [Tombstone](/patterns/tombstone/) | Dùng trong hệ thống database làm marker xoá; thiết yếu cho xoá B-tree và sau này LSM tree |
| ~1976 | [Write-Ahead Log](/patterns/write-ahead-log/) | IBM System R, database quan hệ SQL đầu tiên; hình thức hoá trong ARIES (1992) |
| ~1976 | [Checkpointing](/patterns/checkpointing/) | Dùng song song WAL trong System R để khôi phục sau crash; hình thức hoá trong ARIES |
| 1978 | [MVCC](/patterns/mvcc/) | Luận án TS MIT của David Reed về multi-version concurrency control |
| 1978 | [Logical Clock](/patterns/logical-clock/) | "Time, Clocks, and the Ordering of Events in a Distributed System" của Lamport — Lamport timestamp |
| 1979 | [Observer](/patterns/observer/) | MVC pattern của Reenskaug tại Xerox PARC cho Smalltalk |
| 1979 | [Merkle Tree](/patterns/merkle-tree/) | Ralph Merkle đăng ký bằng sáng chế hash tree để xác minh hiệu quả và bảo mật cho cấu trúc dữ liệu lớn |
| 1981 | [Work Stealing](/patterns/work-stealing/) | Burton & Sleep mô tả task stealing cho giảm đồ thị song song |
| ~1986 | [Rate Limiter](/patterns/rate-limiter/) | Turner mô tả leaky bucket để tạo hình traffic mạng |
| 1989 | [Skip List](/patterns/skip-list/) | Pugh: "Skip Lists: A Probabilistic Alternative to Balanced Trees" (CACM) |
| 1990 | [Flyweight](/patterns/flyweight/) | Calder & Linton: "Glyphs: Flyweight Objects for User Interfaces" (USENIX) |
| ~1993 | [Middleware Chain](/patterns/middleware-chain/) | Chain of Responsibility (GoF 1994) được các framework web tổng quát hoá thành pipeline middleware; middleware CORBA có trước |
| ~1993 | [Registry](/patterns/registry/) | COM (1993) và CORBA dùng registry để khám phá component; Abstract Factory của GoF có liên quan |
| ~1994 | [Object Pool](/patterns/object-pool/) | Slab allocator của Bonwick cho Solaris; pool kết nối database phổ biến hoá nó |
| 1994 | [Visitor](/patterns/visitor/) | "Design Patterns" của GoF hình thức hoá Visitor pattern cho double dispatch trên cấu trúc object |
| 1996 | [LSM Tree](/patterns/lsm-tree/) | O'Neil et al.: "The Log-Structured Merge-Tree" — đệm ghi trong bộ nhớ, flush thành file đã sắp xếp |
| 1997 | [Consistent Hashing](/patterns/consistent-hashing/) | Karger et al.: "Consistent Hashing and Random Trees" (STOC) |
| ~2003 | [Merge Iterator](/patterns/merge-iterator/) | Gộp K-luồng đã sắp xếp qua min-heap; hình thức hoá trong các hệ thống thời LevelDB/BigTable |
| 2007 | [Circuit Breaker](/patterns/circuit-breaker/) | Nygard mô tả nó trong "Release It!" — vay mượn từ kỹ thuật điện |

> **Lưu ý:** Các năm có dấu ~ là gần đúng — các khái niệm này nảy sinh tự nhiên từ thực hành kỹ thuật chứ không phải từ một xuất bản duy nhất.

## Điều này nói lên điều gì

1. **Các kiến thức nền tảng đã rất CŨ.** Semaphore (1965), heap (1964) và state machine (1943) đã được kiểm chứng 60-80 năm. Khi bạn dùng chúng, bạn đang đứng trên hàng chục năm kỹ thuật đã được chứng minh.

2. **Hầu hết các pattern "mới" là sự kết hợp.** Reconciler của React (2017) kết hợp bitmask + min heap + cooperative scheduling + diff/patch + double buffering — tất cả đều được phát minh giữa 1943 và 1974.

3. **Khoảng cách giữa phát minh và được áp dụng rộng rãi đang thu hẹp.** Bloom filter mất 30 năm từ bài báo (1970) đến phổ biến trong database (những năm 2000). Circuit breaker chỉ mất 5 năm từ sách (2007) tới Netflix Hystrix (2012).

4. **Pattern sống lâu hơn các công nghệ phổ biến hoá chúng.** Copy-on-Write được phát minh cho IBM mainframe năm 1971 — giờ có mặt trong Git, Rust và mọi kernel OS hiện đại.
