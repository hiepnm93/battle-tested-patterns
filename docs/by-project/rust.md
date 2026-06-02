# Patterns from Rust

Rust's standard library embodies zero-cost abstractions through its type system.

| Pattern | Where | What It Does |
|---------|-------|--------------|
| [Iterator / Lazy Eval](/patterns/iterator/) | `core/iter/traits/iterator.rs` | The `Iterator` trait — `next()` + composable `map`/`filter`/`fold` |
| [Copy-on-Write](/patterns/copy-on-write/) | `alloc/src/borrow.rs` | `Cow<'a, B>` — clone-on-write smart pointer for zero-copy parsing |

## Further Reading

- [Rust Source Code (GitHub)](https://github.com/rust-lang/rust)
