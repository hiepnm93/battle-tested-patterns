---
title: "Pattern: B+ Tree"
description: "Cây tự cân bằng với hệ số phân nhánh cao — node nội hướng dẫn, node lá lưu, mọi lá liên kết cho range scan hiệu quả."
difficulty: "advanced"
---

# Pattern: B+ Tree

<DifficultyBadge />

## Mô tả một câu

Cây tự cân bằng với hệ số phân nhánh cao — node nội hướng dẫn, node lá lưu, mọi lá liên kết cho range scan hiệu quả.

<DemoBadge />

## Tương tự thực tế

Catalog thẻ thư viện với nhiều cấp. Ngăn trên cùng ghi 'A-M' và 'N-Z.' Trong 'A-M,' bạn tìm 'A-D', 'E-H', v.v. Bạn cứ thu hẹp tới khi đến thẻ thực, được liên kết để dễ duyệt.

## Ý tưởng cốt lõi

B+ tree tách routing khỏi storage. Node nội chỉ giữ key và con trỏ con để hướng dẫn tìm kiếm xuống cây. Node lá giữ cặp key-value thực và được liên kết, cho phép quét tuần tự hiệu quả. Hệ số phân nhánh cao (hàng trăm key mỗi node) giữ cây nông — thường 3-4 tầng cho hàng tỉ record — giảm thiểu I/O đĩa.

```text
                    ┌──────────────┐
                    │   [30 | 60]  │          Nội (chỉ key)
                    └──┬─────┬──┬──┘
                       │     │  │
          ┌────────────┘     │  └────────────┐
          ▼                  ▼               ▼
     ┌─────────┐      ┌──────────┐     ┌─────────┐
     │[10 | 20]│      │[40 | 50] │     │[70 | 80]│   Nội
     └─┬──┬──┬─┘      └──┬──┬──┬─┘     └─┬──┬──┬─┘
       │  │  │           │  │  │         │  │  │
       ▼  ▼  ▼           ▼  ▼  ▼         ▼  ▼  ▼
     ┌───┬───┬───┬───┬───┬───┬───┬───┬───┐
     │1-9│10-│20-│30-│40-│50-│60-│70-│80-│  Node lá
     │   │ 19│ 29│ 39│ 49│ 59│ 69│ 79│ 99│  (dữ liệu ở đây)
     └─►─┴─►─┴─►─┴─►─┴─►─┴─►─┴─►─┴─►─┴───┘
       Linked list cho range scan ───────►
```

| Thuộc tính | Giá trị |
|----------|-------|
| Tìm kiếm | O(log_B n) — B = hệ số phân nhánh |
| Chèn | O(log_B n) — có thể tách node |
| Range scan | O(log_B n + k) — k = số kết quả |
| Bộ nhớ | O(n) |
| Fan-out | Thường 100-1000 key mỗi node |

**Thử ngay** — chèn key và xem B+ tree tách node để giữ cân bằng:

<BPlusTreeViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| PostgreSQL | [nbtinsert.c#L22-L55](https://github.com/postgres/postgres/blob/e18b0cb7344cb4bd28468f6c0aeeb9b9241d30aa/src/backend/access/nbtree/nbtinsert.c#L22-L55) | B-link tree (biến thể Lehman-Yao của B+ tree). `_bt_doinsert` quản lý chèn đồng thời với right-link giữa anh em. Page nội lưu key + con trỏ con; page lá lưu heap TID và được nối cho index scan qua `_bt_readnextpage`. |
| SQLite | [btreeInt.h#L190-L198](https://github.com/sqlite/sqlite/blob/2cb57d9d4ac7eac3b1d15cfa71511f54817cb3e4/src/btreeInt.h#L190-L198) | Mọi bảng và index nền B+ tree trên page đĩa. Định dạng cell định nghĩa trong `btreeInt.h`: cell nội giữ con trỏ page con + key; cell lá giữ payload đầy đủ. `balance_nonroot()` xử lý tách page khi node tràn. |

## Triển khai

::: code-group

```typescript [TypeScript]
class BPlusLeaf<K, V> {
  keys: K[] = [];
  values: V[] = [];
  next: BPlusLeaf<K, V> | null = null;
}

class BPlusInternal<K> {
  keys: K[] = [];
  children: (BPlusInternal<K> | BPlusLeaf<K, any>)[] = [];
}

type BPlusNode<K, V> = BPlusInternal<K> | BPlusLeaf<K, V>;

class BPlusTree<V> {
  private root: BPlusNode<number, V>;

  constructor(private order: number) {
    this.root = new BPlusLeaf<number, V>();
  }

  search(key: number): V | undefined {
    let node = this.root;
    while (node instanceof BPlusInternal) {
      let i = 0;
      while (i < node.keys.length && key >= node.keys[i]) i++;
      node = node.children[i];
    }
    const leaf = node as BPlusLeaf<number, V>;
    const idx = leaf.keys.indexOf(key);
    return idx >= 0 ? leaf.values[idx] : undefined;
  }

  insert(key: number, value: V): void {
    const result = this.insertNode(this.root, key, value);
    if (result) {
      const newRoot = new BPlusInternal<number>();
      newRoot.keys = [result.key];
      newRoot.children = [this.root, result.node];
      this.root = newRoot;
    }
  }

  rangeQuery(start: number, end: number): V[] {
    let node = this.root;
    while (node instanceof BPlusInternal) {
      let i = 0;
      while (i < node.keys.length && start >= node.keys[i]) i++;
      node = node.children[i];
    }
    const results: V[] = [];
    let leaf: BPlusLeaf<number, V> | null = node as BPlusLeaf<number, V>;
    while (leaf) {
      for (let i = 0; i < leaf.keys.length; i++) {
        if (leaf.keys[i] > end) return results;
        if (leaf.keys[i] >= start) results.push(leaf.values[i]);
      }
      leaf = leaf.next;
    }
    return results;
  }

  private insertNode(
    node: BPlusNode<number, V>,
    key: number,
    value: V,
  ): { key: number; node: BPlusNode<number, V> } | null {
    if (node instanceof BPlusLeaf) {
      let i = 0;
      while (i < node.keys.length && node.keys[i] < key) i++;
      if (i < node.keys.length && node.keys[i] === key) {
        node.values[i] = value;
        return null;
      }
      node.keys.splice(i, 0, key);
      node.values.splice(i, 0, value);
      if (node.keys.length >= this.order) {
        return this.splitLeaf(node);
      }
      return null;
    }
    const internal = node as BPlusInternal<number>;
    let i = 0;
    while (i < internal.keys.length && key >= internal.keys[i]) i++;
    const result = this.insertNode(internal.children[i], key, value);
    if (!result) return null;
    internal.keys.splice(i, 0, result.key);
    internal.children.splice(i + 1, 0, result.node);
    if (internal.keys.length >= this.order) {
      return this.splitInternal(internal);
    }
    return null;
  }

  private splitLeaf(leaf: BPlusLeaf<number, V>) {
    const mid = Math.ceil(leaf.keys.length / 2);
    const newLeaf = new BPlusLeaf<number, V>();
    newLeaf.keys = leaf.keys.splice(mid);
    newLeaf.values = leaf.values.splice(mid);
    newLeaf.next = leaf.next;
    leaf.next = newLeaf;
    return { key: newLeaf.keys[0], node: newLeaf as BPlusNode<number, V> };
  }

  private splitInternal(node: BPlusInternal<number>) {
    const mid = Math.floor(node.keys.length / 2);
    const promoteKey = node.keys[mid];
    const newNode = new BPlusInternal<number>();
    newNode.keys = node.keys.splice(mid + 1);
    newNode.children = node.children.splice(mid + 1);
    node.keys.pop();
    return { key: promoteKey, node: newNode as BPlusNode<number, any> };
  }
}
```

```rust [Rust]
pub struct BPlusTree {
    order: usize,
    root: BPlusNode,
}

enum BPlusNode {
    Leaf(LeafNode),
    Internal(InternalNode),
}

struct LeafNode {
    keys: Vec<i64>,
    values: Vec<String>,
}

struct InternalNode {
    keys: Vec<i64>,
    children: Vec<BPlusNode>,
}

impl BPlusTree {
    pub fn new(order: usize) -> Self {
        BPlusTree {
            order,
            root: BPlusNode::Leaf(LeafNode { keys: vec![], values: vec![] }),
        }
    }

    pub fn search(&self, key: i64) -> Option<&str> {
        let mut node = &self.root;
        loop {
            match node {
                BPlusNode::Internal(n) => {
                    let mut i = 0;
                    while i < n.keys.len() && key >= n.keys[i] { i += 1; }
                    node = &n.children[i];
                }
                BPlusNode::Leaf(leaf) => {
                    for (i, &k) in leaf.keys.iter().enumerate() {
                        if k == key { return Some(&leaf.values[i]); }
                    }
                    return None;
                }
            }
        }
    }

    pub fn insert(&mut self, key: i64, value: String) {
        let order = self.order;
        let root = std::mem::replace(
            &mut self.root,
            BPlusNode::Leaf(LeafNode { keys: vec![], values: vec![] }),
        );
        let (new_root, split) = Self::insert_node(root, key, value, order);
        if let Some((promote_key, right)) = split {
            let left = new_root;
            self.root = BPlusNode::Internal(InternalNode {
                keys: vec![promote_key],
                children: vec![left, right],
            });
        } else {
            self.root = new_root;
        }
    }

    fn insert_node(
        node: BPlusNode, key: i64, value: String, order: usize,
    ) -> (BPlusNode, Option<(i64, BPlusNode)>) {
        match node {
            BPlusNode::Leaf(mut leaf) => {
                let pos = leaf.keys.iter().position(|&k| k >= key);
                match pos {
                    Some(i) if leaf.keys[i] == key => {
                        leaf.values[i] = value;
                        (BPlusNode::Leaf(leaf), None)
                    }
                    Some(i) => {
                        leaf.keys.insert(i, key);
                        leaf.values.insert(i, value);
                        Self::maybe_split_leaf(leaf, order)
                    }
                    None => {
                        leaf.keys.push(key);
                        leaf.values.push(value);
                        Self::maybe_split_leaf(leaf, order)
                    }
                }
            }
            BPlusNode::Internal(mut internal) => {
                let mut i = 0;
                while i < internal.keys.len() && key >= internal.keys[i] { i += 1; }
                let child = internal.children.remove(i);
                let (new_child, split) = Self::insert_node(child, key, value, order);
                internal.children.insert(i, new_child);
                if let Some((promote_key, right)) = split {
                    internal.keys.insert(i, promote_key);
                    internal.children.insert(i + 1, right);
                    if internal.keys.len() >= order {
                        return Self::split_internal(internal);
                    }
                }
                (BPlusNode::Internal(internal), None)
            }
        }
    }

    fn maybe_split_leaf(
        mut leaf: LeafNode, order: usize,
    ) -> (BPlusNode, Option<(i64, BPlusNode)>) {
        if leaf.keys.len() < order {
            return (BPlusNode::Leaf(leaf), None);
        }
        let mid = leaf.keys.len() / 2;
        let new_leaf = LeafNode {
            keys: leaf.keys.split_off(mid),
            values: leaf.values.split_off(mid),
        };
        let promote = new_leaf.keys[0];
        (BPlusNode::Leaf(leaf), Some((promote, BPlusNode::Leaf(new_leaf))))
    }

    fn split_internal(
        mut node: InternalNode,
    ) -> (BPlusNode, Option<(i64, BPlusNode)>) {
        let mid = node.keys.len() / 2;
        let promote = node.keys[mid];
        let right_keys = node.keys.split_off(mid + 1);
        node.keys.pop();
        let right_children = node.children.split_off(mid + 1);
        let right = InternalNode { keys: right_keys, children: right_children };
        (BPlusNode::Internal(node), Some((promote, BPlusNode::Internal(right))))
    }
}
```

```go [Go]
type BPlusTree struct {
	order int
	root  bpNode
}

type bpNode interface {
	isLeaf() bool
}

type bpLeaf struct {
	keys   []int
	values []string
	next   *bpLeaf
}

type bpInternal struct {
	keys     []int
	children []bpNode
}

func (l *bpLeaf) isLeaf() bool     { return true }
func (n *bpInternal) isLeaf() bool  { return false }

func NewBPlusTree(order int) *BPlusTree {
	return &BPlusTree{order: order, root: &bpLeaf{}}
}

func (t *BPlusTree) Search(key int) (string, bool) {
	node := t.root
	for !node.isLeaf() {
		internal := node.(*bpInternal)
		i := 0
		for i < len(internal.keys) && key >= internal.keys[i] {
			i++
		}
		node = internal.children[i]
	}
	leaf := node.(*bpLeaf)
	for i, k := range leaf.keys {
		if k == key {
			return leaf.values[i], true
		}
	}
	return "", false
}

func (t *BPlusTree) RangeQuery(start, end int) []string {
	node := t.root
	for !node.isLeaf() {
		internal := node.(*bpInternal)
		i := 0
		for i < len(internal.keys) && start >= internal.keys[i] {
			i++
		}
		node = internal.children[i]
	}
	var results []string
	leaf := node.(*bpLeaf)
	for leaf != nil {
		for i, k := range leaf.keys {
			if k > end {
				return results
			}
			if k >= start {
				results = append(results, leaf.values[i])
			}
		}
		leaf = leaf.next
	}
	return results
}
```

```python [Python]
class BPlusLeaf:
    def __init__(self):
        self.keys: list[int] = []
        self.values: list[str] = []
        self.next: "BPlusLeaf | None" = None

class BPlusInternal:
    def __init__(self):
        self.keys: list[int] = []
        self.children: list = []

class BPlusTree:
    def __init__(self, order: int):
        self.order = order
        self.root: BPlusLeaf | BPlusInternal = BPlusLeaf()

    def search(self, key: int) -> str | None:
        node = self.root
        while isinstance(node, BPlusInternal):
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        leaf: BPlusLeaf = node
        for i, k in enumerate(leaf.keys):
            if k == key:
                return leaf.values[i]
        return None

    def insert(self, key: int, value: str) -> None:
        result = self._insert(self.root, key, value)
        if result:
            new_root = BPlusInternal()
            new_root.keys = [result[0]]
            new_root.children = [self.root, result[1]]
            self.root = new_root

    def _insert(self, node, key, value):
        if isinstance(node, BPlusLeaf):
            i = 0
            while i < len(node.keys) and node.keys[i] < key:
                i += 1
            if i < len(node.keys) and node.keys[i] == key:
                node.values[i] = value
                return None
            node.keys.insert(i, key)
            node.values.insert(i, value)
            if len(node.keys) >= self.order:
                return self._split_leaf(node)
            return None

        internal: BPlusInternal = node
        i = 0
        while i < len(internal.keys) and key >= internal.keys[i]:
            i += 1
        result = self._insert(internal.children[i], key, value)
        if result is None:
            return None
        internal.keys.insert(i, result[0])
        internal.children.insert(i + 1, result[1])
        if len(internal.keys) >= self.order:
            return self._split_internal(internal)
        return None

    def _split_leaf(self, leaf: BPlusLeaf):
        mid = len(leaf.keys) // 2
        new_leaf = BPlusLeaf()
        new_leaf.keys = leaf.keys[mid:]
        new_leaf.values = leaf.values[mid:]
        leaf.keys = leaf.keys[:mid]
        leaf.values = leaf.values[:mid]
        new_leaf.next = leaf.next
        leaf.next = new_leaf
        return (new_leaf.keys[0], new_leaf)

    def _split_internal(self, node: BPlusInternal):
        mid = len(node.keys) // 2
        promote_key = node.keys[mid]
        new_node = BPlusInternal()
        new_node.keys = node.keys[mid + 1:]
        new_node.children = node.children[mid + 1:]
        node.keys = node.keys[:mid]
        node.children = node.children[:mid + 1]
        return (promote_key, new_node)

    def range_query(self, start: int, end: int) -> list[str]:
        node = self.root
        while isinstance(node, BPlusInternal):
            i = 0
            while i < len(node.keys) and start >= node.keys[i]:
                i += 1
            node = node.children[i]
        results: list[str] = []
        leaf: BPlusLeaf | None = node
        while leaf is not None:
            for i, k in enumerate(leaf.keys):
                if k > end:
                    return results
                if k >= start:
                    results.append(leaf.values[i])
            leaf = leaf.next
        return results
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai B+ tree với insert và search | `exercises/typescript/b-plus-tree/01-basic.test.ts` |
| Trung bình | Thêm range query với duyệt lá liên kết | `exercises/typescript/b-plus-tree/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/b_plus_tree/mod.rs` · Go `exercises/go/b_plus_tree/b_plus_tree_test.go` · Python `exercises/python/b_plus_tree/test_b_plus_tree.py`

## Khi nào nên dùng

- **Index database** — mọi RDBMS dùng B+ tree cho index chính và phụ
- **Filesystem** — NTFS, ext4, Btrfs lưu entry thư mục và metadata trong B+ tree
- **Cần range query** — lá liên kết cho `WHERE x BETWEEN a AND b` hiệu quả
- **Lưu trữ nền đĩa** — fan-out cao giảm thiểu seek đĩa (3-4 tầng cho hàng tỉ row)
- **Lặp có thứ tự** — chuỗi lá cung cấp duyệt đã sắp xếp không cần đi cây

## Khi nào KHÔNG nên dùng

- **Chỉ trong bộ nhớ với dữ liệu nhỏ** — hash map hoặc BST cân bằng đơn giản và nhanh hơn
- **Nặng ghi không đọc** — LSM tree (LevelDB, RocksDB) batch ghi hiệu quả hơn
- **Chỉ tra cứu điểm** — hash index O(1) so với O(log n); bỏ qua overhead cây
- **Tải append-only** — chèn ngẫu nhiên gây tách page; lưu trữ log-structured tránh được

## Thêm các ứng dụng production

- [InnoDB (MySQL)](https://github.com/mysql/mysql-server) — clustered index là B+ tree; index phụ trỏ về nó
- [MongoDB WiredTiger](https://github.com/mongodb/mongo) — engine lưu trữ WiredTiger dùng B+ tree cho index
- [LMDB](https://github.com/LMDB/lmdb) — B+ tree copy-on-write cho lưu trữ memory-mapped an toàn crash
- [Btrfs](https://github.com/torvalds/linux) — filesystem Linux xây hoàn toàn trên B-tree / B+ tree

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Skip List](/patterns/skip-list/) | Lựa chọn theo xác suất đơn giản hơn với hiệu năng O(log n) tương đương |
| [LSM Tree (Log-Structured Merge Tree)](/patterns/lsm-tree/) | LSM tree đệm ghi cho tốc độ; B+ tree tối ưu đọc với cấu trúc cân bằng |
| [Merkle Tree](/patterns/merkle-tree/) | Cả hai là cấu trúc cây — Merkle cho xác minh toàn vẹn, B+ cho lưu trữ có thứ tự |
| [Merge Iterator (K-Way Merge)](/patterns/merge-iterator/) | Range scan B+ tree dùng pattern iterator tương tự merge iterator |
| [Min-Heap / Priority Queue](/patterns/min-heap/) | Cả hai là cấu trúc nền cây — B+ tree tối ưu range query, min-heap tối ưu trích ưu tiên |

## Câu hỏi thử thách

::: details Câu 1: B+ tree với order 100 và 1 tỉ key. Sâu bao nhiêu tầng? Bao nhiêu lần đọc đĩa cho tra cứu điểm?
**Trả lời:** Tối đa 5 tầng.

Mỗi node nội giữ tối đa 99 key và 100 con. Tầng 0 (root): 1 node. Tầng 1: 100 node. Tầng 2: 10.000 node. Tầng 3: 1.000.000 node. Tầng 4 (lá): 100.000.000 node.

100^4 = 10 tỉ > 1 tỉ, nên 5 tầng đủ. Tra cứu điểm đọc một node mỗi tầng = 5 lần đọc đĩa. Thực tế root và các tầng nội trên cùng được cache trong RAM, nên thường 2-3 lần đọc đĩa.
:::

::: details Câu 2: Sao B+ tree CHỈ lưu giá trị ở lá, khác B-tree lưu giá trị ở cả node nội?
**Trả lời:** Hai lý do:

1. **Fan-out cao hơn**: Node nội không có giá trị nhỏ hơn, nên nhiều key vừa mỗi page. Nhiều key mỗi node = cây nông hơn = ít đọc đĩa hơn.
2. **Range scan đơn giản hơn**: Mọi giá trị ở cấp lá liên kết với nhau. Range query đi qua chuỗi lá tuyến tính. Trong B-tree, bạn cần duyệt in-order thăm mọi tầng.

Đánh đổi: tra cứu match chính xác luôn đi tới cấp lá trong B+ tree (không short-circuit ở node nội). Nhưng hệ thống nền đĩa tối ưu cho fan-out, làm B+ tree là lựa chọn phổ quát cho database.
:::

::: details Câu 3: PostgreSQL dùng "B-link tree" thay B+ tree chuẩn. Right-link giải vấn đề gì?
**Trả lời:** Truy cập đồng thời không cần lock toàn cục.

Trong B+ tree chuẩn, một split cần lock parent để chèn con trỏ con mới. Điều này có thể lan lên root, tạo nút thắt. B-link tree của Lehman và Yao thêm con trỏ right-link giữa anh em ở mọi tầng. Reader đáp xuống node giữa lúc split có thể theo right-link tìm anh em mới. Writer chỉ cần lock node đang split và hàng xóm phải — không cần lock parent lúc split.

Đây là lý do PostgreSQL có thể xử lý chèn index đồng thời không lock toàn cây.
:::

::: details Câu 4: Index B+ tree của bạn hoạt động tốt cho `SELECT * FROM orders WHERE price BETWEEN 10 AND 50`, nhưng `SELECT * FROM orders WHERE status = 'pending' AND region = 'US'` chậm dù có index tổng hợp trên (status, region). Chuyện gì xảy ra?
**Trả lời:** Truy vấn có thể không dùng prefix trái nhất của index, hoặc thứ tự cột trong index tổng hợp không match mẫu truy vấn.

Index tổng hợp B+ tree trên (status, region) lưu entry sắp xếp đầu tiên theo status, rồi theo region trong mỗi status. Index này xử lý `WHERE status = 'pending'` và `WHERE status = 'pending' AND region = 'US'` hiệu quả. Nhưng nếu truy vấn lọc trên `region` riêng không có `status`, B+ tree không thể nhảy tới lá đúng — nó phải quét cả index. Đây là quy tắc "leftmost prefix": index tổng hợp B+ tree chỉ hữu ích cho truy vấn lọc trên prefix các cột đã index theo thứ tự. Cho lọc đa cột trên tổ hợp tuỳ ý, cân nhắc index riêng hoặc chiến lược index khác.
:::
