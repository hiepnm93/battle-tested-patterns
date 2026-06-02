# Rust 标准库中的模式

| 模式 | 位置 | 作用 |
|------|------|------|
| [迭代器](/zh/patterns/iterator/) | `core/iter/traits/iterator.rs` | `Iterator` trait — 零成本抽象的可组合序列处理 |
| [写时复制](/zh/patterns/copy-on-write/) | `alloc/src/borrow.rs` | `Cow<'a, B>` — 写时克隆智能指针 |
