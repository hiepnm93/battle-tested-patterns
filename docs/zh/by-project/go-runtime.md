# Go 中的模式

Go 的运行时和标准库展示了干净、实用的模式实现。

| 模式 | Go 中的位置 | 作用 |
|------|------------|------|
| [协作调度](/zh/patterns/cooperative-scheduling/) | `runtime/proc.go` | 带协作抢占点的 goroutine 调度 |
| [位掩码](/zh/patterns/bitmask/) | `os/types.go` | `FileMode` — 通过 `iota` 类型常量实现的 Unix 权限标志 |
| [对象池](/zh/patterns/object-pool/) | `sync/pool.go` | `sync.Pool` — per-P 本地池，无锁快速路径，广泛用于 `fmt`、`encoding/json` |
| [工作窃取](/zh/patterns/work-stealing/) | `runtime/proc.go` | `stealWork` — goroutine 调度器通过 `runqsteal`/`runqgrab` 从其他 P 的运行队列窃取 |
| [空闲链表](/zh/patterns/free-list/) | `runtime/mfixalloc.go` | `fixalloc` — 固定大小空闲链表分配器，侵入式 `mlink` 节点 |
| [LRU 缓存](/zh/patterns/lru-cache/) | groupcache `lru/lru.go` | `Cache` 结构体，双向链表 + 哈希表，Brad Fitzpatrick 作品 |
| [一致性哈希](/zh/patterns/consistent-hashing/) | groupcache `consistenthash.go` | 带虚拟节点的哈希环，用于分布式缓存 |
| [限流器](/zh/patterns/rate-limiter/) | `x/time/rate` | 扩展标准库中的令牌桶限流器 |

## 延伸阅读

- [Go 源码 (GitHub)](https://github.com/golang/go)
- [Go Runtime 包文档](https://pkg.go.dev/runtime)
