---
title: "Pattern: Skip List"
description: "Cấu trúc sắp xếp theo xác suất với tìm/chèn/xoá O(log n) — đơn giản hơn cây cân bằng với hiệu năng tương đương."
difficulty: "advanced"
---

# Pattern: Skip List

<DifficultyBadge />

## Mô tả một câu

Cấu trúc sắp xếp theo xác suất với tìm/chèn/xoá O(log n) — đơn giản hơn cây cân bằng với hiệu năng tương đương.

<DemoBadge />

## Tương tự thực tế

Hệ tàu tốc hành có ga địa phương và ga nhanh. Tuyến nhanh bỏ qua hầu hết các trạm, cho bạn nhảy nhanh về phía trước. Khi gần đích, bạn chuyển sang tuyến địa phương để dừng chính xác. Nhiều cấp tốc hành tăng tốc tìm kiếm xa.

## Ý tưởng cốt lõi

Skip list là linked list đa cấp nơi mỗi cấp bỏ qua nhiều phần tử hơn. Cấp dưới cùng là linked list sắp xếp thường. Các cấp cao đóng vai "làn tốc hành" cho phép hành vi giống tìm nhị phân. Mỗi node được thăng cấp ngẫu nhiên với xác suất p (thường 0,5).

```text
  Level 3:  HEAD ─────────────────────────────── 30 ─ NIL
              │                                  │
  Level 2:  HEAD ─────── 10 ──────────────────── 30 ─ NIL
              │           │                      │
  Level 1:  HEAD ── 5 ── 10 ──── 20 ──────────── 30 ─ NIL
              │     │     │       │              │
  Level 0:  HEAD  3  5  7  10  15  20  25  30 ─ NIL
              │   │  │  │   │   │   │   │   │
              ▼   ▼  ▼  ▼   ▼   ▼   ▼   ▼   ▼

  Search(15): L3→30(xa)↓ L2→10→30(xa)↓ L1→20(xa)↓ L0→15 ✓
```

| Thuộc tính | Giá trị |
|----------|-------|
| Tìm | O(log n) trung bình |
| Chèn | O(log n) trung bình |
| Xoá | O(log n) trung bình |
| Bộ nhớ | O(n) kỳ vọng |
| Lợi thế | Đơn giản hơn red-black/AVL, có biến thể lock-free |

**Thử ngay** — chèn giá trị và tìm để xem làn tốc hành tăng tốc duyệt:

<SkipListViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| Redis | [t_zset.c#L70-L130](https://github.com/redis/redis/blob/df63a65d4d4ee33ae67e9f101885074febe0bccb/src/t_zset.c#L70-L130) | `zskiplist` / `zskiplistNode` — sorted set Redis dùng skip list (không phải cây cân bằng) cho truy vấn khoảng O(log n). `zslInsert` tạo node với cấp ngẫu nhiên. Antirez chọn vì đơn giản và thân thiện cache. |
| LevelDB | [skiplist.h#L40-L90](https://github.com/google/leveldb/blob/7ee830d02b623e8ffe0b95d59a74db1e58da04c5/db/skiplist.h#L40-L90) | Template class `SkipList` — dùng làm cấu trúc sắp xếp trong bộ nhớ (MemTable) cho LevelDB. `Insert` và `Contains` với compare-and-swap cho đọc đồng thời. Nền tảng kiến trúc LSM-tree. |

## Triển khai

::: code-group

```typescript [TypeScript]
class SkipNode {
  forward: (SkipNode | null)[];
  constructor(public key: number, public value: string, level: number) {
    this.forward = new Array(level + 1).fill(null);
  }
}

class SkipList {
  private maxLevel = 16;
  private level = 0;
  private header = new SkipNode(-Infinity, '', 16);

  private randomLevel(): number {
    let lvl = 0;
    while (lvl < this.maxLevel && Math.random() < 0.5) lvl++;
    return lvl;
  }

  insert(key: number, value: string): void {
    const update: (SkipNode | null)[] = new Array(this.maxLevel + 1).fill(null);
    let cur = this.header;
    for (let i = this.level; i >= 0; i--) {
      while (cur.forward[i] && cur.forward[i]!.key < key) cur = cur.forward[i]!;
      update[i] = cur;
    }
    if (cur.forward[0]?.key === key) { cur.forward[0]!.value = value; return; }
    const newLvl = this.randomLevel();
    if (newLvl > this.level) {
      for (let i = this.level + 1; i <= newLvl; i++) update[i] = this.header;
      this.level = newLvl;
    }
    const node = new SkipNode(key, value, newLvl);
    for (let i = 0; i <= newLvl; i++) {
      node.forward[i] = update[i]!.forward[i];
      update[i]!.forward[i] = node;
    }
  }

  search(key: number): string | undefined {
    let cur = this.header;
    for (let i = this.level; i >= 0; i--) {
      while (cur.forward[i] && cur.forward[i]!.key < key) cur = cur.forward[i]!;
    }
    return cur.forward[0]?.key === key ? cur.forward[0]!.value : undefined;
  }
}
```

```rust [Rust]
const MAX_LEVEL: usize = 4;

struct SkipNode {
    key: i64,
    value: String,
    forward: Vec<Option<usize>>,
}

pub struct SkipList {
    nodes: Vec<SkipNode>,
    head: usize,
    level: usize,
    seed: u64,
}

impl SkipList {
    pub fn new() -> Self {
        let head = SkipNode { key: i64::MIN, value: String::new(), forward: vec![None; MAX_LEVEL] };
        SkipList { nodes: vec![head], head: 0, level: 0, seed: 42 }
    }

    fn random_level(&mut self) -> usize {
        let mut lvl = 0;
        while lvl < MAX_LEVEL - 1 {
            self.seed ^= self.seed << 13;
            self.seed ^= self.seed >> 7;
            self.seed ^= self.seed << 17;
            if self.seed % 2 == 0 { lvl += 1; } else { break; }
        }
        lvl
    }

    pub fn insert(&mut self, key: i64, value: &str) {
        let mut update = [0usize; MAX_LEVEL];
        let mut cur = self.head;
        for i in (0..=self.level).rev() {
            while let Some(nx) = self.nodes[cur].forward[i] {
                if self.nodes[nx].key < key { cur = nx; } else { break; }
            }
            update[i] = cur;
        }
        if let Some(nx) = self.nodes[cur].forward[0] {
            if self.nodes[nx].key == key {
                self.nodes[nx].value = value.to_string();
                return;
            }
        }
        let lvl = self.random_level();
        if lvl > self.level {
            for i in (self.level + 1)..=lvl { update[i] = self.head; }
            self.level = lvl;
        }
        let idx = self.nodes.len();
        self.nodes.push(SkipNode { key, value: value.to_string(), forward: vec![None; lvl + 1] });
        for i in 0..=lvl {
            self.nodes[idx].forward[i] = self.nodes[update[i]].forward[i];
            self.nodes[update[i]].forward[i] = Some(idx);
        }
    }

    pub fn search(&self, key: i64) -> Option<&str> {
        let mut cur = self.head;
        for i in (0..=self.level).rev() {
            while let Some(nx) = self.nodes[cur].forward[i] {
                if self.nodes[nx].key < key { cur = nx; } else { break; }
            }
        }
        if let Some(nx) = self.nodes[cur].forward[0] {
            if self.nodes[nx].key == key { return Some(&self.nodes[nx].value); }
        }
        None
    }
}
```

```go [Go]
type SkipNode struct {
	key     int
	value   string
	forward []*SkipNode
}

type SkipList struct {
	header   *SkipNode
	level    int
	maxLevel int
}

func NewSkipList() *SkipList {
	header := &SkipNode{forward: make([]*SkipNode, 17)}
	return &SkipList{header: header, maxLevel: 16}
}

func (sl *SkipList) Insert(key int, value string) {
	update := make([]*SkipNode, sl.maxLevel+1)
	cur := sl.header
	for i := sl.level; i >= 0; i-- {
		for cur.forward[i] != nil && cur.forward[i].key < key {
			cur = cur.forward[i]
		}
		update[i] = cur
	}
	if cur.forward[0] != nil && cur.forward[0].key == key {
		cur.forward[0].value = value
		return
	}
	lvl := 0
	for lvl < sl.maxLevel && rand.Float64() < 0.5 {
		lvl++
	}
	if lvl > sl.level {
		for i := sl.level + 1; i <= lvl; i++ {
			update[i] = sl.header
		}
		sl.level = lvl
	}
	node := &SkipNode{key: key, value: value, forward: make([]*SkipNode, lvl+1)}
	for i := 0; i <= lvl; i++ {
		node.forward[i] = update[i].forward[i]
		update[i].forward[i] = node
	}
}

func (sl *SkipList) Search(key int) (string, bool) {
	cur := sl.header
	for i := sl.level; i >= 0; i-- {
		for cur.forward[i] != nil && cur.forward[i].key < key {
			cur = cur.forward[i]
		}
	}
	if cur.forward[0] != nil && cur.forward[0].key == key {
		return cur.forward[0].value, true
	}
	return "", false
}
```

```python [Python]
import random

class SkipNode:
    def __init__(self, key: int, value: str, level: int):
        self.key = key
        self.value = value
        self.forward: list[SkipNode | None] = [None] * (level + 1)

class SkipList:
    def __init__(self, max_level: int = 16, p: float = 0.5):
        self.max_level = max_level
        self.p = p
        self.level = 0
        self.header = SkipNode(-1, '', max_level)

    def _random_level(self) -> int:
        lvl = 0
        while lvl < self.max_level and random.random() < self.p:
            lvl += 1
        return lvl

    def insert(self, key: int, value: str) -> None:
        update = [self.header] * (self.max_level + 1)
        cur = self.header
        for i in range(self.level, -1, -1):
            while cur.forward[i] and cur.forward[i].key < key:
                cur = cur.forward[i]
            update[i] = cur
        if cur.forward[0] and cur.forward[0].key == key:
            cur.forward[0].value = value
            return
        lvl = self._random_level()
        if lvl > self.level:
            for i in range(self.level + 1, lvl + 1):
                update[i] = self.header
            self.level = lvl
        node = SkipNode(key, value, lvl)
        for i in range(lvl + 1):
            node.forward[i] = update[i].forward[i]
            update[i].forward[i] = node

    def search(self, key: int) -> str | None:
        cur = self.header
        for i in range(self.level, -1, -1):
            while cur.forward[i] and cur.forward[i].key < key:
                cur = cur.forward[i]
        if cur.forward[0] and cur.forward[0].key == key:
            return cur.forward[0].value
        return None
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai skip list với insert/search/delete | `exercises/typescript/skip-list/01-basic.test.ts` |
| Trung bình | Skip list với truy vấn khoảng | `exercises/typescript/skip-list/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/skip_list/mod.rs` · Go `exercises/go/skip_list/skip_list_test.go` · Python `exercises/python/skip_list/test_skip_list.py`

## Khi nào nên dùng

- **Lưu trữ sắp xếp trong bộ nhớ** — khi cần lặp đã sắp xếp + tra cứu điểm nhanh (sorted set Redis)
- **Cấu trúc dữ liệu đồng thời** — skip list lock-free đơn giản hơn cây cân bằng lock-free
- **Memtable database** — buffer ghi trong bộ nhớ trước khi flush ra đĩa (LevelDB, RocksDB)
- **Truy vấn khoảng** — quét khoảng hiệu quả trên dữ liệu đã sắp xếp

## Khi nào KHÔNG nên dùng

- **Tra cứu key-value thuần** — hash map O(1) trung bình so với skip list O(log n)
- **Cần hiệu năng xác định** — skip list bảo đảm theo xác suất, không phải worst-case
- **Eo hẹp bộ nhớ** — mảng con trỏ forward tốn bộ nhớ hơn cây cân bằng
- **Lưu trữ bền vững** — B-tree tối ưu hơn cho mẫu I/O đĩa

## Thêm các ứng dụng production

- [RocksDB](https://github.com/facebook/rocksdb/blob/7affaee1c49ebc80cb213ad86fe7d2a3ad447da2/memtable/inlineskiplist.h) — `InlineSkipList` cho MemTable đồng thời
- [CockroachDB](https://github.com/cockroachdb/cockroach) — memtable nền skip list cho storage engine Pebble
- [Java ConcurrentSkipListMap](https://github.com/openjdk/jdk) — map sắp xếp lock-free trong JDK
- [FoundationDB](https://github.com/apple/foundationdb) — skip list cho dữ liệu sắp xếp trong bộ nhớ

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [LSM Tree (Log-Structured Merge Tree)](/patterns/lsm-tree/) | LSM tree dùng skip list làm buffer sắp xếp trong bộ nhớ (memtable) |
| [B+ Tree](/patterns/b-plus-tree/) | B+ tree đảm bảo O(log n); skip list đạt nó theo xác suất với code đơn giản hơn |
| [Bloom Filter](/patterns/bloom-filter/) | Cả hai theo xác suất — bloom filter cho thành viên, skip list cho thứ tự |
| [Free List](/patterns/free-list/) | Node skip list cần quản lý cấp phát; free list cung cấp cấp phát O(1) cho node kích thước cố định |
| [Merge Iterator](/patterns/merge-iterator/) | Merge iterator kết hợp output sắp xếp từ nhiều cấp hoặc instance skip list |
| [Trie (Prefix Tree)](/patterns/trie/) | Cả hai cung cấp duyệt key có thứ tự — skip list qua cân bằng xác suất, trie qua cấu trúc prefix |

## Câu hỏi thử thách

::: details Câu 1: Skip list dùng `Math.random()` để quyết định cấp thăng node. Đồng nghiệp lập luận điều này làm hiệu năng skip list "không tin cậy" vì chuỗi random xấu có thể tạo tìm O(n). Đây có phải lo ngại thực tế trong production không?
**Trả lời:** Về lý thuyết có, nhưng thực tế xác suất cực thấp — tương đương hash table thoái hoá O(n) do va chạm.

Với xác suất thăng p=0,5, cơ hội một node đạt cấp k là (1/2)^k. Cấp tối đa kỳ vọng cho n phần tử là O(log n). Để skip list thoái hoá thành O(n), một phần lớn node phải chỉ ở cấp 0 — sự kiện có xác suất gần 0 đến mức thực tế bất khả. Redis chọn skip list thay red-black tree vì lý do này: đảm bảo trường hợp trung bình đủ mạnh, và triển khai đơn giản hơn nhiều. LevelDB dùng skip list cùng lý do.
:::

::: details Câu 2: Redis dùng skip list (không phải red-black tree hay B-tree) cho sorted set. Cả skip list và BST cân bằng đều cho thao tác O(log n). Cái gì làm skip list ưu tiên cho use case Redis?
**Trả lời:** Skip list đơn giản hơn để triển khai đúng, hỗ trợ truy vấn khoảng hiệu quả qua con trỏ forward, và dễ làm lock-free cho truy cập đồng thời.

Trong BST cân bằng, truy vấn khoảng cần duyệt in-order nhảy giữa con trỏ cha và con. Trong skip list, sau khi tìm được điểm bắt đầu khoảng ở cấp 0, bạn đơn giản theo con trỏ forward — tuần tự và thân thiện cache. Thêm nữa, thuật toán skip list lock-free (dùng trong LevelDB và ConcurrentSkipListMap) đã được hiểu rõ, trong khi thuật toán cây cân bằng lock-free nổi tiếng phức tạp. Antirez (cha đẻ Redis) cũng dẫn ra sự đơn giản triển khai: code chèn/xoá skip list đơn giản so với xoay red-black tree.
:::

::: details Câu 3: Skip list LevelDB hỗ trợ đọc đồng thời không lock nhưng yêu cầu đồng bộ bên ngoài cho ghi. Sao không làm ghi lock-free luôn?
**Trả lời:** LevelDB chỉ có một thread ghi (writer memtable), nên ghi lock-free thêm phức tạp không lợi ích — ràng buộc thiết kế là đọc đồng thời, không phải ghi đồng thời.

Kiến trúc LSM-tree của LevelDB dồn mọi ghi qua một WAL duy nhất rồi vào memtable. Vì chỉ có một writer, mutex đơn giản và không tranh chấp. Skip list dùng thao tác atomic cho con trỏ forward để writer duy nhất và nhiều reader thread có thể hoạt động đồng thời không cần read lock. Đây là insight SWMR (single-writer, multiple-reader): tối ưu cho mẫu concurrency thực tế, không phải trường hợp tổng quát.
:::

::: details Câu 4: Bạn đang triển khai skip list cho leaderboard cần top-100 player theo điểm. Cách ngây thơ lặp từ head cấp 0. Đồng nghiệp nói "chỉ cần duy trì con trỏ đến tail cho lặp ngược." Tại sao không dễ như doubly-linked list?
**Trả lời:** Skip list vốn là cấu trúc một chiều. Thêm con trỏ ngược ở mọi cấp gấp đôi số con trỏ và làm phức tạp chèn/xoá, mất lợi thế đơn giản so với cây cân bằng.

Trong doubly-linked list, duy trì con trỏ tail và lặp ngược dễ dàng. Trong skip list, bạn cần con trỏ ngược ở mọi cấp để duyệt ngược O(log n) — nếu không rơi về O(n) ở cấp 0. Điều này biến skip list thành skip list hai chiều, phức tạp hơn đáng kể. Giải pháp thực tế cho truy vấn "top-K" là lưu điểm đảo dấu (hoặc dùng comparator ngược) để điểm cao nhất sắp trước, rồi lặp tiến từ head. Sorted set Redis dùng cách này với `ZREVRANGE` bằng cách đi con trỏ forward trên skip list hỗ trợ cả hai hướng chỉ ở cấp 0.
:::
