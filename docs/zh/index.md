---
layout: home

hero:
  name: Battle-Tested Patterns
  text: 生产验证的编程模式
  tagline: 源自 React、Linux、Go、Chromium 等顶级项目的实战经验。精确源码链接、多语言实现、交互式练习。
  actions:
    - theme: brand
      text: 快速开始
      link: /zh/guide/what-is-this
    - theme: alt
      text: 浏览模式
      link: /zh/patterns/bitmask/

features:
  - icon: 🔗
    title: 生产验证
    details: 每个模式附带精确到行号的 GitHub 源码链接，证明它在真实项目中被使用。
  - icon: 🌍
    title: 多语言实现
    details: TypeScript、Rust、Go、C 的地道实现——不是机械翻译，而是每种语言的原生表达。
  - icon: 🧪
    title: 可运行练习
    details: 渐进式练习（基础 → 进阶 → 高级），配套测试用例，本地即可运行。
  - icon: 🎮
    title: 官方 Playground
    details: 一键跳转 TypeScript、Go、Rust、Python 官方在线环境，直接动手实践。
---

## 编程模式

| 模式 | 核心洞察 | 来源项目 |
|------|---------|---------|
| [位掩码 (Bitmask)](/zh/patterns/bitmask/) | 将多个布尔标志压缩到一个整数中 | React, Linux, Chromium |
| [双缓冲 (Double Buffering)](/zh/patterns/double-buffering/) | 在两份副本间切换以实现原子更新 | React Fiber, GPU, PostgreSQL |
| [协作调度 (Cooperative Scheduling)](/zh/patterns/cooperative-scheduling/) | 主动让出控制权以保持响应 | React, Go Runtime |
| [最小堆 (Min Heap)](/zh/patterns/min-heap/) | O(1) 访问最高优先级元素 | React Scheduler, Linux CFS, Node.js |
| [差异/补丁 (Diff/Patch)](/zh/patterns/diff-patch/) | 计算两个状态之间的最小变更 | React Reconciler, Git |
| [对象池 (Object Pool)](/zh/patterns/object-pool/) | 预分配并复用对象，避免 GC | Go sync.Pool, Godot |
| [环形缓冲区 (Ring Buffer)](/zh/patterns/ring-buffer/) | 固定大小循环队列，零分配 | LMAX Disruptor, Linux ftrace |
| [状态机 (State Machine)](/zh/patterns/state-machine/) | 显式状态+转换，不可能状态不可表达 | XState, Linux TCP |
| [写时复制 (Copy-on-Write)](/zh/patterns/copy-on-write/) | 引用共享，修改时才复制 | Git 对象, Rust Cow |
| [观察者 (Observer)](/zh/patterns/observer/) | 订阅事件，通知时无耦合 | Node EventEmitter, Redux |
| [迭代器 (Iterator)](/zh/patterns/iterator/) | 惰性处理序列，零中间分配 | Rust Iterator, Python 生成器 |
| [信号量 (Semaphore)](/zh/patterns/semaphore/) | 用计数器限制并发操作 | Linux 内核, Go x/sync |
| [批处理 (Batch Processing)](/zh/patterns/batch-processing/) | 累积操作批量执行提升吞吐 | Kafka, React batched setState |
| [指数退避重试 (Retry)](/zh/patterns/retry-backoff/) | 指数增长延迟重试 + 抖动 | Kubernetes, gRPC |
| [享元/驻留 (Flyweight)](/zh/patterns/flyweight/) | 共享相同对象，避免重复分配 | Python 整数缓存, V8 |
