# 全部模式

46 个生产验证的编程模式，按类别组织。每个都包含交互式可视化、多语言实现、练习和精确源码链接。

## 数据结构

| 模式 | 一句话描述 | 来源 |
|------|-----------|------|
| [位掩码 (Bitmask)](./bitmask/) | 将 N 个标志压缩到一个整数，O(1) 检查任意组合 | React, Linux |
| [最小堆 (Min Heap)](./min-heap/) | O(1) 查看最高优先级，O(log n) 插入/删除 | React, Linux CFS |
| [环形缓冲区 (Ring Buffer)](./ring-buffer/) | 固定大小循环队列，零分配 | LMAX, Linux |
| [Trie 前缀树](./trie/) | O(k) 前缀查找，共享前缀共享节点 | Linux FIB, Redis |
| [跳表 (Skip List)](./skip-list/) | 概率 O(log n) 有序结构 | Redis, LevelDB |
| [布隆过滤器 (Bloom Filter)](./bloom-filter/) | 概率集合判存，零漏判 | LevelDB, Chromium |
| [LRU 缓存](./lru-cache/) | 淘汰最少使用，O(1) get/put | groupcache, Linux |
| [B+ 树](./b-plus-tree/) | 高扇出平衡树，叶链支持范围扫描 | PostgreSQL, SQLite |
| [标签联合 (Tagged Union)](./tagged-union/) | 类型标签 + 联合体安全分发 | Godot, PyTorch |
| [Merkle 树](./merkle-tree/) | 哈希逐层上推实现 O(log n) 完整性证明 | Git, ZFS |
| [归并迭代器 (Merge Iterator)](./merge-iterator/) | 最小堆实现 K 路合并 | LevelDB, RocksDB |

## 并发

| 模式 | 一句话描述 | 来源 |
|------|-----------|------|
| [信号量 (Semaphore)](./semaphore/) | 计数器限制并发访问 | Linux, Go |
| [Actor 模型](./actor-model/) | 私有状态+信箱，无共享内存 | Akka, Erlang |
| [工作窃取 (Work Stealing)](./work-stealing/) | 空闲线程从繁忙队列窃取 | Go, Tokio |
| [MVCC](./mvcc/) | 版本化行让读者永不阻塞写者 | PostgreSQL, etcd |
| [协作调度](./cooperative-scheduling/) | 在工作块间让出控制权保持响应 | React, Go |
| [双缓冲 (Double Buffering)](./double-buffering/) | 交换两份副本实现原子更新 | React Fiber, GPU |
| [背压 (Backpressure)](./backpressure/) | 消费者跟不上时减慢生产者 | Node.js, Reactive |
| [事件循环 (Event Loop)](./event-loop/) | 单线程 I/O 多路复用 | libuv, Redis |
| [逻辑时钟 (Logical Clock)](./logical-clock/) | 无需墙钟排序事件 | etcd, LevelDB |

## 系统

| 模式 | 一句话描述 | 来源 |
|------|-----------|------|
| [熔断器 (Circuit Breaker)](./circuit-breaker/) | 停止调用故障服务，快速失败 | Hystrix, gobreaker |
| [限流器 (Rate Limiter)](./rate-limiter/) | 令牌桶控制吞吐量 | Go, Nginx |
| [指数退避重试 (Retry)](./retry-backoff/) | 失败时指数延迟 + 抖动 | K8s, gRPC |
| [预写日志 (WAL)](./write-ahead-log/) | 应用前先记录变更，崩溃安全 | etcd, PostgreSQL |
| [批处理 (Batch Processing)](./batch-processing/) | 累积操作批量执行 | Kafka, React |
| [一致性哈希](./consistent-hashing/) | 增删节点只重映射 ~1/n 的键 | groupcache, HAProxy |
| [依赖图 (Dependency Graph)](./dependency-graph/) | DAG + 拓扑排序 | Cargo, pnpm |
| [中间件链 (Middleware Chain)](./middleware-chain/) | 可组合的前/后处理器 | gRPC, Koa |
| [注册表 (Registry)](./registry/) | 按名注册，运行时发现 | TensorFlow, gRPC |
| [脏标记 (Dirty Flag)](./dirty-flag/) | 变更时标脏，按需重算 | Chromium, React |
| [LSM 树](./lsm-tree/) | 写入缓冲在内存，刷入磁盘有序文件 | LevelDB, RocksDB |
| [检查点 (Checkpointing)](./checkpointing/) | 周期快照，从检查点恢复 | PostgreSQL, Redis |

## 内存

| 模式 | 一句话描述 | 来源 |
|------|-----------|------|
| [对象池 (Object Pool)](./object-pool/) | 预分配复用避免 GC | Go sync.Pool, Godot |
| [享元 (Flyweight)](./flyweight/) | 跨使用方共享不可变对象 | Python 整数缓存, V8 |
| [Arena 分配器](./arena-allocator/) | 区域内推进指针分配，一次性释放 | bumpalo, Go |
| [空闲链表 (Free List)](./free-list/) | 链表已释放槽位 O(1) 分配/释放 | Go runtime, Linux |
| [写时复制 (Copy-on-Write)](./copy-on-write/) | 引用共享，修改时才复制 | Git, Rust Cow |
| [引用计数 (Reference Counting)](./reference-counting/) | 零引用自动清理 | CPython, Rust Arc |
| [墓碑 (Tombstone)](./tombstone/) | 标记删除，后台回收 | LevelDB, Cassandra |
| [驻留 (Interning)](./interning/) | 去重不可变值，指针等值判断 | Rust 编译器, CPython |

## 行为型

| 模式 | 一句话描述 | 来源 |
|------|-----------|------|
| [状态机 (State Machine)](./state-machine/) | 显式状态，不可能转换不可表达 | XState, Linux TCP |
| [观察者 (Observer)](./observer/) | 订阅事件，解耦生产消费 | EventEmitter, Redux |
| [迭代器 (Iterator)](./iterator/) | 惰性序列，零中间分配 | Rust, Python |
| [差异/补丁 (Diff/Patch)](./diff-patch/) | 计算两个状态间最小变更 | React, Git |
| [虚函数表 (Vtable)](./vtable/) | 函数指针结构体实现多态 | Linux 内核, CPython |
| [访问者 (Visitor)](./visitor/) | 对树节点分发类型特定回调 | LLVM, Vue |
