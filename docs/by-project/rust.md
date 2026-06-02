# Patterns from Rust

Rust's standard library embodies zero-cost abstractions through its type system.

| Pattern | Where | What It Does |
|---------|-------|--------------|
| [Iterator / Lazy Eval](/patterns/iterator/) | `core/iter/traits/iterator.rs` | The `Iterator` trait — `next()` + composable `map`/`filter`/`fold` |
| [Copy-on-Write](/patterns/copy-on-write/) | `alloc/src/borrow.rs` | `Cow<'a, B>` — clone-on-write smart pointer for zero-copy parsing |
| [Arena Allocator](/patterns/arena-allocator/) | bumpalo `lib.rs` | `Bump` — canonical Rust arena allocator, used in wasm-bindgen and Deno |
| [Work Stealing](/patterns/work-stealing/) | Tokio `worker.rs` | `Core::steal_work` — multi-threaded async runtime work stealing |
| [Dependency Graph](/patterns/dependency-graph/) | Cargo `resolver/` | DAG-based dependency resolution for crate compilation order |
| [Circuit Breaker](/patterns/circuit-breaker/) | Sony gobreaker | Go implementation, but pattern applies to Rust via `recloser` crate |

## Further Reading

- [Rust Source Code (GitHub)](https://github.com/rust-lang/rust) · [bumpalo (GitHub)](https://github.com/fitzgen/bumpalo)
