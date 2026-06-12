---
title: "Pattern: Bitmask"
description: "Nhồi nhiều cờ boolean vào một số nguyên và thao tác qua các phép bitwise cho set với thời gian hằng."
difficulty: "beginner"
---

# Pattern: Bitmask

<DifficultyBadge />

## Mô tả một câu

Nhồi nhiều cờ boolean vào một số nguyên và thao tác qua các phép bitwise cho set với thời gian hằng.

<DemoBadge />

## Tương tự thực tế

Một hàng công tắc đèn trên panel tường. Mỗi công tắc bật hoặc tắt. Bạn có thể bật/tắt bất kỳ công tắc nào độc lập, kiểm tra cái nào đang bật qua một cái liếc, và panel chiếm cùng một diện tích tường dù bạn có 8 hay 32 công tắc.

## Ý tưởng cốt lõi

Thay vì dùng mảng boolean hoặc object với nhiều trường, bitmask mã hoá mỗi cờ thành một bit trong một số nguyên. Điều đó cho bạn set/check/clear/toggle O(1) và kết hợp nhiều cờ một cách dễ dàng.

```text
 bit  7     6     5     4     3     2     1     0
    ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
    │     │     │     │ SN  │ CB  │ RF  │ UP  │ PL  │
    └─────┴─────┴─────┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┘
                         │     │     │     │     └── Placement  1 << 0
                         │     │     │     └──────── Update     1 << 1
                         │     │     └────────────── Ref        1 << 2
                         │     └──────────────────── Callback   1 << 3
                         └────────────────────────── Snapshot   1 << 4
```

**Thao tác cốt lõi** — đều O(1), không rẽ nhánh:

| Muốn... | Viết | Vì sao đúng |
|------------|-------|-------------|
| Set một cờ | `flags \|= FLAG` | OR bật bit, các bit khác không đổi |
| Kiểm tra một cờ | `(flags & FLAG) !== 0` | AND cô lập bit — khác 0 = đã set |
| Clear một cờ | `flags &= ~FLAG` | AND với mask đảo tắt bit |
| Toggle một cờ | `flags ^= FLAG` | XOR lật bit |
| Kết hợp cờ | `flags = A \| B \| C` | OR gộp nhiều cờ thành một giá trị |
| Kiểm tra TẤT CẢ mask | `(flags & mask) === mask` | Đúng chỉ khi mọi bit trong mask được set |
| Kiểm tra BẤT KỲ mask | `(flags & mask) !== 0` | Đúng nếu ít nhất một bit trong mask được set |
| Đếm bit set | `n.toString(2).split('1').length - 1` | Population count (popcnt) |

Insight then chốt: một thao tác `&` duy nhất có thể kiểm tra mọi tổ hợp cờ đồng thời — không vòng lặp, không rẽ nhánh.

| Thuộc tính | Giá trị |
|----------|-------|
| Set / check / clear | O(1) — một thao tác bitwise duy nhất, không rẽ nhánh |
| Kết hợp nhiều cờ | O(1) — một `\|` hoặc `&` bất kể số cờ |
| Số cờ tối đa | Độ rộng word — 32 hoặc 64 trên hầu hết nền tảng |
| Bộ nhớ | O(1) — một số nguyên chứa mọi cờ |

**Thử ngay** — toggle các bit phân quyền và xem giá trị mask cập nhật ở dạng nhị phân, thập phân và hex:

<BitmaskViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| React | [ReactFiberFlags.js#L14-L36](https://github.com/facebook/react/blob/34b78a2897cc208260a88e6b62ecaf9ca2a9dfe4/packages/react-reconciler/src/ReactFiberFlags.js#L14-L36) | Flag tác dụng phụ — `Placement = 0b0000010`, `Update = 0b0000100`. Kiểm tra với `fiber.flags & Update`, kết hợp bằng OR bitwise. Một integer thay thế hàng chục boolean cho các effect pending khi reconciliation. |
| Nhân Linux | [stat.h#L25-L33](https://github.com/torvalds/linux/blob/acb7500801e98639f6d8c2d796ed9f64cba83d3a/include/uapi/linux/stat.h#L25-L33) | Bit phân quyền file — `rwxrwxrwx` kinh điển (read/write/execute cho owner/group/other) mã hoá thành mask 9-bit |
| Stdlib Go | [types.go#L32-L46](https://github.com/golang/go/blob/f5cdf4745455415c7a43cfc7d925214d4511489b/src/os/types.go#L32-L46) | `os.FileMode` — bit mode file của Go phản chiếu cờ phân quyền Unix bằng hằng có kiểu với dịch bit iota |

## Triển khai

::: code-group

```typescript [TypeScript]
// Định nghĩa cờ là luỹ thừa của 2
const Flags = {
  Read:    1 << 0,  // 0b0001
  Write:   1 << 1,  // 0b0010
  Execute: 1 << 2,  // 0b0100
  Delete:  1 << 3,  // 0b1000
} as const;

type FlagSet = number;

const hasFlag = (set: FlagSet, flag: number): boolean =>
  (set & flag) === flag;

const hasAny = (set: FlagSet, mask: number): boolean =>
  (set & mask) !== 0;

const setFlag = (set: FlagSet, flag: number): FlagSet =>
  set | flag;

const clearFlag = (set: FlagSet, flag: number): FlagSet =>
  set & ~flag;

const toggleFlag = (set: FlagSet, flag: number): FlagSet =>
  set ^ flag;

// Cách dùng: kết hợp nhiều cờ
const editorPerms = Flags.Read | Flags.Write;
hasFlag(editorPerms, Flags.Read);    // true
hasFlag(editorPerms, Flags.Delete);  // false
```

```rust [Rust]
// Rust theo idiom: hằng có kiểu, thao tác bitwise trên u32
pub const READ:    u32 = 1 << 0;
pub const WRITE:   u32 = 1 << 1;
pub const EXECUTE: u32 = 1 << 2;
pub const DELETE:  u32 = 1 << 3;

pub fn has_flag(flags: u32, flag: u32) -> bool {
    (flags & flag) == flag
}

pub fn has_any(flags: u32, mask: u32) -> bool {
    (flags & mask) != 0
}

pub fn set_flag(flags: u32, flag: u32) -> u32 {
    flags | flag
}

pub fn clear_flag(flags: u32, flag: u32) -> u32 {
    flags & !flag
}

pub fn toggle_flag(flags: u32, flag: u32) -> u32 {
    flags ^ flag
}

// Cách dùng
let editor = READ | WRITE;
assert!(has_flag(editor, READ));     // true
assert!(!has_flag(editor, DELETE));  // false
```

```go [Go]
// Go theo idiom: hằng có kiểu với iota
type Permission uint32

const (
    Read    Permission = 1 << iota // 0b0001
    Write                          // 0b0010
    Execute                        // 0b0100
    Delete                         // 0b1000
)

func HasFlag(flags, flag Permission) bool {
    return flags&flag == flag
}

func HasAny(flags, mask Permission) bool {
    return flags&mask != 0
}

func SetFlag(flags, flag Permission) Permission {
    return flags | flag
}

func ClearFlag(flags, flag Permission) Permission {
    return flags &^ flag // toán tử AND NOT của Go
}

func ToggleFlag(flags, flag Permission) Permission {
    return flags ^ flag
}

// Cách dùng
editor := Read | Write
HasFlag(editor, Read)    // true
HasFlag(editor, Delete)  // false
```

```python [Python]
# Python: toán tử bitwise tự nhiên, không giới hạn kích thước integer
READ    = 1 << 0  # 0b0001
WRITE   = 1 << 1  # 0b0010
EXECUTE = 1 << 2  # 0b0100
DELETE  = 1 << 3  # 0b1000

def has_flag(flags: int, flag: int) -> bool:
    return (flags & flag) == flag

def has_any(flags: int, mask: int) -> bool:
    return (flags & mask) != 0

def set_flag(flags: int, flag: int) -> int:
    return flags | flag

def clear_flag(flags: int, flag: int) -> int:
    return flags & ~flag

def toggle_flag(flags: int, flag: int) -> int:
    return flags ^ flag

# Cách dùng
editor = READ | WRITE
assert has_flag(editor, READ)       # True
assert not has_flag(editor, DELETE)  # True
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Thao tác cờ bitwise nền tảng (set, check, clear, toggle) | `exercises/typescript/bitmask/01-basic.test.ts` |
| Trung bình | Xây hệ phân quyền theo role | `exercises/typescript/bitmask/02-permission-system.test.ts` |
| Nâng cao | Cờ fiber kiểu React với bubble lên subtree | `exercises/typescript/bitmask/03-react-flags.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/bitmask/mod.rs` · Go `exercises/go/bitmask/bitmask_test.go` · Python `exercises/python/bitmask/test_bitmask.py`

## Khi nào nên dùng

- **Nhiều cờ boolean trên hot path** — một integer thay vì N boolean tiết kiệm bộ nhớ và cho phép thao tác hàng loạt
- **State tổ hợp** — khi cần kiểm tra "bất kỳ cái nào trong số này" hoặc "tất cả các cái này" trong một thao tác
- **Serialize** — một integer dễ lưu, truyền và so sánh
- **Hệ phân quyền** — mô hình `rwx` của Unix là bitmask không phải ngẫu nhiên
- **ECS (Entity Component System)** — mask thành viên component trong game engine

## Khi nào KHÔNG nên dùng

- **Hơn 32 cờ** — toán tử bitwise JavaScript làm việc trên integer 32-bit; vượt thì dùng `BigInt` hoặc `Set`
- **State loại trừ tương hỗ** — nếu chỉ một giá trị có thể active một lúc, dùng `enum`
- **Khả năng đọc quan trọng hơn hiệu năng** — trường boolean có tên rõ hơn cho phần lớn dev
- **Set cờ động** — nếu tập cờ khả dĩ không biết lúc compile, dùng `Set<string>`

## Thêm các ứng dụng production

- [Chromium](https://chromium.googlesource.com/chromium/src) — cờ compositing layer
- [SQLite](https://www.sqlite.org/src) — cờ VFS
- [Nginx](https://github.com/nginx/nginx) — cờ event
- [Bevy ECS](https://github.com/bevyengine/bevy/blob/fd4f66fc36ec9f8181afe85d65e22c52b14e86a9/crates/bevy_ecs/src/archetype.rs) — mask thành viên component trong ECS dựa trên archetype
- [Linux fcntl](https://github.com/torvalds/linux/blob/acb7500801e98639f6d8c2d796ed9f64cba83d3a/include/uapi/asm-generic/fcntl.h#L5-L30) — `O_RDONLY`, `O_WRONLY`, `O_CREAT` cờ kiểm soát file

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Tagged Union](/patterns/tagged-union/) | Cả hai mã hoá thông tin kiểu trong biểu diễn integer gọn |
| [Dirty Flag](/patterns/dirty-flag/) | Dirty flag thường lưu dưới dạng bit trong bitmask |
| [Double Buffering](/patterns/double-buffering/) | React dùng cờ bitmask trên mỗi node Fiber để theo dõi công việc trong cây double-buffer |

## Câu hỏi thử thách

::: details Câu 1: Team bạn định nghĩa 40 feature flag thành bitmask trong hệ thống config JavaScript. QA báo cờ 32-39 hành xử bất thường — đôi khi kiểm tra cờ trả false dù đã set. Có gì sai?
**Trả lời:** Toán tử bitwise JavaScript chỉ làm việc trên integer 32-bit, nên cờ ở vị trí 32 trở lên bị truncate âm thầm.

Toán tử `|`, `&`, `^` và `~` nội bộ chuyển toán hạng thành integer signed 32-bit. `1 << 32` wrap về `1` (cùng `1 << 0`), nghĩa là cờ 32 đụng cờ 0. Vượt 32 cờ, bạn cần `BigInt` cho thao tác bitwise hoặc chuyển sang cách tiếp cận `Set<string>`.
:::

::: details Câu 2: Bạn có `permissions = Read | Write | Execute`. Dev junior viết `if (permissions === Read)` để kiểm tra user có quyền đọc không. Hoạt động trong unit test nhưng fail trong production. Tại sao?
**Trả lời:** Phép `===` kiểm tra bằng chính xác, nên chỉ trả true khi permissions *chính xác* là `Read` và không gì khác.

Trong production, user thường có nhiều quyền kết hợp. `permissions === Read` sẽ là false cho `Read | Write` (giá trị 3 vs giá trị 1). Cách kiểm tra đúng là `(permissions & Read) !== 0` hoặc `(permissions & Read) === Read`, cô lập và kiểm tra chỉ bit Read bất kể các cờ khác.
:::

::: details Câu 3: React dùng cờ bitmask cho tác dụng phụ fiber. Vì sao React chọn bitmask thay vì mảng chuỗi như `['placement', 'update', 'ref']` để theo dõi fiber cần effect nào?
**Trả lời:** Bitmask cho phép React kiểm tra, kết hợp và lan truyền nhiều cờ effect trong một thao tác integer thay vì lặp mảng.

Khi reconciliation, React "bubble" effect con vào fiber cha qua `parent.subtreeFlags |= child.flags`. Với mảng, sẽ cần khử trùng lặp và nối. Cách bitmask cũng cho phép kiểm tra "subtree này có việc không?" bằng một so sánh `subtreeFlags !== 0` — then chốt khi duyệt hàng nghìn node fiber mỗi frame.
:::

::: details Câu 4: Bạn đang thiết kế hệ phân quyền nơi role loại trừ tương hỗ — user chính xác là một trong Admin, Editor hoặc Viewer. Đồng nghiệp đề nghị dùng bitmask. Có phải pattern phù hợp không?
**Trả lời:** Không. State loại trừ tương hỗ nên dùng enum, không phải bitmask.

Bitmask toả sáng khi cờ có thể kết hợp tự do (`Read | Write | Execute`). Với role loại trừ tương hỗ, bitmask cho phép bạn vô tình set `Admin | Viewer`, là state vô nghĩa. Enum thực thi đúng một giá trị ở cấp kiểu, làm state bất hợp lệ không biểu diễn được. Bitmask cho cờ tổ hợp; enum cho state loại trừ.
:::
