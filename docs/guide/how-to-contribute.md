---
title: "Cách đóng góp"
description: "Cách đóng góp một pattern mới: yêu cầu xác minh, chuẩn liên kết nguồn, hướng dẫn triển khai đa ngôn ngữ."
---

# Cách đóng góp

Chúng tôi hoan nghênh các đóng góp! Đây là cách bắt đầu.

## Khởi động nhanh

```bash
git clone https://github.com/Totoro-jam/battle-tested-patterns.git
cd battle-tested-patterns
pnpm install
pnpm dev        # Khởi động dev server tài liệu
pnpm test       # Chạy tất cả test (bài tập + component tài liệu)
```

## Các loại đóng góp

### Thêm một pattern mới

1. Mở một [Issue](https://github.com/Totoro-jam/battle-tested-patterns/issues/new?template=new-pattern.md) đề xuất pattern
2. Theo [SOP 01: Pattern mới](https://github.com/Totoro-jam/battle-tested-patterns/blob/e758be266d38db94723be233863e6f3effbf46cc/.sop/01-new-pattern.md)
3. Gửi PR kèm checklist đã điền

### Thêm phần triển khai ngôn ngữ

- Chọn một pattern còn thiếu ngôn ngữ của bạn
- Theo [SOP 03: Triển khai đa ngôn ngữ](https://github.com/Totoro-jam/battle-tested-patterns/blob/e758be266d38db94723be233863e6f3effbf46cc/.sop/03-multi-lang-impl.md)
- Bản triển khai phải **theo idiom** — không phải dịch dòng-một-dòng

### Sửa liên kết hỏng

- Theo [SOP 06: Sửa liên kết hỏng](https://github.com/Totoro-jam/battle-tested-patterns/blob/e758be266d38db94723be233863e6f3effbf46cc/.sop/06-broken-link-fix.md)

### Cải thiện tài liệu

- Sửa lỗi typo, làm rõ phần giải thích, cải thiện sơ đồ
- Dùng commit type `docs:`

## Tiêu chuẩn chất lượng

Mỗi pattern phải đáp ứng tối thiểu các yêu cầu sau:

- ≥ 2 bằng chứng production với liên kết GitHub chính xác (tới số dòng)
- Triển khai TypeScript + ≥ 1 ngôn ngữ khác (Rust/Go/Python)
- File bài tập cho cả 4 ngôn ngữ (TS, Rust, Go, Python) + file đáp án
- Bản dịch tiếng Trung với khối code giống nhau
- Tất cả test pass (`pnpm test` · `cargo test` · `go test ./...` · `pytest`), không có lỗi lint

Xem checklist đầy đủ trong [template PR](https://github.com/Totoro-jam/battle-tested-patterns/blob/e758be266d38db94723be233863e6f3effbf46cc/.github/PULL_REQUEST_TEMPLATE.md).

## Quy ước commit

Chúng tôi dùng [Conventional Commits](https://www.conventionalcommits.org/):

```text
feat: add cooperative-scheduling pattern
fix: update broken Linux source link in bitmask
docs: improve Core Idea diagram for double-buffering
test: add advanced exercise for min-heap
ci: add Go test step to CI workflow
chore: update dependencies
```
