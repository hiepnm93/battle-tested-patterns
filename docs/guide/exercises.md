---
title: "Hướng dẫn bài tập"
description: "Hướng dẫn cài đặt từng bước cho bài tập TypeScript, Rust, Go và Python — điều kiện tiên quyết, cách chạy test và xử lý sự cố."
---

# Hướng dẫn bài tập

Dự án này có **bài tập bằng 4 ngôn ngữ** — TypeScript, Rust, Go và Python. Mỗi pattern có ít nhất một bài tập cho mỗi ngôn ngữ, với phần triển khai chạy được và các marker `TODO` để bạn viết lại.

## Điều kiện tiên quyết

| Ngôn ngữ | Phiên bản yêu cầu | Cài đặt |
|----------|-----------------|---------|
| Node.js | v22 LTS | [nvm](https://github.com/nvm-sh/nvm) hoặc [nodejs.org](https://nodejs.org/) |
| Rust | stable (mới nhất) | [rustup.rs](https://rustup.rs/) |
| Go | 1.21+ | [go.dev/dl](https://go.dev/dl/) |
| Python | 3.10+ | [python.org](https://www.python.org/downloads/) hoặc trình quản lý gói hệ thống |

## Khởi động nhanh

```bash
# Clone repo
git clone https://github.com/Totoro-jam/battle-tested-patterns.git
cd battle-tested-patterns

# Dùng đúng phiên bản Node.js
nvm use   # đọc .nvmrc → Node 22
```

## Cài đặt theo ngôn ngữ

### TypeScript

```bash
# Cài dependency (một lần)
pnpm install

# Chạy tất cả bài tập TypeScript
pnpm test:exercises

# Chạy một pattern cụ thể
pnpm test:exercises bitmask

# Chế độ watch — chạy lại khi lưu file
pnpm test:exercises -- --watch
```

**Vị trí file:** `exercises/typescript/<tên-pattern>/01-basic.test.ts`

Mỗi pattern có 1–3 file bài tập theo cấp độ (01-basic, 02-intermediate, 03-advanced).

### Rust

```bash
# Không cần cài thêm — Cargo xử lý tất cả

# Chạy tất cả bài tập Rust
cd exercises/rust
cargo test

# Chạy một pattern cụ thể
cargo test bitmask

# Chạy với output hiển thị
cargo test bitmask -- --nocapture
```

**Vị trí file:** `exercises/rust/src/<tên_pattern>/mod.rs`

Mỗi file chứa cả phần triển khai và test trong một module với `#[cfg(test)]`.

### Go

```bash
# Không cần cài thêm — Go module xử lý dependency

# Chạy tất cả bài tập Go
cd exercises/go
go test ./...

# Chạy một pattern cụ thể
go test -run Bitmask -v ./...

# Chạy với output chi tiết
go test -v ./...
```

**Vị trí file:** `exercises/go/<tên_pattern>/<tên_pattern>_test.go`

Mỗi file chứa cả phần triển khai và hàm test trong cùng một package.

### Python

```bash
# Cài pytest (một lần)
pip install pytest

# Chạy tất cả bài tập Python
cd exercises/python
pytest

# Chạy một pattern cụ thể
pytest bitmask/test_bitmask.py

# Chạy với output chi tiết
pytest -v
```

**Vị trí file:** `exercises/python/<tên_pattern>/test_<tên_pattern>.py`

Mỗi file độc lập — không import chéo file.

## Cách bài tập hoạt động

Mỗi bài tập theo **định dạng TODO-stub**:

1. Các hàm đã có **triển khai chạy được** (để CI luôn pass)
2. Marker `// TODO: implement` chỉ ra các dòng bạn cần viết lại
3. Các test phía dưới đường ngăn cách là **bất biến** — đừng sửa
4. Xoá thân hàm, triển khai từ đầu, chạy test

### Quy trình ví dụ

```bash
# 1. Chọn một pattern — ví dụ ring-buffer
# 2. Mở file bài tập trong editor
# 3. Tìm các marker TODO
# 4. Xoá phần triển khai, giữ chữ ký hàm
# 5. Viết phần triển khai của bạn
# 6. Chạy test để kiểm tra:
pnpm test:exercises ring-buffer     # TypeScript
cargo test ring_buffer     # Rust
go test -run RingBuffer    # Go
pytest ring_buffer/test_ring_buffer.py # Python
```

### Đường ngăn cách

```text
// ─── Tests (do not modify below this line) ───────────────────────
```

Mọi thứ phía trên đường này là sân chơi của bạn. Mọi thứ phía dưới là bộ test.

### Thành công / thất bại trông thế nào

Khi triển khai đúng:

```text
✓ Ring Buffer - Basic: should enqueue and dequeue in FIFO order (2ms)
✓ Ring Buffer - Basic: should reject enqueue when full
```

Khi có gì đó sai:

```text
✗ Ring Buffer - Basic: should enqueue and dequeue in FIFO order
  → expected 1, got undefined
```

## File đáp án

Phần triển khai tham chiếu nằm trong `exercises/answers/<ngôn-ngữ>/<pattern>/`:

```text
exercises/answers/
├── typescript/   # 46 thư mục, mỗi cái một .ts
├── rust/         # 46 thư mục, mỗi cái một .rs
├── go/           # 46 thư mục, mỗi cái một .go
└── python/       # 46 thư mục, mỗi cái một .py
```

Chúng chứa code triển khai thuần (không test). Dùng để đối chiếu hoặc nghiên cứu hướng tiếp cận khác.

## Chạy tất cả ngôn ngữ cùng lúc

```bash
# Từ thư mục gốc dự án:
pnpm test:exercises                        # TypeScript (491 test)
(cd exercises/rust && cargo test)          # Rust (173 test)
(cd exercises/go && go test ./...)         # Go (176 test)
(cd exercises/python && pytest)            # Python (233 test)
```

## Xử lý sự cố

| Vấn đề | Giải pháp |
|---------|----------|
| `nvm: command not found` | Cài nvm: `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh \| bash` |
| `pnpm: command not found` | Cài pnpm: `npm install -g pnpm` |
| `rustup: command not found` | Cài Rust: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \| sh` |
| `go: command not found` | Tải từ [go.dev/dl](https://go.dev/dl/) và thêm vào PATH |
| `pytest: command not found` | `pip install pytest` (hoặc `pip3 install pytest`) |
| Test TypeScript lỗi import | Chạy `pnpm install` trước |
| Test Rust không compile được | Chạy `rustup update` để có stable mới nhất |
| Test Go báo lỗi module | Chạy `go mod tidy` trong `exercises/go/` |
| Python `ModuleNotFoundError` | Mỗi file độc lập — không cần import |
