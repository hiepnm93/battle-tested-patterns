---
title: "Pattern: Reference Counting"
description: "Theo dõi chủ sở hữu qua bộ đếm atomic, tự dọn dẹp khi về 0 — vòng đời tài nguyên xác định không cần garbage collection."
difficulty: "beginner"
---

# Pattern: Reference Counting

<DifficultyBadge />

## Mô tả một câu

Theo dõi chủ sở hữu qua bộ đếm atomic, tự dọn dẹp khi về 0 — vòng đời tài nguyên xác định không cần garbage collection.

<DemoBadge />

## Tương tự thực tế

Tài khoản Netflix chung. Bạn theo dõi bao nhiêu người đang dùng. Khi người cuối cùng huỷ, subscription chấm dứt. Không cần kiểm tra nền — đếm về 0 là tín hiệu.

## Ý tưởng cốt lõi

Reference counting gán mỗi tài nguyên chia sẻ một bộ đếm. Mỗi chủ sở hữu mới (clone) tăng nó; mỗi giải phóng (drop) giảm nó. Khi bộ đếm về 0, tài nguyên được dọn dẹp ngay — không pause GC, không queue finalizer, hoàn toàn xác định.

```text
  ┌────────────┐
  │  Resource  │   refcount = 1
  │  (value)   │
  └─────┬──────┘
        │
     owner A

  A.clone() → B
  ┌────────────┐
  │  Resource  │   refcount = 2
  │  (value)   │
  └──┬─────┬───┘
     │     │
  owner A  owner B

  A.drop()
  ┌────────────┐
  │  Resource  │   refcount = 1
  │  (value)   │
  └─────┬──────┘
        │
     owner B

  B.drop()
  ┌────────────┐
  │  Resource  │   refcount = 0 → cleanup()!
  │  (value)   │
  └────────────┘
```

| Thuộc tính | Giá trị |
|----------|-------|
| Clone | O(1) — tăng bộ đếm |
| Drop | O(1) — giảm bộ đếm, dọn dẹp có điều kiện |
| Kích hoạt dọn dẹp | Xác định — chính xác khi chủ cuối drop |
| Thread safety | Cần thao tác atomic (hoặc mutex) cho dùng đa luồng |

**Thử ngay** — drop reference để giảm ref count và xem object được giải phóng khi rc=0:

<ReferenceCountingViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| CPython | [refcount.h#L255-L310](https://github.com/python/cpython/blob/ff64d8de66ab7f8e56b5d410796a7d76c955280c/Include/refcount.h#L255-L310) | `Py_INCREF` (L255-L310) là hàm inline tăng `ob_refcnt`. `Py_DECREF` (L417-L430) giảm và gọi `_Py_Dealloc` khi về 0. Mọi object Python mang `ob_refcnt` trong `PyObject` ([object.h#L127-L150](https://github.com/python/cpython/blob/ff64d8de66ab7f8e56b5d410796a7d76c955280c/Include/object.h#L127-L150)). Đây là cơ chế quản lý bộ nhớ chính — GC chỉ tồn tại để phá chu trình tham chiếu. |
| Stdlib Rust | [sync.rs#L269-L276](https://github.com/rust-lang/rust/blob/ab26b175979ee7b2cb3302dce204b99df96f7efb/library/alloc/src/sync.rs#L269-L276) | Struct `Arc<T>` (Atomic Reference Counted) tại L269. Impl `Drop` (L2799-L2875) gọi `fetch_sub(1, Release)` trên strong count, fence Acquire, rồi `drop_slow()` khi về 0. Dùng khắp Tokio, Actix và code Rust cấp OS. |

## Triển khai

::: code-group

```typescript [TypeScript]
type CleanupFn<T> = (value: T) => void;

interface RefCountedInner<T> {
  value: T;
  count: number;
  dropped: boolean;
  cleanup: CleanupFn<T>;
}

class RefCounted<T> {
  private inner: RefCountedInner<T>;
  private owned: boolean;

  constructor(value: T, cleanup: CleanupFn<T>) {
    this.inner = { value, count: 1, dropped: false, cleanup };
    this.owned = true;
  }

  /** Tạo chủ mới chia sẻ cùng giá trị. */
  clone(): RefCounted<T> {
    if (!this.owned) throw new Error('Cannot clone a dropped reference');
    this.inner.count++;
    const cloned = Object.create(RefCounted.prototype) as RefCounted<T>;
    cloned.inner = this.inner;
    cloned.owned = true;
    return cloned;
  }

  /** Giải phóng reference của chủ này. Kích hoạt cleanup khi count = 0. */
  drop(): void {
    if (!this.owned) return; // double-drop là no-op
    this.owned = false;
    this.inner.count--;
    if (this.inner.count === 0 && !this.inner.dropped) {
      this.inner.dropped = true;
      this.inner.cleanup(this.inner.value);
    }
  }

  refCount(): number { return this.inner.count; }

  value(): T {
    if (!this.owned) throw new Error('Reference has been dropped');
    return this.inner.value;
  }
}
```

```rust [Rust]
use std::cell::Cell;

struct RcInner<T> {
    value: T,
    count: Cell<usize>,
}

pub struct Rc<T> {
    inner: *const RcInner<T>,
}

impl<T> Rc<T> {
    pub fn new(value: T) -> Self {
        let inner = Box::into_raw(Box::new(RcInner {
            value,
            count: Cell::new(1),
        }));
        Rc { inner }
    }

    pub fn strong_count(&self) -> usize {
        unsafe { (*self.inner).count.get() }
    }

    pub fn value(&self) -> &T {
        unsafe { &(*self.inner).value }
    }
}

impl<T> Clone for Rc<T> {
    fn clone(&self) -> Self {
        unsafe {
            let c = (*self.inner).count.get();
            (*self.inner).count.set(c + 1);
        }
        Rc { inner: self.inner }
    }
}

impl<T> Drop for Rc<T> {
    fn drop(&mut self) {
        unsafe {
            let c = (*self.inner).count.get();
            (*self.inner).count.set(c - 1);
            if c == 1 {
                drop(Box::from_raw(self.inner as *mut RcInner<T>));
            }
        }
    }
}
```

```go [Go]
type RefCounted[T any] struct {
	mu      sync.Mutex
	value   T
	count   int
	cleanup func(T)
}

func NewRefCounted[T any](value T, cleanup func(T)) *RefCounted[T] {
	return &RefCounted[T]{value: value, count: 1, cleanup: cleanup}
}

func (rc *RefCounted[T]) Clone() *RefCounted[T] {
	rc.mu.Lock()
	defer rc.mu.Unlock()
	rc.count++
	return rc // cùng con trỏ, state chia sẻ
}

func (rc *RefCounted[T]) Drop() {
	rc.mu.Lock()
	defer rc.mu.Unlock()
	rc.count--
	if rc.count == 0 {
		rc.cleanup(rc.value)
	}
}

func (rc *RefCounted[T]) Count() int {
	rc.mu.Lock()
	defer rc.mu.Unlock()
	return rc.count
}
```

```python [Python]
from typing import TypeVar, Generic, Callable, Optional

T = TypeVar("T")

class RefCounted(Generic[T]):
    def __init__(self, value: T, cleanup: Callable[[T], None]):
        self._value = value
        self._count = 1
        self._dropped = False
        self._cleanup = cleanup
        self._owned = True

    def clone(self) -> "RefCounted[T]":
        if not self._owned:
            raise RuntimeError("Cannot clone a dropped reference")
        self._count += 1
        copy = object.__new__(RefCounted)
        # Chia sẻ state nội bộ qua reference
        copy.__dict__ = self.__dict__
        copy._owned = True
        return copy

    def drop(self) -> None:
        if not self._owned:
            return
        self._owned = False
        self._count -= 1
        if self._count == 0 and not self._dropped:
            self._dropped = True
            self._cleanup(self._value)

    @property
    def ref_count(self) -> int:
        return self._count

    @property
    def value(self) -> T:
        if not self._owned:
            raise RuntimeError("Reference has been dropped")
        return self._value
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai giá trị ref-counted với clone/drop và callback cleanup | `exercises/typescript/reference-counting/01-basic.test.ts` |
| Trung bình | Mở rộng với weak reference không ngăn cleanup | `exercises/typescript/reference-counting/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/reference_counting/mod.rs` · Go `exercises/go/reference_counting/reference_counting_test.go` · Python `exercises/python/reference_counting/test_reference_counting.py`

## Khi nào nên dùng

- **Sở hữu chung với dọn dẹp xác định** — nhiều phần code cần cùng tài nguyên, và bạn cần nó giải phóng ngay khi người dùng cuối xong (file handle, GPU buffer, kết nối database)
- **Tránh pause GC** — hệ realtime (game, audio) nơi stop-the-world GC không chấp nhận được
- **Interop giữa ngôn ngữ** — refcount của CPython cho extension C quản lý object Python tự nhiên; COM dùng `AddRef`/`Release` qua ranh giới DLL
- **State chia sẻ sống ngắn** — khi object chủ yếu sở hữu bởi một nơi nhưng thỉnh thoảng chia sẻ ngắn (pattern `Rc`/`Arc` của Rust)

## Khi nào KHÔNG nên dùng

- **Cấu trúc dữ liệu chu trình** — chu trình cha-con (ví dụ doubly linked list, node đồ thị) rò vì count không bao giờ về 0. Dùng weak reference hoặc GC tracing.
- **Chia sẻ tranh chấp cao** — nếu nhiều thread liên tục clone/drop cùng object, bộ đếm atomic trở thành điểm nghẽn cache-line. Cân nhắc epoch-based reclamation hoặc hazard pointer.
- **Mẫu cấp phát hàng loạt** — nếu bạn cấp/giải phóng hàng nghìn object nhỏ, bộ đếm mỗi object thêm overhead. Dùng arena allocation.

## Thêm các ứng dụng production

- [Swift ARC](https://github.com/apple/swift) — toàn bộ mô hình bộ nhớ của Swift xây trên automatic reference counting (retain/release do compiler chèn)
- [COM IUnknown](https://learn.microsoft.com/en-us/windows/win32/api/unknwn/nn-unknwn-iunknown) — `AddRef`/`Release` qua mọi object COM trong Windows
- [Linux kernel kobject](https://github.com/torvalds/linux/blob/acb7500801e98639f6d8c2d796ed9f64cba83d3a/lib/kobject.c) — `kref` cung cấp reference counting cho object kernel
- [Objective-C ARC](https://clang.llvm.org/docs/AutomaticReferenceCounting.html) — gọi `retain`/`release` do compiler quản lý

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Copy-on-Write (CoW)](/patterns/copy-on-write/) | Reference counting xác định khi nào giá trị CoW cần copy |
| [Object Pool](/patterns/object-pool/) | Pool cung cấp thay thế cho reference counting — trả object thay vì giải phóng |
| [Tombstone](/patterns/tombstone/) | Tombstone hoãn cleanup như reference counting hoãn giải phóng |
| [Arena Allocator](/patterns/arena-allocator/) | Arena tránh reference counting mỗi object bằng cách giải phóng tất cả khi phạm vi kết thúc |

## Câu hỏi thử thách

::: details Câu 1: Object A tham chiếu B, và B tham chiếu A. Cả hai có refcount 2. Bạn drop handle của bạn với A. Chuyện gì xảy ra?
**Trả lời:** Rò bộ nhớ. Drop handle của bạn với A giảm refcount của A xuống 1 (B vẫn tham chiếu A). Refcount của A không bao giờ về 0, nên A không bao giờ được giải phóng. Vì A không bao giờ giải phóng, nó không bao giờ drop reference tới B, nên refcount của B giữ 1 mãi.

Đây là **bài toán chu trình tham chiếu** — điểm yếu cơ bản của reference counting. Giải pháp: (1) dùng weak reference cho back-pointer (`Weak<T>` của Rust, `weakref` của Python), (2) thêm GC phát hiện chu trình lên trên (CPython làm vậy), (3) thiết kế lại để tránh chu trình hoàn toàn.
:::

::: details Câu 2: CPython dùng refcounting làm chiến lược GC chính, nhưng vẫn có cycle collector. Sao không chỉ dùng refcounting?
**Trả lời:** Reference counting đơn không thể thu hồi chu trình tham chiếu. Bất kỳ cấu trúc dữ liệu nào có tham chiếu lẫn nhau (cha-con, cạnh đồ thị, closure bắt `self`) sẽ rò.

Cycle collector của CPython (module `gc`) định kỳ đi các object *có thể* tạo chu trình (container như list, dict, object có `__dict__`) và xác định nhóm không thể đến. Refcount xử lý ~95% object không tham gia chu trình, làm việc của cycle collector nhẹ hơn. Cách lai này cho dọn dẹp xác định cho hầu hết object trong khi vẫn xử lý chu trình.
:::

::: details Câu 3: `Arc` của Rust dùng `fetch_add(1, Relaxed)` cho Clone nhưng `fetch_sub(1, Release)` cho Drop. Vì sao thứ tự bộ nhớ khác?
**Trả lời:** Clone chỉ cần đảm bảo bộ đếm được tăng — không dữ liệu nào được truy cập hoặc giải phóng, nên `Relaxed` (thứ tự rẻ nhất) đủ. Bộ đếm chỉ cần lên atomic.

Drop khác: trước khi giải phóng tài nguyên, mọi ghi trước đó của mọi thread phải hiển thị. `Release` trên giảm đảm bảo thread làm cleanup cuối (dùng fence `Acquire`) thấy mọi dữ liệu ghi bởi mọi thread từng giữ reference. Không có điều này, destructor có thể đọc dữ liệu cũ.

Trên x86 (Total Store Ordering), cả thao tác RMW `Relaxed` và `Release` biên dịch thành cùng lệnh `lock xadd` — phân biệt miễn phí trên x86. Thứ tự quan trọng trên kiến trúc yếu thứ tự như ARM, nơi `Release` cần store barrier. Rust dùng `Relaxed` cho clone và `Release` cho drop để đảm bảo tính đúng qua mọi kiến trúc.
:::

::: details Câu 4: Bạn xây resource pool. Nên dùng reference counting hay finalizer/destructor?
**Trả lời:** Không cái nào đơn lý tưởng cho pool. Reference counting kích hoạt cleanup khi về 0, nhưng "cleanup" cho tài nguyên pool nên nghĩa "trả về pool", không phải "huỷ".

Pattern đúng là: bọc item pool trong handle ref-counted nơi callback "cleanup" trả item về pool thay vì giải phóng. Đây chính xác cách pool kết nối database hoạt động — `Drop` trên handle trả kết nối thay vì đóng nó. Pool tự quản lý huỷ thực tế (ví dụ khi shutdown hoặc khi kết nối cũ).
:::
