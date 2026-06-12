---
title: "Pattern: Tombstone / Xoá trì hoãn"
description: "Đánh dấu entry đã xoá bằng marker tombstone thay vì gỡ chúng — process nền thu hồi không gian sau."
difficulty: "beginner"
---

# Pattern: Tombstone / Xoá trì hoãn

<DifficultyBadge />

## Mô tả một câu

Đánh dấu entry đã xoá bằng marker tombstone thay vì gỡ chúng — process nền thu hồi không gian sau.

<DemoBadge />

## Tương tự thực tế

Sách thư viện được đánh dấu 'rút khỏi sử dụng' bằng sticker nhưng vẫn để trên kệ. Người mượn thấy không còn dùng được, và thủ thư thu sách rút khỏi sử dụng theo lô khi dọn kệ hàng tháng.

## Ý tưởng cốt lõi

Thay vì xoá dữ liệu ngay, ghi một bản ghi "tombstone" đặc biệt che bản gốc. Đọc kiểm tra tombstone và xử lý entry được đánh dấu như đã xoá. Process compaction nền sau đó thu hồi không gian bằng cách xoá vật lý cả tombstone và dữ liệu bị che. Điều này tách đường nhanh (đánh dấu đã xoá) khỏi đường chậm (thu hồi không gian).

```text
  Đường ghi:                       Đường đọc:

  delete("B")                      get("B")
      │                                │
      ▼                                ▼
  ┌──────────┐                   ┌───────────┐
  │ Log/SST  │                   │  Lookup   │
  ├──────────┤                   ├───────────┤
  │ A = "v1" │                   │ Tìm thấy: │
  │ B = tomb │ ◄── tombstone     │ B = tomb  │──► trả NOT FOUND
  │ C = "v3" │                   │           │
  └──────────┘                   └───────────┘

  Compaction (nền):
  ┌──────────┐      ┌──────────┐
  │ A = "v1" │      │ A = "v1" │
  │ B = "v2" │ ──►  │ C = "v3" │  B bị gỡ (tombstone + gốc)
  │ B = tomb │      └──────────┘
  │ C = "v3" │
  └──────────┘
```

| Thuộc tính | Giá trị |
|----------|-------|
| Delete | O(1) — chỉ append marker tombstone |
| Thu hồi không gian | Hoãn — compaction nền |
| Overhead đọc | Phải check tombstone |
| Consistency | Tombstone phải lan tới mọi replica trước khi gỡ |

**Thử ngay** — ghi entry, xoá bằng tombstone và compact để thu hồi không gian:

<TombstoneViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| LevelDB | [dbformat.h#L39-L43](https://github.com/google/leveldb/blob/7ee830d02b623e8ffe0b95d59a74db1e58da04c5/db/dbformat.h#L39-L43) | `kTypeDeletion` (giá trị 0x0) đánh dấu key đã xoá trong WAL và SSTable. Khi compaction (`DoCompactionWork` trong db_impl.cc), tombstone bị bỏ khi không snapshot cũ nào tham chiếu key. |
| Apache Cassandra | [DeletionTime.java#L37-L99](https://github.com/apache/cassandra/blob/3831d8265d748c21c0fef9d31d4777b134b20637/src/java/org/apache/cassandra/db/DeletionTime.java#L37-L99) | Class `DeletionTime` đại diện tombstone với timestamp `markedForDeleteAt`. `isLive()` (L99) check status tombstone khi đọc. Tombstone lan qua replica trong `gc_grace_seconds` (mặc định 10 ngày, tham chiếu ở L89) trước khi compaction xoá chúng. |

## Triển khai

::: code-group

```typescript [TypeScript]
interface Entry<V> {
  value: V | null;
  deleted: boolean;
  timestamp: number;
}

class TombstoneStore<V> {
  private store = new Map<string, Entry<V>>();
  private tombstoneCount = 0;

  put(key: string, value: V): void {
    this.store.set(key, {
      value,
      deleted: false,
      timestamp: Date.now(),
    });
  }

  get(key: string): V | undefined {
    const entry = this.store.get(key);
    if (!entry || entry.deleted) return undefined;
    return entry.value!;
  }

  delete(key: string): boolean {
    const entry = this.store.get(key);
    if (!entry || entry.deleted) return false;
    entry.deleted = true;
    entry.value = null;
    entry.timestamp = Date.now();
    this.tombstoneCount++;
    return true;
  }

  /** Compact: xoá tombstone cũ hơn maxAge ms. */
  compact(maxAge: number): number {
    const cutoff = Date.now() - maxAge;
    let removed = 0;
    for (const [key, entry] of this.store) {
      if (entry.deleted && entry.timestamp < cutoff) {
        this.store.delete(key);
        removed++;
        this.tombstoneCount--;
      }
    }
    return removed;
  }

  get size(): number {
    let count = 0;
    for (const entry of this.store.values()) {
      if (!entry.deleted) count++;
    }
    return count;
  }

  get pendingTombstones(): number {
    return this.tombstoneCount;
  }
}
```

```rust [Rust]
use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};

struct Entry {
    value: Option<String>,
    deleted: bool,
    timestamp: u128,
}

pub struct TombstoneStore {
    store: HashMap<String, Entry>,
    tombstone_count: usize,
}

impl TombstoneStore {
    pub fn new() -> Self {
        TombstoneStore { store: HashMap::new(), tombstone_count: 0 }
    }

    fn now_ms() -> u128 {
        SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_millis()
    }

    pub fn put(&mut self, key: &str, value: &str) {
        self.store.insert(key.to_string(), Entry {
            value: Some(value.to_string()),
            deleted: false,
            timestamp: Self::now_ms(),
        });
    }

    pub fn get(&self, key: &str) -> Option<&str> {
        self.store.get(key)
            .filter(|e| !e.deleted)
            .and_then(|e| e.value.as_deref())
    }

    pub fn delete(&mut self, key: &str) -> bool {
        if let Some(entry) = self.store.get_mut(key) {
            if !entry.deleted {
                entry.deleted = true;
                entry.value = None;
                entry.timestamp = Self::now_ms();
                self.tombstone_count += 1;
                return true;
            }
        }
        false
    }

    pub fn compact(&mut self, max_age_ms: u128) -> usize {
        let cutoff = Self::now_ms().saturating_sub(max_age_ms);
        let to_remove: Vec<String> = self.store.iter()
            .filter(|(_, e)| e.deleted && e.timestamp < cutoff)
            .map(|(k, _)| k.clone())
            .collect();
        let count = to_remove.len();
        for key in to_remove {
            self.store.remove(&key);
        }
        self.tombstone_count -= count;
        count
    }

    pub fn size(&self) -> usize {
        self.store.values().filter(|e| !e.deleted).count()
    }
}
```

```go [Go]
type Entry struct {
	Value     string
	Deleted   bool
	Timestamp int64
}

type TombstoneStore struct {
	store          map[string]*Entry
	tombstoneCount int
}

func NewTombstoneStore() *TombstoneStore {
	return &TombstoneStore{store: make(map[string]*Entry)}
}

func (s *TombstoneStore) Put(key, value string) {
	s.store[key] = &Entry{Value: value, Deleted: false, Timestamp: time.Now().UnixMilli()}
}

func (s *TombstoneStore) Get(key string) (string, bool) {
	entry, ok := s.store[key]
	if !ok || entry.Deleted {
		return "", false
	}
	return entry.Value, true
}

func (s *TombstoneStore) Delete(key string) bool {
	entry, ok := s.store[key]
	if !ok || entry.Deleted {
		return false
	}
	entry.Deleted = true
	entry.Value = ""
	entry.Timestamp = time.Now().UnixMilli()
	s.tombstoneCount++
	return true
}

func (s *TombstoneStore) Compact(maxAgeMs int64) int {
	cutoff := time.Now().UnixMilli() - maxAgeMs
	removed := 0
	for key, entry := range s.store {
		if entry.Deleted && entry.Timestamp < cutoff {
			delete(s.store, key)
			removed++
			s.tombstoneCount--
		}
	}
	return removed
}

func (s *TombstoneStore) Size() int {
	count := 0
	for _, entry := range s.store {
		if !entry.Deleted {
			count++
		}
	}
	return count
}
```

```python [Python]
import time

class TombstoneStore:
    def __init__(self):
        self._store: dict[str, dict] = {}
        self._tombstone_count = 0

    def put(self, key: str, value: str) -> None:
        self._store[key] = {
            "value": value,
            "deleted": False,
            "timestamp": time.time() * 1000,
        }

    def get(self, key: str) -> str | None:
        entry = self._store.get(key)
        if entry is None or entry["deleted"]:
            return None
        return entry["value"]

    def delete(self, key: str) -> bool:
        entry = self._store.get(key)
        if entry is None or entry["deleted"]:
            return False
        entry["deleted"] = True
        entry["value"] = None
        entry["timestamp"] = time.time() * 1000
        self._tombstone_count += 1
        return True

    def compact(self, max_age_ms: float) -> int:
        cutoff = time.time() * 1000 - max_age_ms
        to_remove = [
            k for k, e in self._store.items()
            if e["deleted"] and e["timestamp"] < cutoff
        ]
        for k in to_remove:
            del self._store[k]
        self._tombstone_count -= len(to_remove)
        return len(to_remove)

    @property
    def size(self) -> int:
        return sum(1 for e in self._store.values() if not e["deleted"])

    @property
    def pending_tombstones(self) -> int:
        return self._tombstone_count
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai kho key-value với xoá tombstone | `exercises/typescript/tombstone/01-basic.test.ts` |
| Trung bình | Thêm compaction theo thời gian và metric tombstone | `exercises/typescript/tombstone/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/tombstone/mod.rs` · Go `exercises/go/tombstone/tombstone_test.go` · Python `exercises/python/tombstone/test_tombstone.py`

## Khi nào nên dùng

- **Storage engine LSM-tree** — LevelDB, RocksDB, Cassandra append tombstone; compaction dọn dẹp
- **Database phân tán** — tombstone lan ý định xoá qua replica trước khi gỡ vật lý
- **Soft delete trong app** — đánh dấu record đã xoá nhưng giữ audit trail; purge sau thời gian giữ
- **Log bất biến/append-only** — không sửa được entry hiện có, nên xoá cần record bóng
- **Cấu trúc dữ liệu đồng thời** — đánh dấu node đã xoá để tránh thao tác con trỏ không an toàn khi đọc đồng thời

## Khi nào KHÔNG nên dùng

- **Lưu trữ mutable in-place** — nếu có thể trực tiếp xoá entry (hash table, mảng mutable), cứ xoá
- **Hệ thống eo hẹp bộ nhớ** — tombstone tiêu tốn không gian tới compaction; nếu không gian eo, xoá ngay tốt hơn
- **Không có xử lý nền** — compaction cần thread/process nền; nếu không có, tombstone tích luỹ mãi

## Thêm các ứng dụng production

- [RocksDB](https://github.com/facebook/rocksdb) — tombstone `kTypeDeletion` và `kTypeSingleDeletion` với trigger compaction điều chỉnh được
- [Apache HBase](https://github.com/apache/hbase) — marker xoá lan tới mọi store file khi major compaction
- [CockroachDB](https://github.com/cockroachdb/cockroach) — tombstone MVCC cho xoá khoảng, GC bởi job nền
- [Elasticsearch](https://github.com/elastic/elasticsearch) — doc soft-delete đánh dấu cờ `_deleted`, purge khi merge segment

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [LSM Tree (Log-Structured Merge Tree)](/patterns/lsm-tree/) | LSM tree dùng tombstone rộng rãi — chúng được dọn khi compaction |
| [MVCC (Multi-Version Concurrency Control)](/patterns/mvcc/) | MVCC đánh dấu phiên bản cũ bằng tombstone cho garbage collection |
| [Free List](/patterns/free-list/) | Sau dọn tombstone, slot trống có thể quản lý bằng free list |
| [LRU Cache](/patterns/lru-cache/) | LRU cache dùng tombstone đánh dấu entry đã xoá trong kịch bản phân tán |
| [Reference Counting](/patterns/reference-counting/) | Reference counting xác định khi nào object tombstone có thể an toàn thu hồi |

## Câu hỏi thử thách

::: details Câu 1: Cluster Cassandra với gc_grace_seconds=10 ngày. Node C sập 15 ngày. Chuyện gì khi C online trở lại?
**Trả lời:** Node C có thể hồi sinh dữ liệu đã xoá.

Trong khi C sập, các node khác đã xoá một số key và tombstone của chúng hết hạn (gc_grace_seconds=10 ngày). Khi C quay lại, nó vẫn có dữ liệu gốc không có tombstone. Khi anti-entropy repair, dữ liệu "live" của C thắng vì không có tombstone để mâu thuẫn. Dữ liệu đã xoá xuất hiện lại qua cluster.

Sửa: Chạy `nodetool repair` trước khi gc_grace_seconds hết, hoặc tăng gc_grace_seconds vượt thời gian downtime tối đa kỳ vọng.
:::

::: details Câu 2: Database LSM-tree của bạn có vấn đề "tích luỹ tombstone" — đọc chậm dần. Tại sao?
**Trả lời:** Tombstone phải được check khi đọc.

Khi bạn đọc một key, database phải quét từ SSTable mới nhất đến cũ nhất. Nếu tìm thấy tombstone, biết key đã xoá — nhưng vẫn phải đọc qua mọi tầng để tìm. Tệ hơn, range scan phải check mọi tombstone trong khoảng để lọc key đã xoá.

Nếu compaction tụt lại hoặc tốc độ xoá cao, tombstone chồng chất qua các tầng. Giải pháp: kích hoạt compaction tích cực hơn trên SSTable nặng tombstone, hoặc dùng "single delete" (RocksDB) huỷ chính xác một put, tránh tombstone bền vững.
:::

::: details Câu 3: Sao bạn không thể xoá tombstone ngay sau khi mọi replica xác nhận xoá?
**Trả lời:** Vì read-repair và anti-entropy.

Ngay cả khi mọi replica hiện-live xác nhận xoá, một replica tạm-offline có thể vẫn giữ dữ liệu gốc. Khi nó quay lại, sẽ giới thiệu lại dữ liệu. Tombstone phải tồn tại đủ lâu để "thắng" giải quyết xung đột chống dữ liệu cũ từ replica nào đã sập.

Đó là lý do Cassandra dùng `gc_grace_seconds` — đó là thời gian tối đa kỳ vọng node offline. Tombstone sống ít nhất bằng thời gian đó để đảm bảo nó sống lâu hơn replica cũ nào.
:::

::: details Câu 4: App của bạn thực hiện bulk delete 10 triệu row bằng tombstone. Ngay sau, range scan trên khoảng đã xoá mất 30 giây thay vì 0 giây kỳ vọng. Giải thích vì sao range scan không tức thì, dù mọi row đã "xoá."
**Trả lời:** Tombstone tự nó là dữ liệu phải đọc và đánh giá khi scan.

Range scan không biết key nào đã xoá tới khi đọc mỗi entry và check marker tombstone. Với 10 triệu tombstone, scan đọc 10 triệu entry, đánh giá từng cái và trả 0 kết quả. Đây là vấn đề "tombstone scan" — công việc tỉ lệ với số tombstone, không phải số kết quả live. Giải pháp gồm: range tombstone (RocksDB `DeleteRange` đánh dấu cả khoảng key đã xoá bằng một marker thay vì tombstone mỗi key), compaction ngay khoảng bị ảnh hưởng, hoặc dùng index riêng chỉ theo dõi key live.
:::
