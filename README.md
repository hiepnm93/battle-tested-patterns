<div align="center">

# Battle-Tested Patterns

**Code-level programming patterns extracted from production codebases.**

Every pattern backed by precise GitHub source links · Multi-language · Runnable exercises

[📖 Documentation](https://totoro-jam.github.io/battle-tested-patterns/) · [📖 中文文档](https://totoro-jam.github.io/battle-tested-patterns/zh/)

English | [简体中文](README.zh-CN.md)

[![CI](https://github.com/Totoro-jam/battle-tested-patterns/actions/workflows/ci.yml/badge.svg)](https://github.com/Totoro-jam/battle-tested-patterns/actions/workflows/ci.yml)
[![Deploy](https://github.com/Totoro-jam/battle-tested-patterns/actions/workflows/deploy.yml/badge.svg)](https://github.com/Totoro-jam/battle-tested-patterns/actions/workflows/deploy.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](.github/CONTRIBUTING.md)

</div>

## The Gap This Fills

| What exists | What's missing |
|------------|----------------|
| Design patterns books | Too abstract, too OOP-centric |
| Algorithm repos | Disconnected from real engineering |
| System design guides | Architecture-level, not code-level |

This project: **code-level techniques from React, Linux, Go, Chromium — each with verifiable source links**.

## Patterns

| Pattern | What It Does | Proven In |
|---------|-------------|-----------|
| [**Bitmask**](https://totoro-jam.github.io/battle-tested-patterns/patterns/bitmask/) | Pack N flags into one integer, check any combo in O(1) | [React Flags](https://github.com/facebook/react/blob/main/packages/react-reconciler/src/ReactFiberFlags.js#L14-L36) · [Linux stat.h](https://github.com/torvalds/linux/blob/master/include/uapi/linux/stat.h#L25-L33)|
| [**Double Buffering**](https://totoro-jam.github.io/battle-tested-patterns/patterns/double-buffering/) | Swap two copies atomically, zero allocation | [React Fiber](https://github.com/facebook/react/blob/main/packages/react-reconciler/src/ReactFiber.js#L327-L355) · [SDL](https://github.com/libsdl-org/SDL/blob/main/src/render/SDL_render.c)|
| [**Cooperative Scheduling**](https://totoro-jam.github.io/battle-tested-patterns/patterns/cooperative-scheduling/) | Yield control between work chunks to stay responsive | [React Scheduler](https://github.com/facebook/react/blob/main/packages/scheduler/src/forks/Scheduler.js#L188-L258) · [Go Runtime](https://github.com/golang/go/blob/master/src/runtime/proc.go#L4143-L4200)|
| [**Min Heap**](https://totoro-jam.github.io/battle-tested-patterns/patterns/min-heap/) | O(1) peek at highest priority, O(log n) push/pop | [React MinHeap](https://github.com/facebook/react/blob/main/packages/scheduler/src/SchedulerMinHeap.js#L17-L90) · [Linux CFS](https://github.com/torvalds/linux/blob/master/kernel/sched/fair.c#L1407-L1460)|
| [**Diff / Patch**](https://totoro-jam.github.io/battle-tested-patterns/patterns/diff-patch/) | Compute minimal edits between two sequences | [React Reconciler](https://github.com/facebook/react/blob/main/packages/react-reconciler/src/ReactChildFiber.js#L1169-L1340) · [Git](https://github.com/git/git/blob/master/diff.c#L5020-L5060)|
| [**Object Pool**](https://totoro-jam.github.io/battle-tested-patterns/patterns/object-pool/) | Pre-allocate and reuse to avoid GC pressure | [Go sync.Pool](https://github.com/golang/go/blob/master/src/sync/pool.go#L52-L97) · [Godot](https://github.com/godotengine/godot/blob/master/core/templates/pooled_list.h#L35-L100)|
| [**Ring Buffer**](https://totoro-jam.github.io/battle-tested-patterns/patterns/ring-buffer/) | Fixed-size circular queue, zero allocation | [LMAX Disruptor](https://github.com/LMAX-Exchange/disruptor/blob/master/src/main/java/com/lmax/disruptor/RingBuffer.java#L84-L130) · [Linux](https://github.com/torvalds/linux/blob/master/include/linux/ring_buffer.h#L12-L70)|
| [**State Machine**](https://totoro-jam.github.io/battle-tested-patterns/patterns/state-machine/) | Explicit states, impossible transitions unrepresentable | [XState](https://github.com/statelyai/xstate/blob/main/packages/core/src/StateMachine.ts#L58-L120) · [Linux TCP](https://github.com/torvalds/linux/blob/master/net/ipv4/tcp_input.c#L4865-L4920)|
| [**Copy-on-Write**](https://totoro-jam.github.io/battle-tested-patterns/patterns/copy-on-write/) | Share by reference, copy only on mutation | [Git objects](https://github.com/git/git/blob/master/object-file.c#L719-L730) · [Rust Cow](https://github.com/rust-lang/rust/blob/main/library/alloc/src/borrow.rs#L169-L220)|
| [**Observer**](https://totoro-jam.github.io/battle-tested-patterns/patterns/observer/) | Subscribe to events, decouple producers from consumers | [Node EventEmitter](https://github.com/nodejs/node/blob/main/lib/events.js#L456-L520) · [Redux](https://github.com/reduxjs/redux/blob/master/src/createStore.ts#L211-L280)|
| [**Iterator**](https://totoro-jam.github.io/battle-tested-patterns/patterns/iterator/) | Lazy sequences, zero intermediate allocations | [Rust Iterator](https://github.com/rust-lang/rust/blob/main/library/core/src/iter/traits/iterator.rs#L68-L112) · [Python gen](https://github.com/python/cpython/blob/main/Objects/genobject.c)|
| [**Semaphore**](https://totoro-jam.github.io/battle-tested-patterns/patterns/semaphore/) | Bounded concurrency with a counter | [Linux](https://github.com/torvalds/linux/blob/master/include/linux/semaphore.h#L15-L55) · [Go x/sync](https://github.com/golang/sync/blob/master/semaphore/semaphore.go)|
| [**Batch Processing**](https://totoro-jam.github.io/battle-tested-patterns/patterns/batch-processing/) | Accumulate ops, execute as group | [Kafka](https://github.com/apache/kafka/blob/trunk/clients/src/main/java/org/apache/kafka/clients/producer/internals/RecordAccumulator.java#L69-L120)|
| [**Retry with Backoff**](https://totoro-jam.github.io/battle-tested-patterns/patterns/retry-backoff/) | Exponential delay + jitter on failure | [Kubernetes](https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/apimachinery/pkg/util/wait/backoff.go#L30-L50) · [gRPC](https://github.com/grpc/grpc/blob/master/doc/connection-backoff.md)|
| [**Flyweight**](https://totoro-jam.github.io/battle-tested-patterns/patterns/flyweight/) | Share identical objects, avoid duplicates | [Python int cache](https://github.com/python/cpython/blob/main/Objects/longobject.c#L61-L75)|

> Every "Proven In" link goes to the **exact lines** in the source code. Not a directory. Not a file. The lines.

## What a Pattern Looks Like

Each pattern follows a consistent structure — here's a taste from **Bitmask**:

```text
  Bit position:  7   6   5   4   3   2   1   0
                ┌───┬───┬───┬───┬───┬───┬───┬───┐
  Flags:        │   │   │   │ SN│ CB│ RF│ UP│ PL│
                └───┴───┴───┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┘
                              │   │   │   │   └─ Placement  (1 << 0)
                              │   │   │   └──── Update     (1 << 1)
                              │   │   └──────── Ref        (1 << 2)
                              │   └──────────── Callback   (1 << 3)
                              └──────────────── Snapshot   (1 << 4)
```

Implementations in 4 languages, each idiomatic:

```typescript
// TypeScript                          // Python
const READ  = 1 << 0;                  READ  = 1 << 0
const WRITE = 1 << 1;                  WRITE = 1 << 1
const perms = READ | WRITE;            perms = READ | WRITE
(perms & READ) !== 0;  // true         bool(perms & READ)  # True
```

Then exercises at 3 difficulty levels — all with tests you can run.

## Quick Start

```bash
git clone https://github.com/Totoro-jam/battle-tested-patterns.git
cd battle-tested-patterns && pnpm install

pnpm test                         # TypeScript exercises (Vitest)
cd exercises/rust && cargo test   # Rust exercises
cd exercises/go && go test ./...  # Go exercises
pnpm dev                          # Local docs site
```

## Contributing

See [CONTRIBUTING.md](.github/CONTRIBUTING.md). The bar is intentionally high:

1. **≥ 2 production proofs** with verified, line-number-precise source links
2. **TypeScript + ≥ 1 other language** — idiomatic, not translated
3. **≥ 2 exercises** with tests that pass
4. Source links checked weekly by CI — broken links auto-open an Issue

## License

[MIT](LICENSE) © Totoro-jam
