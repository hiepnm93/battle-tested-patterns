---
description: "按场景查找模式 — Web API、数据库、分布式系统、前端、编译器等。"
---

# 使用场景

按你正在构建的系统类型查找模式。

## Web API 与微服务

构建 REST/gRPC 服务？这些模式让它在负载下保持可靠。

| 场景 | 模式 | 实际案例 |
|---|---|---|
| 防护下游故障 | [熔断器](/zh/patterns/circuit-breaker/) + [指数退避重试](/zh/patterns/retry-backoff/) | Netflix Hystrix 包装每个 HTTP 客户端调用 |
| API 限流 | [限流器](/zh/patterns/rate-limiter/) | Stripe 允许 25 个突发，以 25/秒补充 |
| 请求中间件（认证、日志、追踪） | [中间件链](/zh/patterns/middleware-chain/) | gRPC 拦截器，Koa.js 洋葱模型 |
| 服务发现 | [注册表](/zh/patterns/registry/) | Consul、etcd 服务注册 |
| 节点间负载分配 | [一致性哈希](/zh/patterns/consistent-hashing/) | HAProxy、groupcache 键分布 |
| 防止过载 | [背压](/zh/patterns/backpressure/) + [批处理](/zh/patterns/batch-processing/) | Node.js stream piping，Kafka 消费者组 |

## 数据库与存储

PostgreSQL、Redis、LevelDB 以及所有严肃存储引擎背后的模式。

| 场景 | 模式 | 实际案例 |
|---|---|---|
| 崩溃恢复 | [预写日志](/zh/patterns/write-ahead-log/) + [检查点](/zh/patterns/checkpointing/) | PostgreSQL：WAL + 定期 checkpoint |
| 写密集负载 | [LSM 树](/zh/patterns/lsm-tree/) + [布隆过滤器](/zh/patterns/bloom-filter/) | LevelDB/RocksDB：memtable → SSTable + bloom 跳过 |
| 磁盘范围查询 | [B+ 树](/zh/patterns/b-plus-tree/) | PostgreSQL btree 索引，SQLite |
| 并发读写 | [MVCC](/zh/patterns/mvcc/) | PostgreSQL 元组版本化，etcd 修订版 |
| 数据完整性验证 | [Merkle 树](/zh/patterns/merkle-tree/) | ZFS 块校验和，Git 对象存储 |
| 有序键合并 | [合并迭代器](/zh/patterns/merge-iterator/) + [最小堆](/zh/patterns/min-heap/) | LevelDB compaction |
| 删除但不立即移除 | [墓碑](/zh/patterns/tombstone/) | Cassandra tombstone，LevelDB 删除标记 |
| 内存有序集合 | [跳表](/zh/patterns/skip-list/) | Redis ZADD/ZRANGE 有序集合 |
| 内存缓存 | [LRU 缓存](/zh/patterns/lru-cache/) | Redis LRU 淘汰，Go groupcache |
| 无时钟事件排序 | [逻辑时钟](/zh/patterns/logical-clock/) | etcd Raft log，DynamoDB 版本向量 |

## 前端与 UI 框架

React、Vue 和浏览器引擎在每一帧中使用这些模式。

| 场景 | 模式 | 实际案例 |
|---|---|---|
| Virtual DOM diffing | [差异/补丁](/zh/patterns/diff-patch/) + [位掩码](/zh/patterns/bitmask/) | React reconciler：diff 树，应用最小补丁 |
| 响应式渲染 | [协作调度](/zh/patterns/cooperative-scheduling/) | React Scheduler：每 5ms 让出以保持 16ms 内 |
| 帧安全状态更新 | [双缓冲](/zh/patterns/double-buffering/) | React Fiber：workInProgress ↔ current 树交换 |
| 避免不必要的重渲染 | [脏标记](/zh/patterns/dirty-flag/) | React shouldComponentUpdate，Chromium layout |
| 状态管理 | [观察者](/zh/patterns/observer/) + [状态机](/zh/patterns/state-machine/) | Redux subscribe，XState 有限状态 |
| 优先级任务调度 | [最小堆](/zh/patterns/min-heap/) | React Scheduler 优先级队列 |

## 分布式系统

跨多台机器的系统模式。

| 场景 | 模式 | 实际案例 |
|---|---|---|
| 共识日志 | [预写日志](/zh/patterns/write-ahead-log/) + [逻辑时钟](/zh/patterns/logical-clock/) | etcd Raft：带 term/index 的追加日志 |
| 分区容错路由 | [一致性哈希](/zh/patterns/consistent-hashing/) | Amazon DynamoDB，Cassandra ring |
| 复制状态 | [状态机](/zh/patterns/state-machine/) + [预写日志](/zh/patterns/write-ahead-log/) | Raft：通过日志复制状态机 |
| 无冲突复制 | [逻辑时钟](/zh/patterns/logical-clock/) + [墓碑](/zh/patterns/tombstone/) | CRDT，Dynamo 风格 last-write-wins |
| 数据同步 | [Merkle 树](/zh/patterns/merkle-tree/) | Cassandra 反熵修复 |
| 消息驱动架构 | [Actor 模型](/zh/patterns/actor-model/) + [背压](/zh/patterns/backpressure/) | Akka cluster，Erlang/OTP |
| 构建/部署流水线 | [依赖图](/zh/patterns/dependency-graph/) + [批处理](/zh/patterns/batch-processing/) | Cargo 构建图，pnpm workspace |

## 运行时与内存管理

Go、CPython、V8 和游戏引擎如何管理内存和执行。

| 场景 | 模式 | 实际案例 |
|---|---|---|
| 减少 GC 压力 | [对象池](/zh/patterns/object-pool/) + [空闲链表](/zh/patterns/free-list/) | Go sync.Pool，Linux SLUB 分配器 |
| 阶段性分配 | [Arena 分配器](/zh/patterns/arena-allocator/) | Rust bumpalo，Go arena（实验性） |
| 确定性清理 | [引用计数](/zh/patterns/reference-counting/) | CPython refcount，Rust Rc/Arc |
| 字符串去重 | [驻留](/zh/patterns/interning/) + [享元](/zh/patterns/flyweight/) | Rust 编译器符号驻留，Python 小整数缓存 |
| 高效克隆 | [写时复制](/zh/patterns/copy-on-write/) | Linux fork()，Rust `Cow<T>` |
| 跨核工作分配 | [工作窃取](/zh/patterns/work-stealing/) | Go runtime P/M/G 调度器，Tokio |
| I/O 多路复用 | [事件循环](/zh/patterns/event-loop/) + [环形缓冲区](/zh/patterns/ring-buffer/) | libuv (Node.js)，Redis 单线程 |
| 线程安全计数器 | [信号量](/zh/patterns/semaphore/) | Linux 内核信号量，Go x/sync |

## 编译器与语言工具

LLVM、V8、rustc 以及 Vue/React 编译器中使用的模式。

| 场景 | 模式 | 实际案例 |
|---|---|---|
| AST 遍历 | [访问者](/zh/patterns/visitor/) | LLVM InstVisitor，Vue 编译器转换 |
| 动态分发 | [虚函数表](/zh/patterns/vtable/) | CPython tp_* slots，Rust dyn Trait |
| 符号表 | [驻留](/zh/patterns/interning/) + [前缀树](/zh/patterns/trie/) | rustc Symbol interning |
| IR 转换 | [迭代器](/zh/patterns/iterator/) + [差异/补丁](/zh/patterns/diff-patch/) | Rust Iterator 适配器，tree-sitter edits |
| 类型表示 | [标签联合体](/zh/patterns/tagged-union/) | V8 tagged pointers，PyTorch TensorImpl |
| 插件系统 | [注册表](/zh/patterns/registry/) + [中间件链](/zh/patterns/middleware-chain/) | Babel 插件，webpack loaders |

## 网络与协议

| 场景 | 模式 | 实际案例 |
|---|---|---|
| 连接状态追踪 | [状态机](/zh/patterns/state-machine/) | Linux TCP 状态机 (SYN_SENT → ESTABLISHED → ...) |
| IP 路由 | [前缀树](/zh/patterns/trie/) | Linux LC-trie IPv4 FIB |
| 报文缓冲 | [环形缓冲区](/zh/patterns/ring-buffer/) | Linux sk_buff，DPDK ring |
| 流控 | [背压](/zh/patterns/backpressure/) + [限流器](/zh/patterns/rate-limiter/) | TCP 流控，Nginx limit_req |
| DNS 解析 | [前缀树](/zh/patterns/trie/) + [LRU 缓存](/zh/patterns/lru-cache/) | 域名查找 + 响应缓存 |
