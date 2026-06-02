<div align="center">

# Battle-Tested Patterns

**从顶级开源项目源码中提炼的代码级编程模式。**

每个模式附带精确到行号的源码链接 · 多语言实现 · 可运行练习

[📖 Documentation](https://totoro-jam.github.io/battle-tested-patterns/) · [📖 中文文档](https://totoro-jam.github.io/battle-tested-patterns/zh/)

[English](README.md) | 简体中文

[![CI](https://github.com/Totoro-jam/battle-tested-patterns/actions/workflows/ci.yml/badge.svg)](https://github.com/Totoro-jam/battle-tested-patterns/actions/workflows/ci.yml)
[![Deploy](https://github.com/Totoro-jam/battle-tested-patterns/actions/workflows/deploy.yml/badge.svg)](https://github.com/Totoro-jam/battle-tested-patterns/actions/workflows/deploy.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](.github/CONTRIBUTING.md)

</div>

## 填补什么空白

| 现有资源 | 缺失的部分 |
|---------|-----------|
| 设计模式书 | 太抽象，过于 OOP |
| 算法仓库 | 脱离工程实践 |
| 系统设计指南 | 架构层面，不涉及代码级 |

本项目：**从 React、Linux、Go、Chromium 等项目中提取的代码级技巧——每个都有可验证的源码链接**。

## 编程模式

| 模式 | 做什么 | 验证来源 |
|------|--------|---------|
| [**位掩码**](https://totoro-jam.github.io/battle-tested-patterns/zh/patterns/bitmask/) | 将 N 个标志打包到一个整数，O(1) 检查任意组合 | [React Flags](https://github.com/facebook/react/blob/main/packages/react-reconciler/src/ReactFiberFlags.js#L14-L36) · [Linux stat.h](https://github.com/torvalds/linux/blob/master/include/uapi/linux/stat.h#L25-L33)|
| [**双缓冲**](https://totoro-jam.github.io/battle-tested-patterns/zh/patterns/double-buffering/) | 原子交换两份副本，零分配 | [React Fiber](https://github.com/facebook/react/blob/main/packages/react-reconciler/src/ReactFiber.js#L327-L355) · [SDL](https://github.com/libsdl-org/SDL/blob/main/src/render/SDL_render.c)|
| [**协作调度**](https://totoro-jam.github.io/battle-tested-patterns/zh/patterns/cooperative-scheduling/) | 在工作块之间让出控制权保持响应 | [React Scheduler](https://github.com/facebook/react/blob/main/packages/scheduler/src/forks/Scheduler.js#L188-L258) · [Go Runtime](https://github.com/golang/go/blob/master/src/runtime/proc.go#L4143-L4200)|
| [**最小堆**](https://totoro-jam.github.io/battle-tested-patterns/zh/patterns/min-heap/) | O(1) 查看最高优先级，O(log n) 插入/删除 | [React MinHeap](https://github.com/facebook/react/blob/main/packages/scheduler/src/SchedulerMinHeap.js#L17-L90) · [Linux CFS](https://github.com/torvalds/linux/blob/master/kernel/sched/fair.c#L1407-L1460)|
| [**差异/补丁**](https://totoro-jam.github.io/battle-tested-patterns/zh/patterns/diff-patch/) | 计算两个序列之间的最小编辑 | [React Reconciler](https://github.com/facebook/react/blob/main/packages/react-reconciler/src/ReactChildFiber.js#L1169-L1340) · [Git](https://github.com/git/git/blob/master/diff.c#L5020-L5060)|
| [**对象池**](https://totoro-jam.github.io/battle-tested-patterns/zh/patterns/object-pool/) | 预分配复用对象，避免 GC 压力 | [Go sync.Pool](https://github.com/golang/go/blob/master/src/sync/pool.go#L52-L97) · [Godot](https://github.com/godotengine/godot/blob/master/core/templates/pooled_list.h#L35-L100)|
| [**环形缓冲区**](https://totoro-jam.github.io/battle-tested-patterns/zh/patterns/ring-buffer/) | 固定大小循环队列，零分配 | [LMAX Disruptor](https://github.com/LMAX-Exchange/disruptor/blob/master/src/main/java/com/lmax/disruptor/RingBuffer.java#L84-L130) · [Linux](https://github.com/torvalds/linux/blob/master/include/linux/ring_buffer.h#L12-L70)|
| [**状态机**](https://totoro-jam.github.io/battle-tested-patterns/zh/patterns/state-machine/) | 显式状态，不可能的转换不存在 | [XState](https://github.com/statelyai/xstate/blob/main/packages/core/src/StateMachine.ts#L58-L120) · [Linux TCP](https://github.com/torvalds/linux/blob/master/net/ipv4/tcp_input.c#L4865-L4920)|
| [**写时复制**](https://totoro-jam.github.io/battle-tested-patterns/zh/patterns/copy-on-write/) | 引用共享，修改时才复制 | [Git objects](https://github.com/git/git/blob/master/object-file.c#L719-L730) · [Rust Cow](https://github.com/rust-lang/rust/blob/main/library/alloc/src/borrow.rs#L169-L220)|
| [**观察者**](https://totoro-jam.github.io/battle-tested-patterns/zh/patterns/observer/) | 订阅事件，生产者消费者解耦 | [Node EventEmitter](https://github.com/nodejs/node/blob/main/lib/events.js#L456-L520) · [Redux](https://github.com/reduxjs/redux/blob/master/src/createStore.ts#L211-L280)|
| [**迭代器**](https://totoro-jam.github.io/battle-tested-patterns/zh/patterns/iterator/) | 惰性序列，零中间分配 | [Rust Iterator](https://github.com/rust-lang/rust/blob/main/library/core/src/iter/traits/iterator.rs#L68-L112) · [Python gen](https://github.com/python/cpython/blob/main/Objects/genobject.c)|
| [**信号量**](https://totoro-jam.github.io/battle-tested-patterns/zh/patterns/semaphore/) | 计数器限制并发 | [Linux](https://github.com/torvalds/linux/blob/master/include/linux/semaphore.h#L15-L55) · [Go x/sync](https://github.com/golang/sync/blob/master/semaphore/semaphore.go)|
| [**批处理**](https://totoro-jam.github.io/battle-tested-patterns/zh/patterns/batch-processing/) | 累积操作批量执行 | [Kafka](https://github.com/apache/kafka/blob/trunk/clients/src/main/java/org/apache/kafka/clients/producer/internals/RecordAccumulator.java#L69-L120)|
| [**指数退避重试**](https://totoro-jam.github.io/battle-tested-patterns/zh/patterns/retry-backoff/) | 指数延迟 + 抖动重试 | [Kubernetes](https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/apimachinery/pkg/util/wait/backoff.go#L30-L50) · [gRPC](https://github.com/grpc/grpc/blob/master/doc/connection-backoff.md)|
| [**享元/驻留**](https://totoro-jam.github.io/battle-tested-patterns/zh/patterns/flyweight/) | 共享相同对象避免重复 | [Python int cache](https://github.com/python/cpython/blob/main/Objects/longobject.c#L61-L75)|

> 每个"验证来源"链接都指向源代码的**精确行号**。不是目录，不是文件，是行。

## 模式长什么样

每个模式遵循一致的结构——以**位掩码**为例：

```text
  比特位:        7   6   5   4   3   2   1   0
                ┌───┬───┬───┬───┬───┬───┬───┬───┐
  标志:         │   │   │   │ SN│ CB│ RF│ UP│ PL│
                └───┴───┴───┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┘
                              │   │   │   │   └─ Placement  (1 << 0)
                              │   │   │   └──── Update     (1 << 1)
                              │   │   └──────── Ref        (1 << 2)
                              │   └──────────── Callback   (1 << 3)
                              └──────────────── Snapshot   (1 << 4)
```

4 种语言实现，各自地道：

```typescript
// TypeScript                          // Python
const READ  = 1 << 0;                  READ  = 1 << 0
const WRITE = 1 << 1;                  WRITE = 1 << 1
const perms = READ | WRITE;            perms = READ | WRITE
(perms & READ) !== 0;  // true         bool(perms & READ)  # True
```

然后是 3 个难度等级的练习——全部配套可运行测试。

## 快速开始

```bash
git clone https://github.com/Totoro-jam/battle-tested-patterns.git
cd battle-tested-patterns && pnpm install

pnpm test                         # TypeScript 练习 (Vitest)
cd exercises/rust && cargo test   # Rust 练习
cd exercises/go && go test ./...  # Go 练习
pnpm dev                          # 本地文档站
```

## 参与贡献

详见 [CONTRIBUTING.md](.github/CONTRIBUTING.md)（[中文版](.github/CONTRIBUTING.zh-CN.md)）。门槛不低：

1. **≥ 2 个生产验证** — 精确到行号的已验证源码链接
2. **TypeScript + ≥ 1 种其他语言** — 地道实现，不是翻译
3. **≥ 2 个练习** — 配套测试且通过
4. 源码链接每周由 CI 自动检查——失效链接自动开 Issue

## 许可证

[MIT](LICENSE) © Totoro-jam
