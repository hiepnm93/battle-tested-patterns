---
title: "Pattern: Vtable / Ops Dispatch"
description: "Gom con trỏ hàm vào một struct để đạt đa hình lúc runtime — nền tảng thủ công đằng sau interface, trait và virtual method."
difficulty: "advanced"
---

# Pattern: Vtable / Ops Dispatch

<DifficultyBadge />

## Mô tả một câu

Gom con trỏ hàm vào một struct để đạt đa hình lúc runtime — nền tảng thủ công đằng sau interface, trait và virtual method.

<DemoBadge />

## Tương tự thực tế

Menu nhà hàng nơi mỗi món ăn liên kết tới thẻ công thức riêng trong bếp. Bồi bàn không biết nấu — họ chỉ tra thẻ công thức cho món được gọi và đưa tới đầu bếp đúng. Các nhà hàng khác nhau có thể có thẻ công thức khác cho cùng tên món.

## Ý tưởng cốt lõi

Vtable (bảng hàm ảo) là struct chứa con trỏ hàm định nghĩa các thao tác có sẵn trên một kiểu. Mỗi "object" lưu con trỏ tới vtable cùng với dữ liệu. Để gọi method, bạn gián tiếp qua con trỏ vtable — đây là cách C đạt đa hình không cần class, và cách compiler triển khai interface và virtual method bên dưới.

```text
  Circle                   Rectangle
  ┌──────────┐             ┌──────────┐
  │ data:    │             │ data:    │
  │  r = 5   │             │  w = 4   │
  │          │             │  h = 6   │
  │ vtable ──┼──┐          │ vtable ──┼──┐
  └──────────┘  │          └──────────┘  │
                ▼                        ▼
  ┌──────────────────┐   ┌──────────────────┐
  │  circle_vtable   │   │   rect_vtable    │
  ├──────────────────┤   ├──────────────────┤
  │ area:  pi*r*r    │   │ area:  w*h       │
  │ perim: 2*pi*r    │   │ perim: 2*(w+h)   │
  └──────────────────┘   └──────────────────┘

  Dispatch: shape.vtable.area(shape.data)
```

| Thuộc tính | Giá trị |
|----------|-------|
| Overhead gọi | Một lần gián tiếp qua con trỏ (tra vtable) |
| Thêm kiểu mới | Thêm vtable mới — không thay code có sẵn |
| Thêm thao tác mới | Phải cập nhật MỌI vtable (expression problem) |
| Bộ nhớ | Một vtable mỗi kiểu (chia sẻ giữa mọi instance) |

**Thử ngay** — gọi method trên object và xem dispatch vtable phân giải triển khai:

<VTableViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| Nhân Linux | [fs.h#L2093-L2163](https://github.com/torvalds/linux/blob/acb7500801e98639f6d8c2d796ed9f64cba83d3a/include/linux/fs.h#L2093-L2163) | Struct `file_operations` (L2093) là vtable con trỏ hàm: `.read`, `.write`, `.open`, `.release`, `.mmap`, `.poll`, v.v. Mọi filesystem (ext4, btrfs, tmpfs) cung cấp instance `file_operations` riêng. Lớp VFS dispatch cuộc gọi `read()` / `write()` qua vtable — một API, nhiều triển khai. |
| CPython | [object.h#L250-L340](https://github.com/python/cpython/blob/ff64d8de66ab7f8e56b5d410796a7d76c955280c/Include/cpython/object.h#L250-L340) | `PyTypeObject` (L250) là vtable cho mọi kiểu Python. Chứa con trỏ hàm như `tp_repr`, `tp_hash`, `tp_call`, `tp_getattro`, `tp_richcompare` và bộ protocol (`tp_as_number`, `tp_as_sequence`, `tp_as_mapping`). Mọi object `type` Python trỏ tới vtable `PyTypeObject`. |

## Triển khai

::: code-group

```typescript [TypeScript]
interface ShapeVtable {
  area: (data: number[]) => number;
  perimeter: (data: number[]) => number;
}

interface Shape {
  vtable: ShapeVtable;
  data: number[];
}

const circleVtable: ShapeVtable = {
  area: (d) => Math.PI * d[0] * d[0],
  perimeter: (d) => 2 * Math.PI * d[0],
};

const rectVtable: ShapeVtable = {
  area: (d) => d[0] * d[1],
  perimeter: (d) => 2 * (d[0] + d[1]),
};

function createCircle(r: number): Shape {
  return { vtable: circleVtable, data: [r] };
}

function createRect(w: number, h: number): Shape {
  return { vtable: rectVtable, data: [w, h] };
}

// Dispatch đa hình — hoạt động cho mọi shape
function totalArea(shapes: Shape[]): number {
  return shapes.reduce((sum, s) => sum + s.vtable.area(s.data), 0);
}
```

```rust [Rust]
struct ShapeVtable {
    area: fn(&[f64]) -> f64,
    perimeter: fn(&[f64]) -> f64,
}

struct Shape {
    vtable: &'static ShapeVtable,
    data: Vec<f64>,
}

static CIRCLE_VTABLE: ShapeVtable = ShapeVtable {
    area: |d| std::f64::consts::PI * d[0] * d[0],
    perimeter: |d| 2.0 * std::f64::consts::PI * d[0],
};

static RECT_VTABLE: ShapeVtable = ShapeVtable {
    area: |d| d[0] * d[1],
    perimeter: |d| 2.0 * (d[0] + d[1]),
};

fn create_circle(r: f64) -> Shape {
    Shape { vtable: &CIRCLE_VTABLE, data: vec![r] }
}

fn create_rect(w: f64, h: f64) -> Shape {
    Shape { vtable: &RECT_VTABLE, data: vec![w, h] }
}
```

```go [Go]
type ShapeOps struct {
	Area      func(data []float64) float64
	Perimeter func(data []float64) float64
}

type Shape struct {
	Ops  *ShapeOps
	Data []float64
}

var CircleOps = &ShapeOps{
	Area:      func(d []float64) float64 { return math.Pi * d[0] * d[0] },
	Perimeter: func(d []float64) float64 { return 2 * math.Pi * d[0] },
}

var RectOps = &ShapeOps{
	Area:      func(d []float64) float64 { return d[0] * d[1] },
	Perimeter: func(d []float64) float64 { return 2 * (d[0] + d[1]) },
}

func NewCircle(r float64) Shape { return Shape{Ops: CircleOps, Data: []float64{r}} }
func NewRect(w, h float64) Shape { return Shape{Ops: RectOps, Data: []float64{w, h}} }
```

```python [Python]
from dataclasses import dataclass
from typing import Callable

@dataclass
class ShapeVtable:
    area: Callable[[list[float]], float]
    perimeter: Callable[[list[float]], float]

@dataclass
class Shape:
    vtable: ShapeVtable
    data: list[float]

import math

circle_vtable = ShapeVtable(
    area=lambda d: math.pi * d[0] ** 2,
    perimeter=lambda d: 2 * math.pi * d[0],
)

rect_vtable = ShapeVtable(
    area=lambda d: d[0] * d[1],
    perimeter=lambda d: 2 * (d[0] + d[1]),
)

def create_circle(r: float) -> Shape:
    return Shape(vtable=circle_vtable, data=[r])

def create_rect(w: float, h: float) -> Shape:
    return Shape(vtable=rect_vtable, data=[w, h])
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai dispatch vtable cho shape (area/perimeter) | `exercises/typescript/vtable/01-basic.test.ts` |
| Trung bình | Hệ plugin với điểm mở rộng nền vtable | `exercises/typescript/vtable/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/vtable/mod.rs` · Go `exercises/go/vtable/vtable_test.go` · Python `exercises/python/vtable/test_vtable.py`

## Khi nào nên dùng

- **Kiến trúc plugin** — plugin cung cấp vtable callback mà host gọi
- **Trừu tượng kernel OS** — filesystem, device driver, network protocol đều dùng struct ops
- **Runtime ngôn ngữ** — type Python, class Ruby, metatable Lua đều là vtable
- **Storage engine database** — mỗi engine (InnoDB, RocksDB) cung cấp ops read/write/scan
- **Backend render** — OpenGL, Vulkan, Metal đằng sau interface vtable chung

## Khi nào KHÔNG nên dùng

- **Một triển khai duy nhất** — nếu chỉ có một triển khai, gọi hàm trực tiếp đơn giản và nhanh hơn
- **Vòng lặp nội nóng** — gián tiếp vtable cản trở inline và dự đoán nhánh; cân nhắc monomorphization
- **Ít thao tác, nhiều kiểu** — nếu chủ yếu thêm thao tác (không phải kiểu), expression problem làm vtable đau

## Thêm các ứng dụng production

- [Rust dyn Trait](https://github.com/rust-lang/rust) — trait object dùng con trỏ vtable cho dispatch động
- [Go interface](https://github.com/golang/go) — giá trị interface chứa con trỏ itable (interface table)
- [SQLite VFS](https://github.com/sqlite/sqlite) — lớp Virtual File System dùng struct con trỏ hàm cho trừu tượng OS
- [QEMU](https://github.com/qemu/qemu) — model thiết bị cung cấp struct ops cho handler I/O memory-mapped

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Tagged Union](/patterns/tagged-union/) | Cả hai cho đa hình — vtable qua gián tiếp, tagged union qua switch |
| [Visitor](/patterns/visitor/) | Visitor dispatch theo kiểu, thường qua tra cứu con trỏ hàm kiểu vtable |
| [Middleware](/patterns/middleware-chain/) | Mỗi handler middleware là con trỏ hàm, tạo vtable động |

## Câu hỏi thử thách

::: details Câu 1: Trong C++, mọi class có virtual method có vptr ẩn. Chi phí bộ nhớ cho 1 triệu object là gì?
**Trả lời:** Mỗi object lưu một vptr (8 byte trên hệ thống 64-bit). Cho 1 triệu object: 8MB chỉ riêng con trỏ vtable.

Nhưng vtable tự nó được chia sẻ — một cho mỗi class, không phải mỗi instance. Nếu bạn có 10 class, đó chỉ là 10 vtable (tổng vài trăm byte). Chi phí mỗi object là vptr, không phải vtable.

Insight then chốt: vtable per-type, vptr per-instance. Độ sâu kế thừa không đổi kích thước vptr — mỗi object có chính xác một vptr.
:::

::: details Câu 2: Linux có ~70 con trỏ hàm trong file_operations. Chuyện gì khi filesystem không hỗ trợ một thao tác?
**Trả lời:** Con trỏ hàm được set NULL, và lớp VFS kiểm tra NULL trước khi gọi. Nếu NULL, trả `-EINVAL` hoặc `-EOPNOTSUPP`.

Ví dụ, `tmpfs` không hỗ trợ `llseek` trên một số file, nên `file_operations` của nó có `.llseek = NULL`. VFS kiểm tra điều này trong `vfs_llseek()` và trả lỗi. Đây là pattern "vtable một phần" — không phải mọi kiểu cần mọi thao tác.
:::

::: details Câu 3: Rust có cả static dispatch (generic) và dynamic dispatch (dyn Trait). Khi nào chọn dynamic?
**Trả lời:** Dynamic dispatch (`dyn Trait`) khi cần collection không đồng nhất — ví dụ `Vec<Box<dyn Shape>>` chứa circle và rectangle cùng nhau. Static dispatch (generic) khi kiểu biết lúc compile và bạn muốn compiler inline và tối ưu.

Dynamic dispatch tốn ~2-5ns mỗi gọi (gián tiếp con trỏ + nguy cơ cache miss). Static dispatch không tốn nhưng tăng kích thước binary qua monomorphization. Quy tắc thump: hot path dùng generic, cold path và API dùng `dyn Trait`.
:::

::: details Câu 4: PyTypeObject của CPython khác vtable C++ thế nào?
**Trả lời:** Vtable C++ được compiler sinh và ẩn — bạn không thể sửa lúc runtime. `PyTypeObject` của CPython là struct C bình thường mutable hoàn toàn lúc runtime.

Điều này cho phép bản chất động của Python: bạn có thể thêm/thay method trên kiểu lúc runtime bằng cách sửa slot của `PyTypeObject`. Cũng hỗ trợ kế thừa bằng cách copy slot cha và cho phép ghi đè. Đánh đổi: mỗi gọi method qua tra dict + slot kiểu, làm dispatch method Python chậm ~100x so với gọi virtual C++.
:::
