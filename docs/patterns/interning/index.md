---
title: "Pattern: Interning / Symbol Table"
description: "Khử trùng lặp các giá trị bất biến qua một bảng tra cứu chính tắc — so sánh bằng O(1) qua con trỏ thay vì O(n) qua nội dung."
difficulty: "intermediate"
---

# Pattern: Interning / Symbol Table

<DifficultyBadge />

## Mô tả một câu

Khử trùng lặp các giá trị bất biến qua một bảng tra cứu chính tắc — so sánh bằng O(1) qua con trỏ thay vì O(n) qua nội dung.

<DemoBadge />

## Tương tự thực tế

Một bưu điện lưu một bản sao mỗi mã ZIP và cho mọi người tham chiếu đến nó. Thay vì mỗi lá thư mang theo bản '94105' riêng, tất cả đều trỏ tới cùng một entry chung.

## Ý tưởng cốt lõi

Interning lưu mỗi giá trị duy nhất chính xác một lần trong một bảng và phát ra các định danh nhẹ (symbol, ID hoặc con trỏ đã intern) trỏ tới bản chính tắc. Hai giá trị có cấu trúc bằng nhau nhận cùng định danh, nên kiểm tra bằng trở thành so sánh con trỏ/số nguyên O(1) thay vì so nội dung O(n). Đây là đánh đổi chi phí khử trùng lặp ban đầu để tiết kiệm khổng lồ trên các phép so bằng lặp lại.

```text
  intern("hello") → 0     intern("world") → 1     intern("hello") → 0
                                                     (tái dùng!)

  ┌───────────────────────┐
  │    Bảng Symbol        │
  ├────┬──────────────────┤
  │ ID │  Giá trị         │
  ├────┼──────────────────┤
  │  0 │  "hello"         │
  │  1 │  "world"         │
  │  2 │  "foo"           │
  └────┴──────────────────┘

  Bằng nhau: symbol_a == symbol_b  (so số nguyên, O(1))
  Thay vì: strcmp(str_a, str_b) (quét ký tự, O(n))
```

| Thuộc tính | Giá trị |
|----------|-------|
| intern() | O(n) lần đầu (hash + lưu), O(1) phân bổ khi hit |
| Bằng nhau | O(1) — so số nguyên/con trỏ |
| Bộ nhớ | Đã khử trùng lặp — mỗi giá trị duy nhất lưu một lần |
| Đánh đổi | Bảng intern tăng đơn điệu (giá trị không bao giờ giải phóng) |

**Thử ngay** — intern chuỗi và xem cách các bản trùng phân giải về cùng ID:

<InterningViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| Rust Compiler (rustc) | [symbol.rs#L24-L79](https://github.com/rust-lang/rust/blob/ab26b175979ee7b2cb3302dce204b99df96f7efb/compiler/rustc_span/src/symbol.rs#L24-L79) | `Symbol` (L24) là newtype quanh `u32` — index vào bảng intern toàn cục. `Interner` (L56-L79) lưu chuỗi trong `Vec` và khử trùng lặp qua `HashMap`. Mọi identifier trong compiler Rust đều là `Symbol` — bằng nhau là một phép so `u32` duy nhất. |
| CPython | [unicodeobject.c#L14416-L14472](https://github.com/python/cpython/blob/ff64d8de66ab7f8e56b5d410796a7d76c955280c/Objects/unicodeobject.c#L14416-L14472) | `PyUnicode_InternInPlace` (L14416) intern các chuỗi Python bằng cách lưu vào dict toàn cục. Nếu chuỗi đã tồn tại, object đã tồn tại được trả về và refcount của cái mới giảm. Mọi chuỗi identifier (tên biến, tên thuộc tính) đều được intern tự động cho tra cứu dict O(1). |

## Triển khai

::: code-group

```typescript [TypeScript]
class StringInterner {
  private strToId = new Map<string, number>();
  private idToStr: string[] = [];

  intern(s: string): number {
    const existing = this.strToId.get(s);
    if (existing !== undefined) return existing;
    const id = this.idToStr.length;
    this.strToId.set(s, id);
    this.idToStr.push(s);
    return id;
  }

  resolve(id: number): string | undefined {
    return this.idToStr[id];
  }

  get size(): number {
    return this.idToStr.length;
  }
}
```

```rust [Rust]
use std::collections::HashMap;

pub struct Interner {
    str_to_id: HashMap<String, u32>,
    id_to_str: Vec<String>,
}

impl Interner {
    pub fn new() -> Self {
        Interner { str_to_id: HashMap::new(), id_to_str: Vec::new() }
    }

    pub fn intern(&mut self, s: &str) -> u32 {
        if let Some(&id) = self.str_to_id.get(s) {
            return id;
        }
        let id = self.id_to_str.len() as u32;
        self.str_to_id.insert(s.to_string(), id);
        self.id_to_str.push(s.to_string());
        id
    }

    pub fn resolve(&self, id: u32) -> Option<&str> {
        self.id_to_str.get(id as usize).map(|s| s.as_str())
    }
}
```

```go [Go]
type Interner struct {
	strToID map[string]int
	idToStr []string
}

func NewInterner() *Interner {
	return &Interner{strToID: make(map[string]int)}
}

func (it *Interner) Intern(s string) int {
	if id, ok := it.strToID[s]; ok {
		return id
	}
	id := len(it.idToStr)
	it.strToID[s] = id
	it.idToStr = append(it.idToStr, s)
	return id
}

func (it *Interner) Resolve(id int) (string, bool) {
	if id < 0 || id >= len(it.idToStr) {
		return "", false
	}
	return it.idToStr[id], true
}
```

```python [Python]
class StringInterner:
    def __init__(self):
        self._str_to_id: dict[str, int] = {}
        self._id_to_str: list[str] = []

    def intern(self, s: str) -> int:
        if s in self._str_to_id:
            return self._str_to_id[s]
        sym_id = len(self._id_to_str)
        self._str_to_id[s] = sym_id
        self._id_to_str.append(s)
        return sym_id

    def resolve(self, sym_id: int) -> str | None:
        if 0 <= sym_id < len(self._id_to_str):
            return self._id_to_str[sym_id]
        return None
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai string interner với intern/resolve | `exercises/typescript/interning/01-basic.test.ts` |
| Trung bình | Type interner với bằng nhau theo cấu trúc | `exercises/typescript/interning/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/interning/mod.rs` · Go `exercises/go/interning/interning_test.go` · Python `exercises/python/interning/test_interning.py`

## Khi nào nên dùng

- **Compiler và interpreter** — intern identifier, keyword, type descriptor cho so bằng nhanh
- **Engine truy vấn database** — intern tên cột, tên bảng cho so sánh nhanh khi lên kế hoạch truy vấn
- **Serialize** — intern tên trường lặp lại trong JSON/XML để giảm bộ nhớ
- **Game engine** — intern tên asset, ID material, trạng thái animation
- **Tải nặng chuỗi** — mọi hệ thống so sánh cùng chuỗi hàng triệu lần

## Khi nào KHÔNG nên dùng

- **Chuỗi sống ngắn** — nếu chuỗi được tạo và bỏ nhanh, overhead intern lớn hơn lợi ích
- **Phần lớn chuỗi là duy nhất** — nếu ít chuỗi lặp, bảng intern lãng phí bộ nhớ mà không tiết kiệm so sánh
- **Eo hẹp bộ nhớ không dọn** — bảng intern cổ điển tăng đơn điệu; cân nhắc weak reference nếu cần dọn

## Thêm các ứng dụng production

- [Java String.intern()](https://github.com/openjdk/jdk) — interning chuỗi cấp JVM trong string pool
- [V8 Internalized Strings](https://chromium.googlesource.com/v8/v8/+/refs/heads/main/src/objects/string.h) — V8 intern chuỗi dùng làm tên thuộc tính để tra thuộc tính O(1)
- [Ruby Symbol](https://github.com/ruby/ruby) — `Symbol` là chuỗi đã intern không bao giờ bị GC
- [LLVM StringPool](https://github.com/llvm/llvm-project) — chuỗi đã intern cho identifier qua pipeline compiler

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Flyweight](/patterns/flyweight/) | Interning là cơ chế đằng sau flyweight — khử trùng lặp các giá trị bất biến giống nhau |
| [LRU Cache](/patterns/lru-cache/) | Bảng intern có thể dùng loại bỏ LRU để giới hạn bộ nhớ |
| [Bloom Filter](/patterns/bloom-filter/) | Bloom filter có thể kiểm tra trước trước khi tra bảng intern tốn kém |

## Câu hỏi thử thách

::: details Câu 1: Compiler của bạn intern 100.000 identifier. Interning ảnh hưởng bộ nhớ thế nào so với lưu chuỗi thô?
**Trả lời:** Mỗi chuỗi duy nhất được lưu đúng một lần trong bảng intern. Mỗi tham chiếu là một `u32` (4 byte) thay vì con trỏ + độ dài + cấp phát heap (thường 24+ byte mỗi chuỗi trên hệ thống 64-bit).

Nếu identifier trung bình 12 ký tự với hệ số trùng lặp 5x, lưu thô tốn 100.000 * (24 + 12) = 3,6MB. Với interning, bạn lưu 20.000 chuỗi duy nhất (720KB) + 100.000 ID 4 byte mỗi cái (400KB) = 1,12MB. Đó là ít hơn ~3x bộ nhớ, cộng với so bằng O(1).
:::

::: details Câu 2: Symbol Ruby được intern và không bao giờ bị GC. Rủi ro bảo mật là gì?
**Trả lời:** Kẻ tấn công có thể vắt kiệt bộ nhớ server bằng cách tạo vô số symbol duy nhất (ví dụ chuyển input người dùng thành symbol qua `to_sym`). Vì symbol không bao giờ bị GC, mỗi input duy nhất tiêu thụ bộ nhớ vĩnh viễn.

Vắt kiệt bảng symbol là một vector tấn công đã biết trong Ruby (lỗ hổng liên quan gồm CVE-2013-0269 trong gem JSON). Cách sửa: không bao giờ intern input do người dùng kiểm soát. Dùng string cho dữ liệu bên ngoài, symbol chỉ cho hằng đã biết. Ruby 2.2+ giới thiệu "mortal symbol" — symbol tạo động (kể cả qua `to_sym`) giờ có thể bị GC. Chỉ symbol xuất hiện literal trong source code mới bất tử.
:::

::: details Câu 3: Tại sao compiler Rust dùng u32 cho Symbol thay vì u64 hoặc usize?
**Trả lời:** Một `u32` giới hạn compiler ở ~4 tỉ symbol duy nhất, đủ dư cho mọi chương trình thực. Lợi ích là mỗi `Symbol` chỉ 4 byte — một nửa kích thước `u64` trên hệ thống 64-bit.

Vì symbol xuất hiện khắp các cấu trúc dữ liệu của compiler (node AST, type, scope), giảm một nửa kích thước cho cải thiện hiệu suất cache rõ rệt. Đây là đánh đổi không gian-thời gian có chủ ý: hiệu năng compiler bị giới hạn bởi bộ nhớ, nên dữ liệu nhỏ hơn = ít cache miss hơn.
:::

::: details Câu 4: Ứng dụng đa luồng của bạn dùng một interner chuỗi toàn cục được bảo vệ bởi mutex. Profiling cho thấy khoá intern là điểm tranh chấp hàng đầu. Làm sao giảm tranh chấp mà không bỏ interning?
**Trả lời:** Dùng interner mỗi luồng (thread-local) cho hot path, và chỉ merge vào bảng toàn cục khi cần so sánh xuyên luồng.

Một interner toàn cục duy nhất trở thành điểm nghẽn serialize khi nhiều thread intern đồng thời. Giải pháp là interning chia mảnh hoặc thread-local: mỗi thread duy trì interner riêng để intern nhanh, lock-free. Symbol từ các interner thread-local khác nhau không so sánh trực tiếp được, nên so xuyên luồng cần bước merge hoặc lược đồ hai cấp (ID local + ID thread). Compiler Rust dùng interner theo phạm vi mỗi session, và một số JVM dùng concurrent hash map với khoá phân vạch để giảm tranh chấp. Insight chính là phần lớn so bằng đều thread-local (trong một đơn vị biên dịch hoặc truy vấn), nên phải trả tiền đồng bộ toàn cục cho mỗi lần intern là lãng phí.
:::
