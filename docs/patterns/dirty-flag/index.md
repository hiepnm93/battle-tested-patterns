---
title: "Pattern: Dirty Flag"
description: 'Đánh dấu object là "dirty" khi sửa, hoãn tính lại tốn kém cho tới khi giá trị thực sự cần, rồi xoá cờ.'
difficulty: "beginner"
---

# Pattern: Dirty Flag

<DifficultyBadge />

## Mô tả một câu

Đánh dấu object là "dirty" khi sửa, hoãn tính lại tốn kém cho tới khi giá trị thực sự cần, rồi xoá cờ.

<DemoBadge />

## Tương tự thực tế

Biển "cần dọn" treo trên cửa phòng khách sạn. Buồng phòng chỉ vào phòng đánh dấu dirty. Nếu khách chưa vào phòng, biển vẫn sạch, và buồng phòng bỏ qua — không lãng phí công.

## Ý tưởng cốt lõi

Pattern dirty flag tránh tính toán dư thừa bằng cách theo dõi state dẫn xuất có cũ chưa. Khi giá trị nguồn đổi, thay vì tính lại ngay mọi giá trị phụ thuộc, ta chỉ set cờ "dirty". Tính lại tốn kém chỉ xảy ra khi giá trị dẫn xuất thực sự được yêu cầu. Sau khi tính lại, cờ được xoá. Điều này đánh đổi một check boolean ở mỗi đọc lấy các tính toán có thể tốn kém mà có thể không bao giờ cần.

```text
  Chu kỳ mutation:

  ┌─────────┐   set()     ┌─────────────┐
  │  Clean  │ ──────────► │    Dirty    │
  │ (cache  │             │ (cache cũ)  │
  │ hợp lệ) │             │             │
  └─────────┘             └──────┬──────┘
       ▲                         │
       │         get()           │
       │   (tính lại + clear)    │
       └─────────────────────────┘

  Timeline:
  set(x)  set(y)  set(z)  get()      set(w)  get()
    │       │       │       │          │       │
    ▼       ▼       ▼       ▼          ▼       ▼
  dirty  dirty   dirty  tính lại    dirty   tính lại
                       (1 lần)              (1 lần)
                          ▲                  ▲
        3 mutation,       │   1 mutation,    │
        1 tính toán ──────┘   1 tính toán ───┘
```

| Thuộc tính | Giá trị |
|----------|-------|
| Chi phí mutation | O(1) — chỉ set một cờ boolean |
| Chi phí đọc (clean) | O(1) — trả giá trị cache |
| Chi phí đọc (dirty) | O(tính lại) — compute + cache + clear cờ |
| Bộ nhớ | O(1) mỗi giá trị theo dõi — một cờ boolean |

**Thử ngay** — di chuyển entity để đánh dấu dirty, rồi tính lại để xem tiết kiệm tối ưu:

<DirtyFlagViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| Chromium/Blink | [layout_object.h#L1425-L1430](https://github.com/chromium/chromium/blob/5cffea3f665b7762369a0fa84d2f208875e7225e/third_party/blink/renderer/core/layout/layout_object.h#L1425-L1430) | `NeedsLayout()` trả về geometry của object layout có dirty không. Khi property CSS đổi, `SetNeedsLayout()` đánh dấu node và ancestor là dirty. Tính layout chỉ xảy ra lúc pass layout tiếp theo — không phải mọi thay đổi style. Điều này gom hàng trăm sửa DOM thành một lần tính layout. |
| React | [ReactFiberFlags.js#L18-L22](https://github.com/facebook/react/blob/34b78a2897cc208260a88e6b62ecaf9ca2a9dfe4/packages/react-reconciler/src/ReactFiberFlags.js#L18-L22) | Cờ fiber như `Placement`, `Update`, `Deletion` là dirty flag trên node fiber. Khi state đổi, fiber được đánh dấu cờ. Pha commit chỉ xử lý fiber có cờ khác 0, bỏ qua hoàn toàn subtree không đổi. |

## Triển khai

::: code-group

```typescript [TypeScript]
class DirtyFlag<T> {
  private dirty = true;
  private cached: T | undefined;

  constructor(private compute: () => T) {}

  /** Đánh dấu dirty — get() tiếp theo sẽ tính lại. */
  markDirty(): void {
    this.dirty = true;
  }

  /** Lấy giá trị. Tính lại chỉ khi dirty. */
  get(): T {
    if (this.dirty) {
      this.cached = this.compute();
      this.dirty = false;
    }
    return this.cached!;
  }

  get isDirty(): boolean {
    return this.dirty;
  }
}

/** Node transform với cache ma trận world dựa trên dirty flag. */
class TransformNode {
  private localX = 0;
  private localY = 0;
  private worldDirty = true;
  private worldX = 0;
  private worldY = 0;
  private children: TransformNode[] = [];
  private parent: TransformNode | null = null;

  setPosition(x: number, y: number): void {
    this.localX = x;
    this.localY = y;
    this.markWorldDirty();
  }

  getWorldPosition(): { x: number; y: number } {
    if (this.worldDirty) {
      if (this.parent) {
        const pw = this.parent.getWorldPosition();
        this.worldX = pw.x + this.localX;
        this.worldY = pw.y + this.localY;
      } else {
        this.worldX = this.localX;
        this.worldY = this.localY;
      }
      this.worldDirty = false;
    }
    return { x: this.worldX, y: this.worldY };
  }

  addChild(child: TransformNode): void {
    child.parent = this;
    this.children.push(child);
    child.markWorldDirty();
  }

  private markWorldDirty(): void {
    this.worldDirty = true;
    for (const child of this.children) {
      child.markWorldDirty();
    }
  }
}
```

```rust [Rust]
pub struct DirtyFlag<T, F: Fn() -> T> {
    dirty: bool,
    cached: Option<T>,
    compute: F,
}

impl<T, F: Fn() -> T> DirtyFlag<T, F> {
    pub fn new(compute: F) -> Self {
        DirtyFlag { dirty: true, cached: None, compute }
    }

    pub fn mark_dirty(&mut self) {
        self.dirty = true;
    }

    pub fn get(&mut self) -> &T {
        if self.dirty {
            self.cached = Some((self.compute)());
            self.dirty = false;
        }
        self.cached.as_ref().unwrap()
    }

    pub fn is_dirty(&self) -> bool {
        self.dirty
    }
}
```

```go [Go]
type DirtyFlag[T any] struct {
	dirty   bool
	cached  T
	compute func() T
}

func NewDirtyFlag[T any](compute func() T) *DirtyFlag[T] {
	return &DirtyFlag[T]{dirty: true, compute: compute}
}

func (d *DirtyFlag[T]) MarkDirty() {
	d.dirty = true
}

func (d *DirtyFlag[T]) Get() T {
	if d.dirty {
		d.cached = d.compute()
		d.dirty = false
	}
	return d.cached
}

func (d *DirtyFlag[T]) IsDirty() bool {
	return d.dirty
}
```

```python [Python]
from typing import TypeVar, Generic, Callable

T = TypeVar("T")

class DirtyFlag(Generic[T]):
    def __init__(self, compute: Callable[[], T]):
        self._compute = compute
        self._dirty = True
        self._cached: T | None = None

    def mark_dirty(self) -> None:
        self._dirty = True

    def get(self) -> T:
        if self._dirty:
            self._cached = self._compute()
            self._dirty = False
        return self._cached  # type: ignore

    @property
    def is_dirty(self) -> bool:
        return self._dirty
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai wrapper tính toán lười dựa trên dirty flag | `exercises/typescript/dirty-flag/01-basic.test.ts` |
| Trung bình | Xây phân cấp transform với cache vị trí thế giới qua dirty flag | `exercises/typescript/dirty-flag/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/dirty_flag/mod.rs` · Go `exercises/go/dirty_flag/dirty_flag_test.go` · Python `exercises/python/dirty_flag/test_dirty_flag.py`

## Khi nào nên dùng

- **Engine layout UI** — đánh dấu node dirty khi đổi style, gom tính layout
- **Scene graph game** — transform world dirty lan từ cha xuống con; tính lại chỉ khi render
- **Cell bảng tính** — đánh dấu cell phụ thuộc dirty khi input đổi, tính lại khi hiển thị
- **Hệ build** — đánh dấu target dirty khi file nguồn đổi, build lại chỉ cái cần
- **Cache state dẫn xuất** — bất kỳ property tính được tốn kém và đọc ít hơn input đổi

## Khi nào KHÔNG nên dùng

- **Tính lại rẻ** — nếu tính toán mất nanosecond, check cờ thêm overhead không lợi ích
- **Mọi mutation cần kết quả** — nếu luôn đọc sau mỗi ghi, bạn chỉ thêm check cờ vào mọi thao tác
- **Concurrency không đồng bộ** — dirty flag vốn là state mutable chia sẻ; đọc và ghi đồng thời cần lock hoặc atomic

## Thêm các ứng dụng production

- [Unity Engine](https://github.com/Unity-Technologies/UnityCsReference) — cờ `Transform.hasChanged` hoãn tính lại ma trận world
- [Qt Framework](https://github.com/qt/qtbase/blob/70891a20ed56ac28c8d4c8265266a06700ce5a09/src/widgets/kernel/qwidget.cpp) — `QWidget::update()` đánh dấu vùng dirty; vẽ xảy ra ở vòng event loop tiếp
- [Make](https://www.gnu.org/software/make/) — thời gian sửa file như dirty flag; chỉ build target mới hơn nguồn
- [Excel/Google Sheets](https://support.google.com) — đồ thị phụ thuộc cell với lan dirty; chỉ tính lại subgraph đổi

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Observer](/patterns/observer/) | Observer thông báo khi state đổi; dirty flag hoãn phản ứng cho tới khi cần |
| [Bitmask](/patterns/bitmask/) | Dirty flag được lưu hiệu quả dưới dạng bit trong bitmask |
| [Dependency Graph](/patterns/dependency-graph/) | Lan dirty đi theo cạnh dependency graph để đánh dấu node downstream |
| [Double Buffering](/patterns/double-buffering/) | Dirty flag theo dõi buffer nào đã đổi và cần hoán đổi |

## Câu hỏi thử thách

::: details Câu 1: Scene graph có 1000 node. Root di chuyển, làm mọi descendant dirty. Nhưng chỉ 3 node thực sự được render frame này. Bao nhiêu tính lại xảy ra?
**Trả lời:** 3 tính lại (cộng ancestor của mỗi node được render).

Set 1000 node dirty tốn O(1000) — chỉ lật boolean. Nhưng tính lại chỉ xảy ra khi `getWorldPosition()` được gọi trên node. Chỉ 3 node được render kích hoạt tính lại, và mỗi cái đi lên root để tính chuỗi. Nếu 3 node chia sẻ ancestor, ancestor đó được tính lại một lần và cache (cờ xoá).

Đây là insight then chốt: chi phí dirty-flag tỉ lệ với node **được đọc**, không phải node **được đánh dấu dirty**.
:::

::: details Câu 2: React đánh dấu node fiber bằng cờ như Placement|Update. Tại sao dùng cờ bitmask thay vì cờ dirty boolean đơn giản?
**Trả lời:** Nhiều loại "dirty" trực giao.

Một node fiber có thể cần placement (DOM node mới), update (đổi prop), deletion, update ref, hoặc effect layout — tất cả độc lập. Một boolean duy nhất chỉ nói được "có gì đó đổi." Cờ bitmask mã hoá **cái gì** đổi, nên pha commit có thể xử lý mỗi loại công việc riêng mà không cần xem lại fiber.

Đây là kết hợp pattern Dirty Flag và pattern Bitmask — mỗi bit là dirty flag độc lập cho một quan tâm cụ thể.
:::

::: details Câu 3: Cache dirty-flag của bạn có bug: `get()` trả dữ liệu cũ. Cờ được set đúng. Có gì sai?
**Trả lời:** Hàm compute bắt closure hoặc reference cũ.

Nguyên nhân phổ biến:

1. Hàm compute đóng trên biến đã được gán lại (stale closure trong React, ví dụ).
2. Hàm compute đọc từ nguồn cache/memoize tự nó cũ.
3. Cờ dirty được clear trước khi tính toán xong (compute bất đồng bộ).

Sửa: đảm bảo hàm compute đọc giá trị hiện tại lúc gọi, không phải giá trị bắt lúc đăng ký. Trong React, đây là lý do `useMemo` lấy mảng dependency — nó tạo hàm compute mới khi dependency đổi.
:::

::: details Câu 4: Hệ build của bạn dùng timestamp sửa file làm dirty flag. Một dev checkout branch cũ, reset timestamp file thành "bây giờ". Hệ build thấy mọi file "dirty" và kích hoạt build full. Sửa thế nào?
**Trả lời:** Dùng content hash thay vì (hoặc thêm) timestamp làm dirty flag.

Timestamp rẻ để kiểm tra nhưng mong manh về ngữ nghĩa — chúng theo dõi *khi* file đổi, không phải *có* thực sự đổi. Git checkout, copy file, trích artifact CI và clock skew đều sinh timestamp gây hiểu lầm. Dirty flag dựa trên content (ví dụ SHA-256 của file) miễn nhiễm với vấn đề này: nếu hash khớp, file không đổi, bất kể timestamp. Đó là lý do Bazel và Buck dùng content hashing thay vì timestamp. Đánh đổi là tính hash đắt hơn `stat()`, nhưng cho hệ build, chi phí biên dịch không cần xa vượt chi phí hashing.
:::
