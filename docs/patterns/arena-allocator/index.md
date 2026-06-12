---
title: "Pattern: Arena Allocator"
description: "Cấp phát object bằng cách bump con trỏ trong một vùng cấp phát trước — giải phóng tất cả một lần khi vùng không còn cần."
difficulty: "intermediate"
---

# Pattern: Arena Allocator

<DifficultyBadge />

## Mô tả một câu

Cấp phát object bằng cách bump con trỏ trong một vùng cấp phát trước — giải phóng tất cả một lần khi vùng không còn cần.

<DemoBadge />

## Tương tự thực tế

Một bảng trắng cho cuộc họp. Mọi người viết ở bất cứ chỗ nào còn trống, kéo bút lên trước. Khi cuộc họp kết thúc, bạn xoá cả bảng cùng lúc — không cần lau từng dòng riêng.

## Ý tưởng cốt lõi

Arena (hay bump allocator) cấp phát trước một khối bộ nhớ liền kề và phát các đoạn ra bằng cách tiến con trỏ. Không thể giải phóng từng cấp phát riêng — toàn bộ arena được giải phóng cùng một lúc. Điều đó loại bỏ overhead cấp phát mỗi object, phân mảnh và áp lực GC.

```text
  Arena: [                 capacity                    ]
         ┌──────┬──────┬──────┬────────────────────────┐
         │ obj1 │ obj2 │ obj3 │    không gian trống    │
         └──────┴──────┴──────┴────────────────────────┘
                              ▲
                              └── offset (bump pointer)

  alloc(16) → offset: 0→16   (trả vùng 0..16)
  alloc(8)  → offset: 16→24  (trả vùng 16..24)
  reset()   → offset: 0      (mọi object được giải phóng tức thì)
```

| Thuộc tính | Giá trị |
|----------|-------|
| Tốc độ cấp phát | O(1) — chỉ bump một con trỏ |
| Giải phóng | O(1) — reset con trỏ (giải phóng tất cả) |
| Giải phóng riêng | **Không hỗ trợ** (dùng free-list hoặc GC cho việc đó) |
| Phân mảnh | **Không** — cấp phát liền kề, không khe |

**Thử ngay** — cấp phát các block trong arena và reset để giải phóng tất cả một lần:

<ArenaAllocatorViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| Rust bumpalo | [lib.rs#L378-L383](https://github.com/fitzgen/bumpalo/blob/d2cc4dd0b8830d5b05d44e9decc776823e6a70ea/src/lib.rs#L378-L383) | Struct `Bump` (L378) giữ bump pointer vào chunk hiện tại. `try_alloc_layout_fast` (L1330-L1422) là hot path: đọc con trỏ, align, trừ size, kiểm tra capacity. `reset` (L1059-L1099) giải phóng hàng loạt mọi chunk. Dùng trong `wasm-bindgen`, compiler Rust và Deno. |
| Stdlib Go | [arena.go#L44-L67](https://github.com/golang/go/blob/f5cdf4745455415c7a43cfc7d925214d4511489b/src/arena/arena.go#L44-L67) | Kiểu `Arena` thử nghiệm — `New[T]()` cấp phát từ arena, `Free()` giải phóng tất cả một lúc, bỏ qua GC. API tối giản bọc primitive arena của runtime. |

## Triển khai

::: code-group

```typescript [TypeScript]
class Arena {
  private buffer: ArrayBuffer;
  private view: DataView;
  private offset = 0;

  constructor(capacity: number) {
    this.buffer = new ArrayBuffer(capacity);
    this.view = new DataView(this.buffer);
  }

  alloc(size: number): { start: number; size: number } | null {
    if (this.offset + size > this.buffer.byteLength) return null;
    const start = this.offset;
    this.offset += size;
    return { start, size };
  }

  writeU32(offset: number, value: number): void {
    this.view.setUint32(offset, value);
  }

  readU32(offset: number): number {
    return this.view.getUint32(offset);
  }

  reset(): void { this.offset = 0; }

  get used(): number { return this.offset; }
  get capacity(): number { return this.buffer.byteLength; }
}
```

```rust [Rust]
pub struct Arena {
    buf: Vec<u8>,
    offset: usize,
}

impl Arena {
    pub fn new(capacity: usize) -> Self {
        Arena { buf: vec![0; capacity], offset: 0 }
    }

    pub fn alloc(&mut self, size: usize) -> Option<&mut [u8]> {
        if self.offset + size > self.buf.len() { return None; }
        let start = self.offset;
        self.offset += size;
        Some(&mut self.buf[start..start + size])
    }

    pub fn reset(&mut self) { self.offset = 0; }

    pub fn used(&self) -> usize { self.offset }
}
```

```go [Go]
type Arena struct {
	buf    []byte
	offset int
}

func NewArena(capacity int) *Arena {
	return &Arena{buf: make([]byte, capacity)}
}

func (a *Arena) Alloc(size int) []byte {
	if a.offset+size > len(a.buf) {
		return nil
	}
	start := a.offset
	a.offset += size
	return a.buf[start : start+size]
}

func (a *Arena) Reset() { a.offset = 0 }

func (a *Arena) Used() int { return a.offset }
```

```python [Python]
class Arena:
    def __init__(self, capacity: int):
        self.buf = bytearray(capacity)
        self.offset = 0

    def alloc(self, size: int) -> memoryview | None:
        if self.offset + size > len(self.buf):
            return None
        start = self.offset
        self.offset += size
        return memoryview(self.buf)[start:start + size]

    def reset(self) -> None:
        self.offset = 0

    @property
    def used(self) -> int:
        return self.offset
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai bump allocator với alloc/reset | `exercises/typescript/arena-allocator/01-basic.test.ts` |
| Trung bình | Arena chuỗi với cấp phát dựa trên handle | `exercises/typescript/arena-allocator/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/arena_allocator/mod.rs` · Go `exercises/go/arena_allocator/arena_allocator_test.go` · Python `exercises/python/arena_allocator/test_arena_allocator.py`

## Khi nào nên dùng

- **Compiler/parser** — node AST được cấp phát khi parse, giải phóng tất cả sau biên dịch
- **Dữ liệu frame của game** — cấp phát theo từng frame, reset ở ranh giới frame
- **Dữ liệu theo phạm vi request** — cấp phát của web server gắn với vòng đời một request
- **Serialize** — buffer tạm cho encode/decode

## Khi nào KHÔNG nên dùng

- **Object sống lâu** — arena giải phóng tất cả một lúc; không thể giải phóng object riêng
- **Vòng đời khác nhau** — nếu object có vòng đời khác nhau, dùng allocator tổng quát
- **Eo hẹp bộ nhớ** — arena có thể lãng phí nếu kích thước cấp phát khó dự đoán
- **Arena chia sẻ giữa thread** — không có đồng bộ, arena không thread-safe (dùng arena thread-local)

## Thêm các ứng dụng production

- [Go arena](https://github.com/golang/go/blob/f5cdf4745455415c7a43cfc7d925214d4511489b/src/arena/arena.go) — API arena thử nghiệm trong thư viện chuẩn Go
- [V8 Engine](https://chromium.googlesource.com/v8/v8/+/refs/heads/main/src/zone/zone.h) — allocator `Zone` cung cấp cấp phát kiểu arena cho biến tạm của compiler
- [Zig](https://github.com/ziglang/zig) — `std.mem.ArenaAllocator` như một pattern allocator cốt lõi
- [Game engine ECS](https://github.com/SanderMertens/flecs) — lưu trữ component với cấp phát kiểu arena

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Free List](/patterns/free-list/) | Free list tái chế object riêng; arena giải phóng hàng loạt |
| [Object Pool](/patterns/object-pool/) | Object pool cấp phát trước; arena bump cấp phát — cả hai giảm overhead malloc |
| [Reference Counting](/patterns/reference-counting/) | Arena tránh reference counting mỗi object bằng cách giải phóng tất cả khi phạm vi kết thúc |

## Câu hỏi thử thách

::: details Câu 1: Arena allocator không bao giờ phân mảnh bộ nhớ. Allocator tổng quát thì có. Tại sao?
**Trả lời:** Vì arena cấp phát liền kề bằng cách bump con trỏ tiến lên và giải phóng tất cả một lúc — không bao giờ có khe giữa các object sống.

Phân mảnh xảy ra khi object được cấp phát và giải phóng riêng, để lại lỗ giữa các object sống quá nhỏ để tái dùng. Arena tránh được điều đó vì không bao giờ giải phóng object riêng — chỉ reset con trỏ về 0, thu hồi tất cả một lần. Đánh đổi là không thể giải phóng một object đơn lẻ sớm; nếu một cấp phát trong arena vẫn cần, toàn bộ arena phải sống tiếp.
:::

::: details Câu 2: Bạn dùng arena cho các cấp phát mỗi HTTP request. Một request kích hoạt upload file 50MB được parse vào arena. Vấn đề là gì?
**Trả lời:** Arena giữ toàn bộ 50MB cho đến khi request hoàn tất, ngay cả khi dữ liệu đã parse được tiêu thụ dần và lẽ ra có thể giải phóng dọc đường.

Arena hoạt động tốt nhất khi mọi cấp phát có vòng đời gần như nhau. Nếu bạn parse file lớn vào arena nhưng chỉ cần một tóm tắt nhỏ, phần lớn dữ liệu nằm trong bộ nhớ tới khi `reset()`. Cách sửa: hoặc stream-process file mà không nạp tất cả vào arena, hoặc dùng arena ngắn riêng cho pass parse và copy chỉ tóm tắt sang arena request.
:::

::: details Câu 3: Một đồng nghiệp đề nghị thay garbage collector của Go bằng arena ở khắp nơi cho hiệu năng tốt hơn. Lỗ hổng trong lập luận này là gì?
**Trả lời:** Arena đòi hỏi mọi object bên trong nó chia sẻ cùng vòng đời. Chương trình thật có object với vòng đời rất khác nhau, mà arena không xử lý được.

Nếu object A phải sống lâu hơn object B nhưng chúng cùng arena, bạn không thể giải phóng B mà không giải phóng A. Bạn sẽ hoặc rò bộ nhớ (giữ arena sống quá lâu) hoặc tạo hàng chục micro-arena để khớp các vòng đời khác nhau — đó là tự phát minh lại allocator với độ phức tạp cao hơn. GC tự xử lý vòng đời tuỳ ý. Arena vượt trội trong phạm vi cụ thể (mỗi request, mỗi frame, mỗi pass biên dịch) nơi vòng đời đồng nhất.
:::

::: details Câu 4: Có hai arena: một cho node AST khi parse, một cho node IR khi sinh mã. Pass IR cần tham chiếu các node AST. Nguy hiểm là gì?
**Trả lời:** Nếu arena AST bị reset trước khi pass IR hoàn tất đọc từ nó, IR sẽ giữ tham chiếu lủng lẳng vào bộ nhớ đã giải phóng.

Đây là bài toán phạm vi vòng đời: object của arena B tham chiếu object của arena A, tạo phụ thuộc vòng đời ngầm. Arena A không được reset cho đến khi arena B xong. Trong Rust, borrow checker thực thi điều này tĩnh. Trong C/Go/TypeScript, đây là vấn đề kỷ luật. Giải pháp: hoặc copy dữ liệu cần thiết ra khỏi arena A trước khi reset, hoặc thực thi thứ tự nghiêm ngặt: reset A chỉ sau khi reset B.
:::
