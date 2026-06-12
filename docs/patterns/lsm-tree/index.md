---
title: "Pattern: LSM Tree (Log-Structured Merge Tree)"
description: "Đệm ghi trong bộ nhớ, flush thành file đã sắp xếp trên đĩa, gộp file ở background — đánh đổi read amplification lấy ghi nhanh."
difficulty: "advanced"
---

# Pattern: LSM Tree (Log-Structured Merge Tree)

<DifficultyBadge />

## Mô tả một câu

Đệm ghi trong bộ nhớ, flush thành file đã sắp xếp trên đĩa, gộp file ở background — đánh đổi read amplification lấy ghi nhanh.

<DemoBadge />

## Tương tự thực tế

Hệ thống tài liệu nơi bạn ghi note vào tờ sticky trước (memtable), rồi định kỳ xếp chúng vào thư mục đã sắp xếp (SSTable). Theo thời gian, bạn gộp thư mục nhỏ thành thư mục lớn vào giờ vắng (compaction).

## Ý tưởng cốt lõi

LSM tree hấp thụ ghi vào cấu trúc sắp xếp trong bộ nhớ (memtable). Khi memtable đạt ngưỡng kích thước, nó được flush ra đĩa thành sorted run bất biến (SSTable). Compaction nền gộp nhiều sorted run để giới hạn số file và thu hồi không gian từ key đã xoá/ghi đè. Đọc kiểm tra memtable trước, rồi mỗi tầng sorted run.

```text
  Đường ghi                           Đường đọc
  ──────────                          ─────────
  PUT k=v ──►  ┌────────────┐         GET k
               │  Memtable  │ ◄──── 1. Check memtable
               │ (sorted,   │
               │ in-memory) │
               └─────┬──────┘
          flush khi   │
          size > giới hạn
                      ▼
               ┌────────────┐
               │  Level 0   │ ◄──── 2. Check file L0
               │  (SSTables)│
               └─────┬──────┘
          compact     │
          khi đầy     │
                      ▼
               ┌────────────┐
               │  Level 1   │ ◄──── 3. Check file L1
               │  (đã gộp)  │
               └─────┬──────┘
                      ▼
                     ...
```

| Thuộc tính | Giá trị |
|----------|-------|
| Write amplification | O(số tầng) do compaction |
| Read amplification | O(số tầng) worst case |
| Throughput ghi | Rất cao — chỉ I/O tuần tự |
| Space amplification | Trùng lặp tạm thời khi compaction |

**Thử ngay** — ghi key vào memtable, xem nó flush thành SSTable, và compact các tầng:

<LSMTreeViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| LevelDB | [db_impl.cc#L1241-L1368](https://github.com/google/leveldb/blob/7ee830d02b623e8ffe0b95d59a74db1e58da04c5/db/db_impl.cc#L1241-L1368) | `DBImpl::Write` — đường ghi cốt lõi. Batch ghi thành nhóm (L1241-L1288), append vào WAL (L1311), chèn vào memtable (L1337-L1354). Khi memtable vượt `write_buffer_size`, `MakeRoomForWrite` (L1368) kích hoạt flush: memtable hiện tại trở thành bất biến và cái mới được tạo. Compaction nền sau đó gộp file SSTable qua các tầng. |
| RocksDB | [memtable.cc#L458-L534](https://github.com/facebook/rocksdb/blob/7affaee1c49ebc80cb213ad86fe7d2a3ad447da2/db/memtable.cc#L458-L534) | `MemTable::Add` chèn cặp key-value với sequence number và type vào memtable nền skip-list. Memtable là điểm đến đầu tiên cho mọi ghi. Khi đạt `write_buffer_size`, nó được làm bất biến và xếp lịch flush thành file L0 SST. RocksDB mở rộng thiết kế LevelDB với ghi memtable đồng thời, column family và triển khai memtable pluggable. |

## Triển khai

::: code-group

```typescript [TypeScript]
interface KVEntry {
  key: string;
  value: string | null; // null = tombstone (đã xoá)
  seq: number;
}

class Memtable {
  private entries: Map<string, KVEntry> = new Map();
  private _size = 0;

  put(key: string, value: string, seq: number): void {
    this.entries.set(key, { key, value, seq });
    this._size++;
  }

  delete(key: string, seq: number): void {
    this.entries.set(key, { key, value: null, seq });
    this._size++;
  }

  get(key: string): KVEntry | undefined {
    return this.entries.get(key);
  }

  get size(): number { return this._size; }

  flush(): KVEntry[] {
    const sorted = [...this.entries.values()].sort((a, b) => a.key.localeCompare(b.key));
    this.entries.clear();
    this._size = 0;
    return sorted;
  }
}

type SortedRun = KVEntry[];

class LSMTree {
  private memtable = new Memtable();
  private runs: SortedRun[] = []; // L0 sorted run, mới nhất trước
  private seq = 0;
  private readonly flushThreshold: number;
  private readonly maxRuns: number;

  constructor(flushThreshold = 4, maxRuns = 4) {
    this.flushThreshold = flushThreshold;
    this.maxRuns = maxRuns;
  }

  put(key: string, value: string): void {
    this.memtable.put(key, value, this.seq++);
    if (this.memtable.size >= this.flushThreshold) {
      this.flushMemtable();
    }
  }

  delete(key: string): void {
    this.memtable.delete(key, this.seq++);
    if (this.memtable.size >= this.flushThreshold) {
      this.flushMemtable();
    }
  }

  get(key: string): string | undefined {
    // Check memtable trước
    const memEntry = this.memtable.get(key);
    if (memEntry) return memEntry.value ?? undefined;

    // Check sorted run (mới nhất trước)
    for (const run of this.runs) {
      const entry = this.binarySearch(run, key);
      if (entry) return entry.value ?? undefined;
    }
    return undefined;
  }

  private binarySearch(run: SortedRun, key: string): KVEntry | undefined {
    let lo = 0, hi = run.length - 1;
    while (lo <= hi) {
      const mid = (lo + hi) >> 1;
      const cmp = run[mid]!.key.localeCompare(key);
      if (cmp === 0) return run[mid];
      if (cmp < 0) lo = mid + 1;
      else hi = mid - 1;
    }
    return undefined;
  }

  private flushMemtable(): void {
    const run = this.memtable.flush();
    this.runs.unshift(run); // mới nhất trước
    if (this.runs.length > this.maxRuns) {
      this.compact();
    }
  }

  private compact(): void {
    // Gộp mọi run thành một
    const merged = new Map<string, KVEntry>();
    // Xử lý cũ nhất trước để mới nhất thắng
    for (let i = this.runs.length - 1; i >= 0; i--) {
      for (const entry of this.runs[i]!) {
        merged.set(entry.key, entry);
      }
    }
    // Xoá tombstone và sort
    const compacted = [...merged.values()]
      .filter((e) => e.value !== null)
      .sort((a, b) => a.key.localeCompare(b.key));
    this.runs = compacted.length > 0 ? [compacted] : [];
  }

  get runCount(): number { return this.runs.length; }
}
```

```rust [Rust]
use std::collections::BTreeMap;

#[derive(Clone, Debug)]
pub struct KVEntry {
    pub key: String,
    pub value: Option<String>, // None = tombstone
    pub seq: usize,
}

pub struct Memtable {
    entries: BTreeMap<String, KVEntry>,
    size: usize,
}

impl Memtable {
    pub fn new() -> Self {
        Memtable { entries: BTreeMap::new(), size: 0 }
    }

    pub fn put(&mut self, key: &str, value: &str, seq: usize) {
        self.entries.insert(key.to_string(), KVEntry {
            key: key.to_string(), value: Some(value.to_string()), seq,
        });
        self.size += 1;
    }

    pub fn delete(&mut self, key: &str, seq: usize) {
        self.entries.insert(key.to_string(), KVEntry {
            key: key.to_string(), value: None, seq,
        });
        self.size += 1;
    }

    pub fn get(&self, key: &str) -> Option<&KVEntry> {
        self.entries.get(key)
    }

    pub fn size(&self) -> usize { self.size }

    pub fn flush(&mut self) -> Vec<KVEntry> {
        let result: Vec<KVEntry> = self.entries.values().cloned().collect();
        self.entries.clear();
        self.size = 0;
        result
    }
}

pub struct LSMTree {
    memtable: Memtable,
    runs: Vec<Vec<KVEntry>>,
    seq: usize,
    flush_threshold: usize,
    max_runs: usize,
}

impl LSMTree {
    pub fn new(flush_threshold: usize, max_runs: usize) -> Self {
        LSMTree {
            memtable: Memtable::new(),
            runs: Vec::new(),
            seq: 0,
            flush_threshold,
            max_runs,
        }
    }

    pub fn put(&mut self, key: &str, value: &str) {
        self.memtable.put(key, value, self.seq);
        self.seq += 1;
        if self.memtable.size() >= self.flush_threshold {
            self.flush_memtable();
        }
    }

    pub fn delete(&mut self, key: &str) {
        self.memtable.delete(key, self.seq);
        self.seq += 1;
        if self.memtable.size() >= self.flush_threshold {
            self.flush_memtable();
        }
    }

    pub fn get(&self, key: &str) -> Option<&str> {
        if let Some(entry) = self.memtable.get(key) {
            return entry.value.as_deref();
        }
        for run in &self.runs {
            if let Ok(idx) = run.binary_search_by(|e| e.key.as_str().cmp(key)) {
                return run[idx].value.as_deref();
            }
        }
        None
    }

    fn flush_memtable(&mut self) {
        let run = self.memtable.flush();
        self.runs.insert(0, run);
        if self.runs.len() > self.max_runs {
            self.compact();
        }
    }

    fn compact(&mut self) {
        let mut merged = BTreeMap::new();
        for run in self.runs.iter().rev() {
            for entry in run {
                merged.insert(entry.key.clone(), entry.clone());
            }
        }
        let result: Vec<KVEntry> = merged.into_values()
            .filter(|e| e.value.is_some())
            .collect();
        self.runs = if result.is_empty() { vec![] } else { vec![result] };
    }

    pub fn run_count(&self) -> usize { self.runs.len() }
}
```

```go [Go]
package lsm

import "sort"

type KVEntry struct {
	Key   string
	Value *string // nil = tombstone
	Seq   int
}

type Memtable struct {
	entries map[string]KVEntry
	size    int
}

func NewMemtable() *Memtable {
	return &Memtable{entries: make(map[string]KVEntry)}
}

func (m *Memtable) Put(key, value string, seq int) {
	m.entries[key] = KVEntry{Key: key, Value: &value, Seq: seq}
	m.size++
}

func (m *Memtable) Delete(key string, seq int) {
	m.entries[key] = KVEntry{Key: key, Value: nil, Seq: seq}
	m.size++
}

func (m *Memtable) Get(key string) (KVEntry, bool) {
	e, ok := m.entries[key]
	return e, ok
}

func (m *Memtable) Flush() []KVEntry {
	result := make([]KVEntry, 0, len(m.entries))
	for _, e := range m.entries {
		result = append(result, e)
	}
	sort.Slice(result, func(i, j int) bool {
		return result[i].Key < result[j].Key
	})
	m.entries = make(map[string]KVEntry)
	m.size = 0
	return result
}

type LSMTree struct {
	memtable       *Memtable
	runs           [][]KVEntry
	seq            int
	flushThreshold int
	maxRuns        int
}

func NewLSMTree(flushThreshold, maxRuns int) *LSMTree {
	return &LSMTree{
		memtable:       NewMemtable(),
		flushThreshold: flushThreshold,
		maxRuns:        maxRuns,
	}
}

func (t *LSMTree) Put(key, value string) {
	t.memtable.Put(key, value, t.seq)
	t.seq++
	if t.memtable.size >= t.flushThreshold {
		t.flushMemtable()
	}
}

func (t *LSMTree) Delete(key string) {
	t.memtable.Delete(key, t.seq)
	t.seq++
	if t.memtable.size >= t.flushThreshold {
		t.flushMemtable()
	}
}

func (t *LSMTree) Get(key string) (string, bool) {
	if e, ok := t.memtable.Get(key); ok {
		if e.Value == nil {
			return "", false
		}
		return *e.Value, true
	}
	for _, run := range t.runs {
		if e := binarySearch(run, key); e != nil {
			if e.Value == nil {
				return "", false
			}
			return *e.Value, true
		}
	}
	return "", false
}

func binarySearch(run []KVEntry, key string) *KVEntry {
	lo, hi := 0, len(run)-1
	for lo <= hi {
		mid := (lo + hi) / 2
		if run[mid].Key == key {
			return &run[mid]
		}
		if run[mid].Key < key {
			lo = mid + 1
		} else {
			hi = mid - 1
		}
	}
	return nil
}

func (t *LSMTree) flushMemtable() {
	run := t.memtable.Flush()
	t.runs = append([][]KVEntry{run}, t.runs...)
	if len(t.runs) > t.maxRuns {
		t.compact()
	}
}

func (t *LSMTree) compact() {
	merged := make(map[string]KVEntry)
	for i := len(t.runs) - 1; i >= 0; i-- {
		for _, e := range t.runs[i] {
			merged[e.Key] = e
		}
	}
	result := make([]KVEntry, 0)
	for _, e := range merged {
		if e.Value != nil {
			result = append(result, e)
		}
	}
	sort.Slice(result, func(i, j int) bool {
		return result[i].Key < result[j].Key
	})
	if len(result) > 0 {
		t.runs = [][]KVEntry{result}
	} else {
		t.runs = nil
	}
}

func (t *LSMTree) RunCount() int {
	return len(t.runs)
}
```

```python [Python]
from dataclasses import dataclass, field
from bisect import bisect_left

@dataclass
class KVEntry:
    key: str
    value: str | None  # None = tombstone
    seq: int = 0

class Memtable:
    def __init__(self):
        self._entries: dict[str, KVEntry] = {}
        self._size = 0

    def put(self, key: str, value: str, seq: int) -> None:
        self._entries[key] = KVEntry(key=key, value=value, seq=seq)
        self._size += 1

    def delete(self, key: str, seq: int) -> None:
        self._entries[key] = KVEntry(key=key, value=None, seq=seq)
        self._size += 1

    def get(self, key: str) -> KVEntry | None:
        return self._entries.get(key)

    @property
    def size(self) -> int:
        return self._size

    def flush(self) -> list[KVEntry]:
        result = sorted(self._entries.values(), key=lambda e: e.key)
        self._entries.clear()
        self._size = 0
        return result

class LSMTree:
    def __init__(self, flush_threshold: int = 4, max_runs: int = 4):
        self._memtable = Memtable()
        self._runs: list[list[KVEntry]] = []
        self._seq = 0
        self._flush_threshold = flush_threshold
        self._max_runs = max_runs

    def put(self, key: str, value: str) -> None:
        self._memtable.put(key, value, self._seq)
        self._seq += 1
        if self._memtable.size >= self._flush_threshold:
            self._flush()

    def delete(self, key: str) -> None:
        self._memtable.delete(key, self._seq)
        self._seq += 1
        if self._memtable.size >= self._flush_threshold:
            self._flush()

    def get(self, key: str) -> str | None:
        entry = self._memtable.get(key)
        if entry is not None:
            return entry.value

        for run in self._runs:
            entry = self._binary_search(run, key)
            if entry is not None:
                return entry.value
        return None

    def _binary_search(self, run: list[KVEntry], key: str) -> KVEntry | None:
        keys = [e.key for e in run]
        i = bisect_left(keys, key)
        if i < len(run) and run[i].key == key:
            return run[i]
        return None

    def _flush(self) -> None:
        run = self._memtable.flush()
        self._runs.insert(0, run)
        if len(self._runs) > self._max_runs:
            self._compact()

    def _compact(self) -> None:
        merged: dict[str, KVEntry] = {}
        for run in reversed(self._runs):
            for entry in run:
                merged[entry.key] = entry
        result = [e for e in merged.values() if e.value is not None]
        result.sort(key=lambda e: e.key)
        self._runs = [result] if result else []

    @property
    def run_count(self) -> int:
        return len(self._runs)
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Memtable trong bộ nhớ với flush thành sorted run | `exercises/typescript/lsm-tree/01-basic.test.ts` |
| Trung bình | Compaction đa tầng với gộp kích hoạt theo size | `exercises/typescript/lsm-tree/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/lsm_tree/mod.rs` · Go `exercises/go/lsm_tree/lsm_tree_test.go` · Python `exercises/python/lsm_tree/test_lsm_tree.py`

## Khi nào nên dùng

- **Tải nặng ghi** — log, dữ liệu time-series, luồng event
- **Kho key-value** — LevelDB, RocksDB, Cassandra, HBase
- **Database nhúng** — tiết kiệm không gian, đơn giản triển khai
- **Dữ liệu phần lớn append** — dữ liệu sensor IoT, event analytics
- **Lưu trữ tối ưu SSD** — ghi tuần tự tối đa hoá tuổi thọ SSD

## Khi nào KHÔNG nên dùng

- **Tải nặng đọc** — đọc có thể check nhiều tầng; dùng B+ tree cho đọc nhanh
- **Dataset nhỏ** — overhead LSM (compaction, nhiều file) không đáng cho dữ liệu vừa B+ tree
- **Range scan với độ trễ nghiêm ngặt** — compaction có thể gây đỉnh độ trễ
- **Nặng update với đọc điểm** — update lặp tới cùng key tạo write amplification khi compaction

## Thêm các ứng dụng production

- [Apache Cassandra](https://github.com/apache/cassandra) — database NoSQL phân tán nền LSM
- [ScyllaDB](https://github.com/scylladb/scylladb) — store LSM tương thích Cassandra hiệu năng cao
- [BadgerDB](https://github.com/dgraph-io/badger) — kho key-value LSM gốc Go với tách giá trị
- [SQLite LSM extension](https://www.sqlite.org/lsm.html) — backend lưu trữ nền LSM cho SQLite

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Skip List](/patterns/skip-list/) | Skip list phục vụ buffer sắp xếp trong bộ nhớ (memtable) trong LSM tree |
| [Bloom Filter](/patterns/bloom-filter/) | Bloom filter trên mỗi SSTable tránh đọc đĩa không cần khi tra cứu |
| [Merge Iterator (K-Way Merge)](/patterns/merge-iterator/) | Compaction gộp nhiều SSTable đã sắp xếp dùng merge iterator |
| [Write-Ahead Log (WAL)](/patterns/write-ahead-log/) | WAL đảm bảo ghi memtable sống sót crash trước khi flush sang SSTable |
| [Tombstone](/patterns/tombstone/) | LSM tree dùng tombstone đánh dấu xoá được dọn khi compaction |
| [B+ Tree](/patterns/b-plus-tree/) | B+ tree cung cấp index tối ưu đọc; LSM tree tối ưu cho tải nặng ghi |

## Câu hỏi thử thách

::: details Câu 1: LSM tree của bạn có 5 tầng (L0-L4). Đọc key "user:999" không tìm thấy. Có khả năng phải check bao nhiêu file?
**Trả lời:** Tệ nhất, mọi file qua mọi tầng. File L0 có thể chồng, nên check mọi file L0. File L1-L4 không chồng trong tầng, nên check tối đa một file mỗi tầng. Tổng: mọi file L0 + 4 (một mỗi tầng còn lại).

Đây là "read amplification" — đánh đổi cơ bản của LSM tree. Giải pháp: (1) Bloom filter trên mỗi SSTable để bỏ qua file chắc chắn không chứa key (LevelDB/RocksDB làm vậy); (2) giảm thiểu file L0 bằng compact tích cực; (3) dùng index dựa trên prefix để bỏ qua cả tầng. Bloom filter của RocksDB thường giảm đọc xuống 1-2 lần đọc file kể cả với nhiều tầng.
:::

::: details Câu 2: Bạn xoá một key khỏi LSM tree. Key vẫn tồn tại trong SSTable cũ trên đĩa. Không gian có được giải phóng ngay không?
**Trả lời:** Không. Xoá ghi marker tombstone vào memtable. Cặp key-value gốc vẫn trong SSTable cũ tới khi compaction gộp SSTable đó và gặp tombstone, lúc đó cả hai bị bỏ.

Đây là lý do LSM tree có "space amplification." Dữ liệu đã xoá chiếm không gian đĩa tới khi compaction tới. Trường hợp cực đoan (tải nặng xoá), dùng đĩa có thể tạm thời vượt size dữ liệu logic đáng kể. RocksDB giải bằng filter compaction định kỳ và trigger compaction thủ công. Tombstone tự nó cũng chiếm không gian và phải giữ đủ lâu để che mọi bản sao cũ của key qua mọi tầng.
:::

::: details Câu 3: LSM tree của bạn nhận 100K ghi/giây. Compaction không theo kịp — L0 tích luỹ file nhanh hơn gộp. Chuyện gì và sửa thế nào?
**Trả lời:** Write stall. Khi L0 vượt giới hạn file, hệ thống phải throttle hoặc tạm dừng ghi đến tới khi compaction theo kịp. Điều này gây đỉnh độ trễ.

`MakeRoomForWrite` của LevelDB tường minh check số file L0 và ngủ nếu vượt `kL0_SlowdownWritesTrigger` (8 file) hoặc dừng ghi hoàn toàn ở `kL0_StopWritesTrigger` (12 file). Giải pháp: (1) tăng song song compaction (RocksDB hỗ trợ thread compaction đồng thời); (2) dùng leveled compaction thay size-tiered để giới hạn tăng L0; (3) tăng size memtable để flush ít hơn; (4) dùng rate limit ghi để làm mịn burst thay vì đụng dừng cứng.
:::

::: details Câu 4: LevelDB dùng mô hình compaction đơn luồng. RocksDB chuyển sang compaction đa luồng. Vấn đề gì điều này giải, và tạo vấn đề mới gì?
**Trả lời:** Compaction đa luồng giải nút thắt throughput — compaction có thể theo kịp tốc độ ghi cao hơn bằng cách chạy nhiều thao tác gộp song song. Vấn đề mới: compaction đồng thời khoảng key chồng có thể gây xung đột ghi và cần phối hợp cẩn thận.

Với compaction đơn luồng, một merge chậm chặn mọi cái khác — write stall trở nên phổ biến dưới tải cao. Compaction đa luồng cho phép merge L0→L1 và L2→L3 xảy ra đồng thời. Tuy nhiên, hai job compaction chạm cùng khoảng key sẽ sinh output xung đột. RocksDB giải bằng cách theo dõi khoảng key nào đang "khoá" bởi compaction active và chỉ lập lịch job compaction không chồng. Phối hợp này thêm phức tạp nhưng cải thiện đáng kể throughput ghi duy trì.
:::
