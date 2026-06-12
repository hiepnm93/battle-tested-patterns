---
title: "Pattern trong Go"
description: "Pattern Go runtime: work stealing, object pool, cooperative scheduling, semaphore, free list, flyweight và arena allocator."
---

# Pattern trong Go

Runtime và thư viện chuẩn của Go cho thấy các triển khai pattern gọn gàng, thực tế.

| Pattern | Ở đâu trong Go | Tác dụng |
|---------|------------|--------------|
| [Cooperative Scheduling](/patterns/cooperative-scheduling/) | [`runtime/proc.go`](https://github.com/golang/go/blob/f5cdf4745455415c7a43cfc7d925214d4511489b/src/runtime/proc.go#L4143-L4200) | Lập lịch goroutine với điểm preemption hợp tác |
| [Bitmask](/patterns/bitmask/) | [`os/types.go`](https://github.com/golang/go/blob/f5cdf4745455415c7a43cfc7d925214d4511489b/src/os/types.go#L32-L46) | `FileMode` — flag phân quyền Unix qua hằng có kiểu với `iota` |
| [Object Pool](/patterns/object-pool/) | [`sync/pool.go`](https://github.com/golang/go/blob/f5cdf4745455415c7a43cfc7d925214d4511489b/src/sync/pool.go#L52-L97) | `sync.Pool` — pool cục bộ theo từng P với fast path lock-free, dùng trong `fmt`, `encoding/json` |
| [Work Stealing](/patterns/work-stealing/) | [`runtime/proc.go`](https://github.com/golang/go/blob/f5cdf4745455415c7a43cfc7d925214d4511489b/src/runtime/proc.go#L3836-L3903) | `stealWork` — scheduler goroutine lấy trộm từ queue chạy của P khác qua `runqsteal`/`runqgrab` |
| [Free List](/patterns/free-list/) | [`runtime/mfixalloc.go`](https://github.com/golang/go/blob/f5cdf4745455415c7a43cfc7d925214d4511489b/src/runtime/mfixalloc.go#L31-L109) | `fixalloc` — allocator free-list kích thước cố định với node `mlink` xen vào |
| [LRU Cache](/patterns/lru-cache/) | [groupcache `lru/lru.go`](https://github.com/golang/groupcache/blob/2c02b8208cf8c02a3e358cb1d9b60950647543fc/lru/lru.go#L23-L104) | Struct `Cache` với linked list hai chiều + hash map, do Brad Fitzpatrick viết |
| [Consistent Hashing](/patterns/consistent-hashing/) | [groupcache `consistenthash.go`](https://github.com/golang/groupcache/blob/2c02b8208cf8c02a3e358cb1d9b60950647543fc/consistenthash/consistenthash.go#L28-L81) | Vòng hash với virtual node cho cache phân tán |
| [Rate Limiter](/patterns/rate-limiter/) | [`x/time/rate`](https://github.com/golang/time/blob/812b343c8714c317b0dad633efa6d103e554c006/rate/rate.go#L57-L66) | Rate limiter token bucket trong thư viện chuẩn mở rộng |
| [Semaphore](/patterns/semaphore/) | [`x/sync/semaphore`](https://github.com/golang/sync/blob/5071ed6a9f1617117556b66384f765c934de3698/semaphore/semaphore.go#L28-L107) | Weighted semaphore — `errgroup` dùng nội bộ để giới hạn concurrency goroutine |
| [Flyweight](/patterns/flyweight/) | [`sync/pool.go`](https://github.com/golang/go/blob/f5cdf4745455415c7a43cfc7d925214d4511489b/src/sync/pool.go#L52-L97) | `sync.Pool` như flyweight — `Get()` trả về instance đã cache thay vì cấp phát, `Put()` trả về để tái dùng |
| [Arena Allocator](/patterns/arena-allocator/) | [`arena/arena.go`](https://github.com/golang/go/blob/f5cdf4745455415c7a43cfc7d925214d4511489b/src/arena/arena.go#L44-L67) | Arena allocator thử nghiệm — `New[T]()` cấp phát, `Free()` giải phóng tất cả một lúc, bỏ qua GC |

## Cách chúng kết hợp: Lập lịch goroutine

Khi bạn khởi chạy `go func()`, nhiều pattern phối hợp để chạy hàng triệu goroutine trên vài thread OS:

<CompositionFlow variant="go-goroutine" />

Mô hình GMP (Goroutine, M thread, P processor) là chất kết dính: mỗi P sở hữu một run queue cục bộ, một allocator free-list và một shard sync.Pool. Work stealing chỉ kích hoạt khi P cạn việc. Thiết kế này nghĩa là hầu hết thao tác đều lock-free trên fast path, và tranh chấp chỉ xảy ra khi steal — vốn là trường hợp hiếm theo thiết kế.

## Đọc thêm

- [Source Go (GitHub)](https://github.com/golang/go)
- [Tài liệu package Go Runtime](https://pkg.go.dev/runtime)
