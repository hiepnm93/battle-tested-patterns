---
title: "Dự án này là gì?"
description: "Battle-Tested Patterns: 46 pattern lập trình đã được kiểm chứng trong production từ React, Linux, Go và Chromium với trực quan hoá tương tác."
---

# Dự án này là gì?

**Battle-Tested Patterns** sưu tầm các pattern lập trình có những đặc điểm sau:

1. **Đã được chứng minh trong production** — sử dụng tại các dự án hàng đầu như React, nhân Linux, Go runtime và Chromium
2. **Tương tác** — mỗi pattern có một trực quan hoá SVG thực hành mà bạn có thể click, kéo và thử nghiệm
3. **Đa ngôn ngữ** — triển khai theo idiom bằng TypeScript, Rust, Go và Python
4. **Cấp độ code** — các kỹ thuật cụ thể có thể áp dụng ngay hôm nay, không phải khái niệm kiến trúc trừu tượng

## Tại sao có dự án này

Đã có nhiều sách "design pattern" và kho lưu trữ "thuật toán". Nhưng vẫn còn một khoảng trống:

| Tài nguyên hiện có | Cái còn thiếu |
|---|---|
| Design Patterns (GoF) | Quá trừu tượng, quá thiên về OOP |
| Kho thuật toán | Tách rời khỏi thực hành kỹ thuật |
| Hướng dẫn System Design | Cấp kiến trúc, không phải cấp code |
| Danh sách "Awesome" | Tổng hợp liên kết, không có dạy học |
| Tutorial tương tác | Thường rời rạc, không phải bộ sưu tập có hệ thống |

Dự án này lấp đầy khoảng trống đó: **các kỹ thuật cấp code được trích xuất từ source code production, kèm trực quan hoá tương tác và tham chiếu chính xác bạn có thể tự kiểm chứng**.

## Điều gì khiến một pattern được gọi là "Battle-Tested"?

Mỗi pattern trong bộ sưu tập này phải có:

- **≥ 2 bằng chứng production** — liên kết GitHub chính xác (đến số dòng cụ thể) cho thấy pattern đang được dùng
- **Triển khai đa ngôn ngữ** — code theo idiom bằng TypeScript + ít nhất một ngôn ngữ khác
- **Bài tập chạy được** — có các cấp độ khó tăng dần kèm bộ test

Chúng tôi không bao giờ bịa liên kết nguồn. Nếu không tìm được tham chiếu xác minh được, pattern sẽ không được đưa vào.

## Lộ trình học khuyến nghị

Chọn một lộ trình phù hợp với background — hoặc cứ tự do duyệt qua.

### Lập trình viên frontend

Bắt đầu với các pattern bạn đã dùng (có thể không nhận ra):

1. [Diff / Patch](/patterns/diff-patch/) — reconciliation của virtual DOM trong React
2. [Bitmask](/patterns/bitmask/) — fiber flags của React
3. [Cooperative Scheduling](/patterns/cooperative-scheduling/) — tại sao React yield mỗi 5ms
4. [Observer](/patterns/observer/) — Redux, EventEmitter
5. [Double Buffering](/patterns/double-buffering/) — `current` / `workInProgress` của React Fiber

Sau đó xem chúng phối hợp: [Pattern trong React](/by-project/react) · Tra cứu nhanh: [Cheat Sheet](/guide/cheatsheet)

### Lập trình viên backend / hệ thống

Bắt đầu với các pattern xuất hiện trong database và hệ phân tán:

1. [Write-Ahead Log](/patterns/write-ahead-log/) — khôi phục sau crash trong PostgreSQL, etcd
2. [MVCC](/patterns/mvcc/) — vì sao reader không bao giờ chặn writer
3. [Circuit Breaker](/patterns/circuit-breaker/) — fail nhanh trong microservice
4. [Rate Limiter](/patterns/rate-limiter/) — token bucket để kiểm soát throughput
5. [Consistent Hashing](/patterns/consistent-hashing/) — phân tán key trên các node

Sau đó xem bức tranh đầy đủ: [Pattern trong hệ phân tán](/by-project/distributed-systems) · Tra cứu nhanh: [Cheat Sheet](/guide/cheatsheet)

### Kỹ sư hiệu năng / cấp thấp

Bắt đầu với các pattern bộ nhớ và concurrency:

1. [Arena Allocator](/patterns/arena-allocator/) — bump allocate, giải phóng tất cả cùng lúc
2. [Object Pool](/patterns/object-pool/) — tránh áp lực GC
3. [Free List](/patterns/free-list/) — cấp phát/giải phóng O(1)
4. [Work Stealing](/patterns/work-stealing/) — Go runtime, scheduler Tokio
5. [Ring Buffer](/patterns/ring-buffer/) — queue lock-free

Sau đó xem chúng phối hợp: [Pattern trong Go Runtime](/by-project/go-runtime) · [Pattern trong Linux](/by-project/linux) · Tra cứu nhanh: [Cheat Sheet](/guide/cheatsheet)

## Cách dùng dự án này

- **Chơi với trực quan hoá** — mỗi trang pattern có trực quan hoá SVG tương tác — click, kéo và xây dựng trực giác
- **Duyệt các pattern** — đọc khái niệm, nghiên cứu bằng chứng production, rồi thử các bài tập
- **Chạy bài tập tại máy** — `pnpm test:exercises` cho TypeScript, `cargo test` cho Rust, `go test` cho Go
- **Thử online** — copy bất kỳ code mẫu nào vào playground chính thức: [TypeScript](https://www.typescriptlang.org/play) · [Go](https://go.dev/play/) · [Rust](https://play.rust-lang.org/) · [Python](https://www.online-python.com/)
- **Đóng góp** — xem [Cách đóng góp](./how-to-contribute)
