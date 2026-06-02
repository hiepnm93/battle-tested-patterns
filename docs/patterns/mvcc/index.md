# Pattern: MVCC (Multi-Version Concurrency Control)

## One Liner

Keep multiple timestamped versions of each value so readers never block writers — each transaction sees a consistent snapshot without locks.

## Core Idea

MVCC stores every write as a new version tagged with a timestamp or transaction ID. Readers see the latest version visible to their snapshot, ignoring concurrent writes. This eliminates read-write contention: readers never block writers, writers never block readers.

```text
  Key "balance"
  ┌──────────┬──────────┬──────────┬──────────┐
  │ t=100    │ t=200    │ t=300    │ t=400    │
  │ val=500  │ val=450  │ val=600  │ val=580  │
  └──────────┴──────────┴──────────┴──────────┘

  Transaction at t=250:  sees val=450  (latest version ≤ 250)
  Transaction at t=350:  sees val=600  (latest version ≤ 350)
  Both read without blocking the writer at t=400.
```

| Property | Value |
|----------|-------|
| Read-write conflict | **None** — readers see their snapshot, writers append new versions |
| Write-write conflict | Detected at commit time (first-writer-wins or abort) |
| Space overhead | Multiple versions per key (garbage collected via compaction) |
| Isolation level | Snapshot isolation (stronger than read-committed, weaker than serializable) |

## Production Proof

| Project | Source | Usage |
|---------|--------|-------|
| PostgreSQL | [heapam_visibility.c#L917-L1096](https://github.com/postgres/postgres/blob/master/src/backend/access/heap/heapam_visibility.c#L917-L1096) | `HeapTupleSatisfiesMVCC` — the core visibility check. Given a heap tuple and an MVCC snapshot, determines if the tuple is visible to the current transaction. Uses `XidInMVCCSnapshot` to check transaction visibility without contention on `ProcArrayLock`. |
| etcd | [kvstore.go#L53-L135](https://github.com/etcd-io/etcd/blob/main/server/storage/mvcc/kvstore.go#L53-L135) | `store` struct (L53-L82) tracks `currentRev` and `compactMainRev` with a B-tree `kvindex` for multi-version lookups. `NewStore` (L87-L135) initializes the MVCC store and rebuilds the in-memory index from persisted revisions. Powers Kubernetes' configuration backbone. |

## Implementation

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

## Exercises

| Level | Exercise | File |
|-------|----------|------|
| Basic | Implement a multi-version key-value store | `exercises/typescript/mvcc/01-basic.test.ts` |

Run exercises: `pnpm test`

## When to Use

- **Databases** — snapshot isolation for concurrent transactions (PostgreSQL, MySQL InnoDB)
- **Distributed KV stores** — consistent reads without distributed locks (etcd, CockroachDB, TiKV)
- **Time-travel queries** — read data as of a past timestamp
- **Optimistic concurrency** — detect conflicts at commit time instead of locking upfront

## When NOT to Use

- **Single-writer systems** — MVCC overhead is unnecessary if only one writer exists
- **Memory-constrained** — multiple versions per key consume significant storage
- **Write-heavy, no reads** — version management overhead with no reader benefit
- **Strict serializability needed** — MVCC provides snapshot isolation; full serializability requires additional mechanisms (SSI)

## More Production Uses

- [CockroachDB](https://github.com/cockroachdb/cockroach/blob/master/pkg/storage/mvcc.go#L1923-L1962) — `MVCCPut` / `MVCCGet` for distributed SQL
- [MySQL InnoDB](https://github.com/mysql/mysql-server) — undo logs for MVCC row versioning
- [TiKV](https://github.com/tikv/tikv) — Percolator-based distributed MVCC transactions
- [FoundationDB](https://github.com/apple/foundationdb) — multi-version storage layer
