---
title: "Pattern: Free List"
description: "Duy trì linked list các slot đã giải phóng để cấp/giải phóng O(1) — tái dùng bộ nhớ không gọi allocator hệ thống."
difficulty: "intermediate"
---

# Pattern: Free List

<DifficultyBadge />

## Mô tả một câu

Duy trì linked list các slot đã giải phóng để cấp/giải phóng O(1) — tái dùng bộ nhớ không gọi allocator hệ thống.

<DemoBadge />

## Tương tự thực tế

Bãi đỗ xe giữ chuỗi chỗ trống trên clipboard. Khi xe đến, bạn đưa ra chỗ trống đầu tiên ngay. Khi xe đi, chỗ của nó trở lại đầu danh sách. Không cần quét.

## Ý tưởng cốt lõi

Free list theo dõi slot bộ nhớ trống trong linked list xen qua chính các slot trống (intrusive) hoặc qua mảng index riêng (non-intrusive). `alloc()` pop head; `free()` push lên head. Không phân mảnh trong pool, không system call, hiệu năng O(1) dự đoán được.

```text
  Đầu Free List
       │
       ▼
  ┌────────┐    ┌────────┐    ┌────────┐
  │ slot 3 │───►│ slot 0 │───►│ slot 7 │───► null
  └────────┘    └────────┘    └────────┘

  alloc() → trả slot 3, head dời sang slot 0
  free(5) → slot 5 thành head mới, trỏ tới slot 0
```

| Thuộc tính | Giá trị |
|----------|-------|
| alloc | O(1) — pop từ head |
| free | O(1) — push vào head |
| Phân mảnh | Không trong pool (slot kích thước cố định) |
| Overhead | Một con trỏ mỗi slot trống (intrusive) hoặc mảng index (non-intrusive) |

**Thử ngay** — cấp và giải phóng block, xem free list liên kết các slot trống:

<FreeListViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| Go runtime | [mfixalloc.go#L31-L109](https://github.com/golang/go/blob/f5cdf4745455415c7a43cfc7d925214d4511489b/src/runtime/mfixalloc.go#L31-L109) | `fixalloc` — allocator free-list kích thước cố định. Struct `mlink` (L49-L52) là node list xen đặt lên các block đã giải phóng. `alloc()` (L74-L87) pop từ free list; `free()` (L106-L108) push vào. Free list LIFO kinh điển chạy subsystem bộ nhớ Go. |
| Nhân Linux (SLUB) | [slub.c#L530-L551](https://github.com/torvalds/linux/blob/acb7500801e98639f6d8c2d796ed9f64cba83d3a/mm/slub.c#L530-L551) | `get_freepointer` / `set_freepointer` — đọc/ghi con trỏ next-free nhúng trong mỗi object slab tự do tại `object + s->offset`. Dùng con trỏ XOR-encode (L504-L528) dưới `CONFIG_SLAB_FREELIST_HARDENED` để chống tấn công hư hỏng heap. |

## Triển khai

::: code-group

```typescript [TypeScript]
class FreeList {
  private freeSlots: number[] = [];
  private nextSlot: number;

  constructor(private capacity: number) {
    this.nextSlot = 0;
  }

  alloc(): number | null {
    if (this.freeSlots.length > 0) {
      return this.freeSlots.pop()!;
    }
    if (this.nextSlot >= this.capacity) return null;
    return this.nextSlot++;
  }

  free(slot: number): void {
    this.freeSlots.push(slot);
  }

  get available(): number {
    return this.freeSlots.length + (this.capacity - this.nextSlot);
  }

  get allocated(): number {
    return this.nextSlot - this.freeSlots.length;
  }
}
```

```rust [Rust]
pub struct FreeList {
    capacity: usize,
    next_slot: usize,
    free: Vec<usize>,
}

impl FreeList {
    pub fn new(capacity: usize) -> Self {
        FreeList { capacity, next_slot: 0, free: Vec::new() }
    }

    pub fn alloc(&mut self) -> Option<usize> {
        if let Some(slot) = self.free.pop() {
            return Some(slot);
        }
        if self.next_slot >= self.capacity {
            return None;
        }
        let slot = self.next_slot;
        self.next_slot += 1;
        Some(slot)
    }

    pub fn free(&mut self, slot: usize) {
        self.free.push(slot);
    }

    pub fn available(&self) -> usize {
        self.free.len() + (self.capacity - self.next_slot)
    }

    pub fn allocated(&self) -> usize {
        self.next_slot - self.free.len()
    }
}
```

```go [Go]
type FreeList struct {
	capacity int
	nextSlot int
	free     []int
}

func NewFreeList(capacity int) *FreeList {
	return &FreeList{capacity: capacity, free: nil}
}

func (fl *FreeList) Alloc() (int, bool) {
	if len(fl.free) > 0 {
		slot := fl.free[len(fl.free)-1]
		fl.free = fl.free[:len(fl.free)-1]
		return slot, true
	}
	if fl.nextSlot >= fl.capacity {
		return 0, false
	}
	slot := fl.nextSlot
	fl.nextSlot++
	return slot, true
}

func (fl *FreeList) Free(slot int) {
	fl.free = append(fl.free, slot)
}

func (fl *FreeList) Available() int {
	return len(fl.free) + (fl.capacity - fl.nextSlot)
}

func (fl *FreeList) Allocated() int {
	return fl.nextSlot - len(fl.free)
}
```

```python [Python]
class FreeList:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self._next_slot = 0
        self._free: list[int] = []

    def alloc(self) -> int | None:
        if self._free:
            return self._free.pop()
        if self._next_slot >= self.capacity:
            return None
        slot = self._next_slot
        self._next_slot += 1
        return slot

    def free(self, slot: int) -> None:
        self._free.append(slot)

    @property
    def available(self) -> int:
        return len(self._free) + (self.capacity - self._next_slot)

    @property
    def allocated(self) -> int:
        return self._next_slot - len(self._free)
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai allocator free list với alloc/free và theo dõi | `exercises/typescript/free-list/01-basic.test.ts` |
| Trung bình | Pool có generation với phát hiện handle cũ | `exercises/typescript/free-list/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/free_list/mod.rs` · Go `exercises/go/free_list/free_list_test.go` · Python `exercises/python/free_list/test_free_list.py`

## Khi nào nên dùng

- **Game engine** — pool entity/component với chu kỳ cấp/giải phóng nhanh
- **Kernel OS** — slab allocator cho object kernel kích thước cố định (inode, task struct)
- **Hệ thống nhúng** — không heap, thời gian cấp phát xác định
- **Stack mạng** — buffer pool cho header gói
- **Engine database** — page allocator cho node B-tree

## Khi nào KHÔNG nên dùng

- **Object kích thước thay đổi** — free list yêu cầu slot kích thước cố định (dùng allocator tổng quát)
- **Ít khi giải phóng** — nếu object sống mãi, free list giữ rỗng (dùng bump/arena allocator)
- **Pool nhỏ** — overhead quản lý list vượt lợi ích dưới ~16 slot
- **Cần thread-safe** — free list cơ bản cần đồng bộ bên ngoài (hoặc dùng biến thể lock-free)

## Thêm các ứng dụng production

- [Godot Engine](https://github.com/godotengine/godot/blob/ec67cbe92628bdaf979b10594359ba6f02cf8838/core/templates/pooled_list.h#L57-L131) — `PooledList<T>` free list non-intrusive với mảng index riêng
- [jemalloc](https://github.com/jemalloc/jemalloc) — free list thread-cache cho cấp phát nhỏ
- [mimalloc](https://github.com/microsoft/mimalloc) — free list cấp segment với thiết kế shard
- [Vulkan Memory Allocator](https://github.com/GPUOpen-LibrariesAndSDKs/VulkanMemoryAllocator) — pool sub-allocation với free list

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Arena Allocator](/patterns/arena-allocator/) | Arena giải phóng hàng loạt; free list tái chế slot riêng cho tái dùng O(1) |
| [Object Pool](/patterns/object-pool/) | Object pool dùng free list nội bộ để theo dõi object có sẵn |
| [Ring Buffer (Buffer vòng)](/patterns/ring-buffer/) | Cả hai cung cấp quản lý slot O(1) — ring buffer qua index modulo, free list qua chuỗi liên kết |
| [LRU Cache](/patterns/lru-cache/) | LRU cache dùng free list để tái chế slot node đã loại cho tái dùng O(1) |
| [Skip List](/patterns/skip-list/) | Skip list có thể dùng free list để tái chế slot node đã xoá |
| [Tombstone / Xoá mềm](/patterns/tombstone/) | Xoá dựa trên tombstone hoãn tái chế slot; free list thu hồi các slot đó |
| [Work Stealing](/patterns/work-stealing/) | Queue work-stealing có thể dùng free list để quản lý cấp phát node task |

## Câu hỏi thử thách

::: details Câu 1: Bug làm `free(slot)` được gọi hai lần trên cùng slot. Chuyện gì với free list ngây thơ, và hệ thống production phát hiện thế nào?
**Trả lời:** Slot xuất hiện hai lần trong free list. Hai `alloc()` tiếp theo trả cùng slot, và hai caller ghi vào bộ nhớ chồng lên, gây hư dữ liệu.

Double-free là một trong những bug bộ nhớ nguy hiểm nhất. Kỹ thuật phát hiện gồm: bitmap theo dõi slot nào đã cấp (check trước khi giải phóng), giá trị poison ghi vào slot đã giải phóng (phát hiện nếu giá trị đã là poison), và cách của Linux SLUB là XOR-encode con trỏ free list với giá trị ngẫu nhiên mỗi cache nên hư hỏng được phát hiện ở alloc tiếp. Một số allocator abort ngay khi double-free thay vì âm thầm hư.
:::

::: details Câu 2: Free list intrusive lưu con trỏ "next" trong chính slot trống. Lợi thế so với mảng index riêng là gì, rủi ro là gì?
**Trả lời:** List intrusive dùng không thêm bộ nhớ — con trỏ next chiếm chỗ không dùng đến (slot trống). Rủi ro là bug use-after-free có thể ghi đè con trỏ next, làm hư toàn bộ free list.

Với thiết kế non-intrusive (mảng index riêng), làm hư dữ liệu slot đã giải phóng không phá cấu trúc free list. Với thiết kế intrusive, nếu code vô tình ghi vào slot đã giải phóng, nó ghi đè con trỏ next và chuỗi free list bị phá — alloc tiếp theo có thể trả địa chỉ rác. Đó là lý do SLUB Linux dùng `CONFIG_SLAB_FREELIST_HARDENED` để XOR-encode con trỏ.
:::

::: details Câu 3: Free list trả slot mới giải phóng gần nhất (LIFO). Sao tốt hơn cho hiệu năng so với trả slot giải phóng cũ nhất (FIFO)?
**Trả lời:** Slot giải phóng gần nhất có khả năng vẫn trong cache CPU. Tái dùng nó ngay cho tỉ lệ cache hit tốt hơn trả slot giải phóng từ lâu.

Tái dùng LIFO là tối ưu cache có chủ ý. Khi bạn free slot N và alloc ngay, bạn nhận lại slot N — vừa được truy cập và có khả năng vẫn trong cache L1/L2. FIFO sẽ trả slot giải phóng nhiều thao tác trước, có lẽ đã bị loại khỏi cache. Cho hot path cấp phát (game engine làm hàng nghìn alloc/free mỗi frame), khác biệt cache locality này đo được.
:::

::: details Câu 4: Bạn có pool free list 1.000 slot. Giám sát cho thấy pool 95% allocated ở trạng thái ổn định, và alloc() thường trả null. Có nên tăng kích thước pool?
**Trả lời:** Không nhất thiết. Đầu tiên kiểm tra slot allocated có thực sự đang dùng hay bị rò (cấp nhưng không bao giờ giải phóng).

Bug phổ biến là quên gọi `free()` trên slot không còn cần, làm pool cạn từ từ. Thêm slot chỉ trì hoãn cạn kiệt không tránh khỏi. Kiểm tra count `allocated` theo thời gian — nếu tăng đơn điệu, bạn có rò. Nếu dao động quanh 950 với đỉnh đôi khi tới 1000, thì pool thực sự quá nhỏ và nên tăng.
:::
