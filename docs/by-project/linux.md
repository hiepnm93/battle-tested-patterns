---
title: "Pattern trong nhân Linux"
description: "Pattern lập trình từ nhân Linux: bitmask, semaphore, ring buffer, trie, LRU cache, free list, vtable và nhiều hơn."
---

# Pattern trong nhân Linux

Nhân Linux đã được tinh chỉnh qua 30+ năm. Các pattern này đã sống sót qua hàng thập kỷ sử dụng thực tế trên hàng triệu thiết bị.

| Pattern | Ở đâu trong Linux | Tác dụng |
|---------|---------------|--------------|
| [Bitmask](/patterns/bitmask/) | [`include/uapi/linux/stat.h`](https://github.com/torvalds/linux/blob/acb7500801e98639f6d8c2d796ed9f64cba83d3a/include/uapi/linux/stat.h#L25-L33) | Bit phân quyền file (`rwxrwxrwx`) |
| [Min Heap](/patterns/min-heap/) | [`kernel/sched/fair.c` (CFS)](https://github.com/torvalds/linux/blob/acb7500801e98639f6d8c2d796ed9f64cba83d3a/kernel/sched/fair.c#L1407-L1460) | Completely Fair Scheduler — chọn task có vruntime thấp nhất |
| [Ring Buffer](/patterns/ring-buffer/) | [`include/linux/ring_buffer.h`](https://github.com/torvalds/linux/blob/acb7500801e98639f6d8c2d796ed9f64cba83d3a/include/linux/ring_buffer.h#L12-L70) | Ghi log event ftrace, buffer lock-free theo từng CPU |
| [State Machine](/patterns/state-machine/) | [`net/ipv4/tcp_input.c`](https://github.com/torvalds/linux/blob/acb7500801e98639f6d8c2d796ed9f64cba83d3a/net/ipv4/tcp_input.c#L4865-L4920) | State machine kết nối TCP (SYN_SENT → ESTABLISHED → FIN_WAIT) |
| [Semaphore](/patterns/semaphore/) | [`include/linux/semaphore.h`](https://github.com/torvalds/linux/blob/acb7500801e98639f6d8c2d796ed9f64cba83d3a/include/linux/semaphore.h#L15-L55) | Counting semaphore của kernel với `down()`/`up()` |
| [Backpressure](/patterns/backpressure/) | [`net/ipv4/tcp_output.c`](https://github.com/torvalds/linux/blob/acb7500801e98639f6d8c2d796ed9f64cba83d3a/net/ipv4/tcp_output.c) | Cửa sổ tắc nghẽn TCP (`cwnd`) — backpressure kiểm soát luồng |
| [Free List](/patterns/free-list/) | [`mm/slub.c`](https://github.com/torvalds/linux/blob/acb7500801e98639f6d8c2d796ed9f64cba83d3a/mm/slub.c#L530-L551) | Slab allocator SLUB — free list xen với con trỏ được làm cứng bằng XOR |
| [Trie](/patterns/trie/) | [`net/ipv4/fib_trie.c`](https://github.com/torvalds/linux/blob/acb7500801e98639f6d8c2d796ed9f64cba83d3a/net/ipv4/fib_trie.c#L80-L120) | Bảng định tuyến IP dưới dạng trie nén (LC-trie) |
| [Vtable](/patterns/vtable/) | [`include/linux/fs.h`](https://github.com/torvalds/linux/blob/acb7500801e98639f6d8c2d796ed9f64cba83d3a/include/linux/fs.h#L2093-L2163) | Struct `file_operations` — vtable con trỏ hàm cho dispatch VFS (`.read`, `.write`, `.open`) |
| [Batch Processing](/patterns/batch-processing/) | [`block/blk-merge.c`](https://github.com/torvalds/linux/blob/acb7500801e98639f6d8c2d796ed9f64cba83d3a/block/blk-merge.c#L350-L395) | Block layer gộp request I/O liền kề để phân bổ thời gian seek |
| [Rate Limiter](/patterns/rate-limiter/) | [`net/sched/sch_tbf.c`](https://github.com/torvalds/linux/blob/acb7500801e98639f6d8c2d796ed9f64cba83d3a/net/sched/sch_tbf.c#L98-L114) | Bộ lọc token bucket cho kiểm soát traffic kernel |
| [Reference Counting](/patterns/reference-counting/) | [`lib/kobject.c`](https://github.com/torvalds/linux/blob/acb7500801e98639f6d8c2d796ed9f64cba83d3a/lib/kobject.c) | `kref` cung cấp reference counting cho object kernel |

## Cách chúng kết hợp: Đọc một file

Khi một process gọi `read()`, nhiều pattern kích hoạt trong một syscall duy nhất:

<CompositionFlow variant="linux-read" />

Trừu tượng "mọi thứ đều là file" hoạt động được vì vtable dispatch cho phép kernel xử lý file ext4, network socket và entry `/proc` như nhau. Kiểm tra phân quyền bằng bitmask diễn ra một lần bất kể loại filesystem. Và reference counting đảm bảo không tài nguyên nào bị giải phóng khi đang dùng — kể cả khi process khác xoá file.

## Đọc thêm

- [Source Linux (mirror GitHub)](https://github.com/torvalds/linux)
- [Tài liệu nhân Linux](https://www.kernel.org/doc/html/latest/)
