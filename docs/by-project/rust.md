---
title: "Pattern trong Rust"
description: "Pattern thư viện chuẩn Rust: iterator, copy-on-write (Cow), reference counting (Arc), interning và cấp phát arena."
---

# Pattern trong Rust

Thư viện chuẩn của Rust thể hiện các trừu tượng không tốn chi phí thông qua hệ kiểu của nó.

| Pattern | Ở đâu | Tác dụng |
|---------|-------|--------------|
| [Iterator / Đánh giá lười](/patterns/iterator/) | [`core/iter/traits/iterator.rs`](https://github.com/rust-lang/rust/blob/d56483a91d6cf5041351a3208b8d08f98f0c8b56/library/core/src/iter/traits/iterator.rs#L68-L112) | Trait `Iterator` — `next()` + `map`/`filter`/`fold` có thể ghép |
| [Copy-on-Write](/patterns/copy-on-write/) | [`alloc/src/borrow.rs`](https://github.com/rust-lang/rust/blob/d56483a91d6cf5041351a3208b8d08f98f0c8b56/library/alloc/src/borrow.rs#L169-L220) | `Cow<'a, B>` — smart pointer clone-on-write cho parse zero-copy |
| [Arena Allocator](/patterns/arena-allocator/) | [bumpalo `lib.rs`](https://github.com/fitzgen/bumpalo/blob/d2cc4dd0b8830d5b05d44e9decc776823e6a70ea/src/lib.rs#L378-L383) | `Bump` — arena allocator chuẩn của Rust, dùng trong wasm-bindgen và Deno |
| [Work Stealing](/patterns/work-stealing/) | [Tokio `worker.rs`](https://github.com/tokio-rs/tokio/blob/bde89678532a8091d958268c0d36eac9362317d8/tokio/src/runtime/scheduler/multi_thread/worker.rs#L1136-L1175) | `Core::steal_work` — work stealing của runtime async đa luồng |
| [Dependency Graph](/patterns/dependency-graph/) | [Cargo `resolver/`](https://github.com/rust-lang/cargo/blob/b50aa179d3d1099b53548bc8693dd17ddd019ab4/src/cargo/core/resolver/dep_cache.rs#L1-L50) | Phân giải dependency dựa trên DAG cho thứ tự biên dịch crate |
| [Reference Counting](/patterns/reference-counting/) | [`alloc/src/sync.rs`](https://github.com/rust-lang/rust/blob/d56483a91d6cf5041351a3208b8d08f98f0c8b56/library/alloc/src/sync.rs) | `Arc<T>` — reference counting nguyên tử cho quyền sở hữu chung giữa các thread |
| [Interning](/patterns/interning/) | [rustc `symbol.rs`](https://github.com/rust-lang/rust/blob/ab26b175979ee7b2cb3302dce204b99df96f7efb/compiler/rustc_span/src/symbol.rs#L24-L79) | `Symbol` là một index `u32` vào interner toàn cục — mọi identifier đều intern để so sánh O(1) |
| [Semaphore](/patterns/semaphore/) | [Tokio `semaphore.rs`](https://github.com/tokio-rs/tokio/blob/bde89678532a8091d958268c0d36eac9362317d8/tokio/src/sync/semaphore.rs) | `Semaphore` — kiểm soát concurrency có giới hạn nhận biết async |

## Cách chúng kết hợp: Biên dịch một crate

Khi `cargo build` biên dịch một crate Rust, compiler và runtime dùng các pattern này cùng nhau:

<CompositionFlow variant="rust-build" />

Triết lý zero-cost abstractions của Rust có nghĩa là các pattern này không có chi phí runtime nào vượt quá những gì một bản triển khai C viết tay phải chịu. Trait `Iterator` biên dịch xuống cùng machine code như vòng lặp thủ công. `Cow<T>` tránh clone khi dữ liệu chỉ được đọc. `Arc<T>` chỉ dùng thao tác nguyên tử khi thực sự được chia sẻ.

## Đọc thêm

- [Source Rust (GitHub)](https://github.com/rust-lang/rust) · [bumpalo (GitHub)](https://github.com/fitzgen/bumpalo) · [Tokio (GitHub)](https://github.com/tokio-rs/tokio)
