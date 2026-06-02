# Rust 标准库中的模式

| 模式 | 位置 | 作用 |
|------|------|------|
| [迭代器](/zh/patterns/iterator/) | `core/iter/traits/iterator.rs` | `Iterator` trait — 零成本抽象的可组合序列处理 |
| [写时复制](/zh/patterns/copy-on-write/) | `alloc/src/borrow.rs` | `Cow<'a, B>` — 写时克隆智能指针 |
| [Arena 分配器](/zh/patterns/arena-allocator/) | bumpalo `lib.rs` | `Bump` — Rust 经典 arena 分配器，被 wasm-bindgen 和 Deno 使用 |
| [工作窃取](/zh/patterns/work-stealing/) | Tokio `worker.rs` | `Core::steal_work` — 多线程异步运行时的工作窃取 |
| [依赖图](/zh/patterns/dependency-graph/) | Cargo `resolver/` | 基于 DAG 的依赖解析，确定 crate 编译顺序 |
