# 模式：MVCC 多版本并发控制

## 一句话

为每个值保留多个带时间戳的版本，读者永远不阻塞写者——每个事务看到一致的快照，无需加锁。

## 核心思想

MVCC 将每次写入存储为带时间戳或事务 ID 的新版本。读者看到对其快照可见的最新版本，忽略并发写入。这消除了读写竞争：读者不阻塞写者，写者不阻塞读者。

```text
  键 "balance"
  ┌──────────┬──────────┬──────────┬──────────┐
  │ t=100    │ t=200    │ t=300    │ t=400    │
  │ val=500  │ val=450  │ val=600  │ val=580  │
  └──────────┴──────────┴──────────┴──────────┘

  事务 t=250:  看到 val=450  (最新版本 ≤ 250)
  事务 t=350:  看到 val=600  (最新版本 ≤ 350)
  两者读取时不阻塞 t=400 的写者。
```

| 属性 | 值 |
|------|------|
| 读写冲突 | **无** — 读者看自己的快照，写者追加新版本 |
| 写写冲突 | 提交时检测（先写者赢或中止） |
| 空间开销 | 每个键多个版本（通过压缩回收） |
| 隔离级别 | 快照隔离（强于读已提交，弱于可串行化） |

## 生产验证

| 项目 | 源码 | 用途 |
|------|------|------|
| PostgreSQL | [heapam_visibility.c#L917-L1096](https://github.com/postgres/postgres/blob/master/src/backend/access/heap/heapam_visibility.c#L917-L1096) | `HeapTupleSatisfiesMVCC` — 核心可见性检查。给定堆元组和 MVCC 快照，判断元组对当前事务是否可见。使用 `XidInMVCCSnapshot` 检查事务可见性，无需争用 `ProcArrayLock`。 |
| etcd | [kvstore.go#L53-L135](https://github.com/etcd-io/etcd/blob/main/server/storage/mvcc/kvstore.go#L53-L135) | `store` 结构体（L53-L82）跟踪 `currentRev` 和 `compactMainRev`，用 B 树 `kvindex` 进行多版本查找。`NewStore`（L87-L135）初始化 MVCC 存储并从持久化修订重建内存索引。驱动 Kubernetes 的配置基础设施。 |

## 实现

::: code-group

```typescript [TypeScript]
interface Version<T> {
  timestamp: number;
  value: T;
  deleted: boolean;
}

class MVCCStore<T> {
  private store = new Map<string, Version<T>[]>();

  put(key: string, value: T, timestamp: number): void {
    if (!this.store.has(key)) this.store.set(key, []);
    this.store.get(key)!.push({ timestamp, value, deleted: false });
  }

  get(key: string, timestamp: number): T | undefined {
    const versions = this.store.get(key);
    if (!versions) return undefined;
    let best: Version<T> | undefined;
    for (const v of versions) {
      if (v.timestamp <= timestamp && (!best || v.timestamp > best.timestamp)) {
        best = v;
      }
    }
    return best && !best.deleted ? best.value : undefined;
  }

  delete(key: string, timestamp: number): void {
    if (!this.store.has(key)) this.store.set(key, []);
    this.store.get(key)!.push({ timestamp, value: undefined as T, deleted: true });
  }
}
```

```go [Go]
type Version struct {
	Timestamp int
	Value     string
	Deleted   bool
}

type MVCCStore struct {
	data map[string][]Version
}

func NewMVCCStore() *MVCCStore {
	return &MVCCStore{data: make(map[string][]Version)}
}

func (s *MVCCStore) Put(key, value string, ts int) {
	s.data[key] = append(s.data[key], Version{Timestamp: ts, Value: value})
}

func (s *MVCCStore) Get(key string, ts int) (string, bool) {
	versions := s.data[key]
	var best *Version
	for i := range versions {
		v := &versions[i]
		if v.Timestamp <= ts && (best == nil || v.Timestamp > best.Timestamp) {
			best = v
		}
	}
	if best == nil || best.Deleted {
		return "", false
	}
	return best.Value, true
}

func (s *MVCCStore) Delete(key string, ts int) {
	s.data[key] = append(s.data[key], Version{Timestamp: ts, Deleted: true})
}
```

```python [Python]
from dataclasses import dataclass
from typing import Any

@dataclass
class Version:
    timestamp: int
    value: Any
    deleted: bool = False

class MVCCStore:
    def __init__(self):
        self._data: dict[str, list[Version]] = {}

    def put(self, key: str, value: Any, timestamp: int) -> None:
        self._data.setdefault(key, []).append(Version(timestamp, value))

    def get(self, key: str, timestamp: int) -> Any:
        versions = self._data.get(key, [])
        best = None
        for v in versions:
            if v.timestamp <= timestamp and (best is None or v.timestamp > best.timestamp):
                best = v
        if best is None or best.deleted:
            return None
        return best.value

    def delete(self, key: str, timestamp: int) -> None:
        self._data.setdefault(key, []).append(Version(timestamp, None, deleted=True))
```

```rust [Rust]
pub struct Version {
    pub timestamp: u64,
    pub value: Option<String>,
}

pub struct MVCCStore {
    data: std::collections::HashMap<String, Vec<Version>>,
}

impl MVCCStore {
    pub fn new() -> Self {
        MVCCStore { data: std::collections::HashMap::new() }
    }

    pub fn put(&mut self, key: &str, value: &str, ts: u64) {
        self.data.entry(key.to_string()).or_default()
            .push(Version { timestamp: ts, value: Some(value.to_string()) });
    }

    pub fn get(&self, key: &str, ts: u64) -> Option<&str> {
        let versions = self.data.get(key)?;
        let mut best: Option<&Version> = None;
        for v in versions {
            if v.timestamp <= ts && best.map_or(true, |b| v.timestamp > b.timestamp) {
                best = Some(v);
            }
        }
        best.and_then(|v| v.value.as_deref())
    }

    pub fn delete(&mut self, key: &str, ts: u64) {
        self.data.entry(key.to_string()).or_default()
            .push(Version { timestamp: ts, value: None });
    }
}
```

:::

## 练习

| 难度 | 练习 | 文件 |
|------|------|------|
| 基础 | 实现多版本键值存储 | `exercises/typescript/mvcc/01-basic.test.ts` |

## 何时使用

- **数据库** — 并发事务的快照隔离（PostgreSQL、MySQL InnoDB）
- **分布式 KV 存储** — 无分布式锁的一致读（etcd、CockroachDB、TiKV）
- **时间旅行查询** — 读取过去某时间点的数据
- **乐观并发** — 提交时检测冲突而非预先加锁

## 何时不用

- **单写者系统** — 只有一个写者时 MVCC 开销不必要
- **内存受限** — 每个键多个版本消耗大量存储
- **只写不读** — 版本管理开销没有读者收益
- **需要严格可串行化** — MVCC 提供快照隔离；完全可串行化需要额外机制（SSI）

## 更多生产案例

- [CockroachDB](https://github.com/cockroachdb/cockroach/blob/master/pkg/storage/mvcc.go#L1923-L1962) — 分布式 SQL 的 `MVCCPut` / `MVCCGet`
- [MySQL InnoDB](https://github.com/mysql/mysql-server) — undo log 实现 MVCC 行版本
- [TiKV](https://github.com/tikv/tikv) — 基于 Percolator 的分布式 MVCC 事务
- [FoundationDB](https://github.com/apple/foundationdb) — 多版本存储层
