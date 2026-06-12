---
title: "Pattern: Tagged Union / Variant"
description: "Lưu tag kiểu cùng union giá trị để một biến giữ an toàn nhiều kiểu khác nhau, dispatch hành vi qua tag."
difficulty: "beginner"
---

# Pattern: Tagged Union / Variant

<DifficultyBadge />

## Mô tả một câu

Lưu tag kiểu cùng union giá trị để một biến giữ an toàn nhiều kiểu khác nhau, dispatch hành vi qua tag.

<DemoBadge />

## Tương tự thực tế

Nhãn vận chuyển trên kiện hàng. Nhãn ghi 'dễ vỡ', 'mau hỏng' hoặc 'tiêu chuẩn', và kho xử lý mỗi loại khác nhau. Nhãn (tag) quyết định quy trình xử lý (dispatch) — một hệ thống, nhiều hành vi.

## Ý tưởng cốt lõi

Tagged union (còn gọi variant, discriminated union hoặc sum type) ghép cặp một tag phân biệt kiểu với payload giá trị. Lúc runtime, code kiểm tra tag để xác định kiểu thực tế của giá trị, rồi dispatch tới handler đúng. Đây là nền tảng thủ công đằng sau discriminated union của TypeScript, enum Rust và algebraic data type.

```text
  TaggedValue
  ┌────────┬───────────────────┐
  │  tag   │      value        │
  ├────────┼───────────────────┤
  │ NUMBER │  42               │
  │ STRING │  "hello"          │
  │ ARRAY  │  [val, val, ...]  │
  │ OBJECT │  {key: val, ...}  │
  └────────┴───────────────────┘

  Dispatch:
  switch (v.tag) {
    NUMBER → xử lý như number
    STRING → xử lý như string
    ARRAY  → đệ quy vào children
    OBJECT → lặp cặp key-value
  }
```

| Thuộc tính | Giá trị |
|----------|-------|
| Bộ nhớ | Kích thước tag + kích thước variant lớn nhất |
| An toàn kiểu | Switch đầy đủ đảm bảo mọi trường hợp được xử lý |
| Mở rộng | Thêm tag mới + handler (mở để mở rộng) |
| Zero-cost? | Trong C/Rust: có (tag enum + union). Trong JS/Python: overhead object |

**Thử ngay** — chuyển giữa các kiểu variant và xem dispatch theo tag hoạt động:

<TaggedUnionViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| Godot Engine | [variant.h#L78-L120](https://github.com/godotengine/godot/blob/ec67cbe92628bdaf979b10594359ba6f02cf8838/core/variant/variant.h#L78-L120) | Enum `Variant::Type` (L78-L108) liệt kê 38 kiểu (NIL, BOOL, INT, FLOAT, STRING, VECTOR2, ...). Class `Variant` lưu tag `Type` và union mọi giá trị khả dĩ. Mọi giá trị GDScript là một `Variant` — engine dispatch thao tác qua tag. |
| PyTorch | [ivalue.h#L51-L96](https://github.com/pytorch/pytorch/blob/cef26d1e97fcb9dd61b4471f9bd7fa9a32bd42b9/aten/src/ATen/core/ivalue.h#L51-L96) | `IValue` (Interpreter Value) giữ tag (enum `Tag`: Tensor, Int, Double, Bool, String, List, Dict, v.v.) và union `Payload`. Interpreter TorchScript dùng dispatch theo tag cho mọi thao tác trên giá trị không đồng nhất. |

## Triển khai

::: code-group

```typescript [TypeScript]
type Tag = 'null' | 'boolean' | 'number' | 'string' | 'array' | 'object';

interface TaggedValue {
  tag: Tag;
  value: null | boolean | number | string | TaggedValue[] | Record<string, TaggedValue>;
}

function stringify(tv: TaggedValue): string {
  switch (tv.tag) {
    case 'null': return 'null';
    case 'boolean': return String(tv.value);
    case 'number': return String(tv.value);
    case 'string': return `"${tv.value}"`;
    case 'array': {
      const items = (tv.value as TaggedValue[]).map(stringify);
      return `[${items.join(',')}]`;
    }
    case 'object': {
      const obj = tv.value as Record<string, TaggedValue>;
      const pairs = Object.keys(obj).map(k => `"${k}":${stringify(obj[k])}`);
      return `{${pairs.join(',')}}`;
    }
  }
}
```

```rust [Rust]
enum Value {
    Null,
    Bool(bool),
    Number(f64),
    Str(String),
}

impl Value {
    fn display(&self) -> String {
        match self {
            Value::Null => "null".to_string(),
            Value::Bool(b) => b.to_string(),
            Value::Number(n) => n.to_string(),
            Value::Str(s) => format!("\"{}\"", s),
        }
    }

    fn try_add(&self, other: &Value) -> Option<Value> {
        match (self, other) {
            (Value::Number(a), Value::Number(b)) => Some(Value::Number(a + b)),
            _ => None,
        }
    }
}
```

```go [Go]
type Tag int

const (
	TagNull Tag = iota
	TagBool
	TagNumber
	TagString
)

type TaggedValue struct {
	Tag    Tag
	Bool   bool
	Number float64
	Str    string
}

func Display(tv TaggedValue) string {
	switch tv.Tag {
	case TagNull:
		return "null"
	case TagBool:
		if tv.Bool {
			return "true"
		}
		return "false"
	case TagNumber:
		return fmt.Sprintf("%g", tv.Number)
	case TagString:
		return fmt.Sprintf("%q", tv.Str)
	default:
		return "unknown"
	}
}
```

```python [Python]
from dataclasses import dataclass
from typing import Union

@dataclass
class TaggedValue:
    tag: str  # "null", "bool", "number", "string"
    value: Union[None, bool, int, float, str]

def display(tv: TaggedValue) -> str:
    if tv.tag == "null":
        return "null"
    elif tv.tag == "bool":
        return str(tv.value).lower()
    elif tv.tag == "number":
        return str(tv.value)
    elif tv.tag == "string":
        return f'"{tv.value}"'
    raise ValueError(f"Unknown tag: {tv.tag}")

def try_add(a: TaggedValue, b: TaggedValue) -> TaggedValue | None:
    if a.tag != "number" or b.tag != "number":
        return None
    return TaggedValue("number", a.value + b.value)
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai giá trị có tag với dispatch theo kiểu | `exercises/typescript/tagged-union/01-basic.test.ts` |
| Trung bình | Kiểu giá trị giống JSON với mảng/object lồng | `exercises/typescript/tagged-union/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/tagged_union/mod.rs` · Go `exercises/go/tagged_union/tagged_union_test.go` · Python `exercises/python/tagged_union/test_tagged_union.py`

## Khi nào nên dùng

- **Giá trị scripting language** — một kiểu Value duy nhất giữ số, chuỗi, mảng, v.v. (Variant Godot, TValue Lua)
- **Định dạng serialize** — JSON, MessagePack, oneof field Protocol Buffers
- **IR compiler** — node AST, toán hạng lệnh, giá trị interpreter
- **Hệ thống cấu hình** — setting có thể là chuỗi, số, boolean hoặc list
- **Driver database** — giá trị cột với nhiều kiểu SQL trong một interface

## Khi nào KHÔNG nên dùng

- **Collection đồng nhất** — nếu mọi thứ cùng kiểu, mảng thường đơn giản hơn
- **Vòng lặp nội then chốt cho hiệu năng** — dispatch tag có overhead branch; dùng kiểu cụ thể khi kiểu biết tĩnh
- **Phân cấp sâu** — nếu cần 50+ variant với hành vi phức tạp, cân nhắc phân cấp class hoặc trait object

## Thêm các ứng dụng production

- [V8 Engine](https://github.com/v8/v8/blob/02a623d69f6ba69f513ae2c7aef84b9914fbde51/src/objects/tagged-value.h) — giá trị JavaScript dùng con trỏ có tag để phân biệt Smi (số nguyên nhỏ) với object heap
- [SQLite](https://github.com/sqlite/sqlite) — struct `Mem` nội bộ lưu tag kiểu + union giá trị cho mọi kiểu SQL
- [Lua TValue](https://github.com/lua/lua) — mọi giá trị Lua là một `TValue` với tag kiểu và union `Value`
- [GHC Haskell](https://github.com/ghc/ghc) — algebraic data type biên dịch thành object heap có tag

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Vtable](/patterns/vtable/) | Cả hai cho đa hình lúc runtime — tagged union qua switch, vtable qua con trỏ hàm |
| [Bitmask](/patterns/bitmask/) | Bitmask flag có thể đóng vai tag kiểu trong triển khai tagged union nhẹ |
| [Visitor](/patterns/visitor/) | Visitor dispatch theo kiểu node, thường biểu diễn dưới dạng tagged union |

## Câu hỏi thử thách

::: details Câu 1: Bạn có tagged union với 4 kiểu. Giá trị chiếm bao nhiêu byte trong C nếu variant lớn nhất 24 byte?
**Trả lời:** Kích thước union bằng phần tử lớn nhất: 24 byte. Thêm tag (thường 4 byte với padding) và bạn có tổng 28 hoặc 32 byte tuỳ alignment.

Insight then chốt: Trong union, mọi variant chia sẻ cùng bộ nhớ. Compiler cấp phát đủ chỗ cho cái lớn nhất. Tag lưu riêng (không bên trong union), nên tổng size = sizeof(tag) + padding + sizeof(variant_lớn_nhất).
:::

::: details Câu 2: TypeScript có discriminated union sẵn. Sao vẫn triển khai tagged union thủ công?
**Trả lời:** Discriminated union của TypeScript chỉ tồn tại lúc compile — chúng bị xoá thành object JavaScript thường lúc runtime. Nếu bạn cần kiểm tra kiểu lúc runtime (ví dụ deserialize JSON từ API, hoặc hệ plugin nơi kiểu không biết lúc compile), bạn cần trường tag tường minh sống tới runtime.

Cũng vậy, khi lưu giá trị không đồng nhất trong database, định dạng serialize hoặc ranh giới xuyên ngôn ngữ, bạn cần tag vật lý — hệ kiểu TypeScript không giúp ở đó.
:::

::: details Câu 3: Variant của Godot có 38 tag kiểu. Rủi ro khi thêm nhiều tag theo thời gian là gì?
**Trả lời:** Mọi hàm switch theo tag phải xử lý trường hợp mới. Nếu switch nào không đầy đủ, bạn gặp lỗi runtime hoặc bug âm thầm. Đây là "expression problem" — thêm kiểu mới dễ (thêm tag), nhưng phải cập nhật mọi thao tác.

Chiến lược giảm nhẹ: (1) Cảnh báo switch đầy đủ trong compiler, (2) Trường hợp default/fallback, (3) Pattern visitor để tập trung dispatch, (4) `match` của Rust thực thi đầy đủ lúc compile.
:::

::: details Câu 4: Khác biệt giữa tagged union và phân cấp class cho đa hình là gì?
**Trả lời:** Tagged union *đóng* — mọi variant biết trước và dispatch qua switch. Phân cấp class *mở* — bạn có thể thêm subclass không cần sửa code có sẵn, dispatch qua vtable.

Đánh đổi: Tagged union dễ thêm *thao tác* mới (chỉ viết switch mới). Phân cấp class dễ thêm *kiểu* mới (chỉ thêm subclass). Đây là expression problem kinh điển. Tagged union tốt hơn cho thiết kế hướng dữ liệu (serialize, interpreter), trong khi phân cấp class hợp thiết kế hướng hành vi (widget UI, entity game).
:::
