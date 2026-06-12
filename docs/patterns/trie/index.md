---
title: "Pattern: Trie (Prefix Tree)"
description: "Lưu chuỗi trong cây nơi mỗi cạnh đại diện một ký tự — các tiền tố chung dùng chung node, cho tra cứu O(k) theo độ dài key."
difficulty: "intermediate"
---

# Pattern: Trie (Prefix Tree)

<DifficultyBadge />

## Mô tả một câu

Lưu chuỗi trong cây nơi mỗi cạnh đại diện một ký tự — các tiền tố chung dùng chung node, cho tra cứu O(k) theo độ dài key.

<DemoBadge />

## Tương tự thực tế

Mép sách danh bạ điện thoại cũ có tab ngón — A, B, C dọc theo cạnh. Để tìm 'Smith', bạn nhảy tới S, rồi SM, rồi SMI. Mỗi chữ thu hẹp tìm kiếm, và tên chia sẻ tiền tố ('Smith', 'Smithson') dùng chung cùng đường.

## Ý tưởng cốt lõi

Trie (đọc "try") là cây nơi mỗi đường từ gốc tới node tạo thành một tiền tố. Node phân nhánh trên ký tự. Điều đó làm truy vấn tiền tố dễ dàng và tra cứu key tỉ lệ với độ dài key, không phải số key đã lưu.

```text
  Root
   ├── c
   │   ├── a
   │   │   ├── r ●       "car"
   │   │   │   ├── d ●   "card"
   │   │   │   └── e ●   "care"
   │   │   └── t ●       "cat"
   │   └── u
   │       └── t ●       "cut"
   └── d
       └── o
           └── g ●       "dog"
```

| Thuộc tính | Giá trị |
|----------|-------|
| Tra cứu | O(k) trong đó k = độ dài key |
| Chèn | O(k) |
| Tìm prefix | O(k + kết quả) — tìm mọi key có prefix trong một lần duyệt |
| Bộ nhớ | O(n × k) tệ nhất, nhưng prefix chung tiết kiệm đáng kể |

**Thử ngay** — chèn từ và tìm để xem các prefix chung tạo cây gọn:

<TrieViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| Nhân Linux | [fib_trie.c#L80-L120](https://github.com/torvalds/linux/blob/acb7500801e98639f6d8c2d796ed9f64cba83d3a/net/ipv4/fib_trie.c#L80-L120) | Bảng định tuyến IP — trie nén (LC-trie) lưu FIB của kernel. Node `key_vector` với match prefix độ dài thay đổi cho tra cứu longest-prefix-match O(log n) trên mỗi gói được chuyển. |
| Redis | [rax.h#L80-L130](https://github.com/redis/redis/blob/df63a65d4d4ee33ae67e9f101885074febe0bccb/src/rax.h#L80-L130) | Radix tree (`rax`) — trie nén dùng cho key Streams Redis, ánh xạ slot-tới-node cluster và iterator sorted set. `raxNode` lưu prefix nén với cờ iskey/isnull. |

## Triển khai

::: code-group

```typescript [TypeScript]
class TrieNode {
  children = new Map<string, TrieNode>();
  isEnd = false;
}

class Trie {
  private root = new TrieNode();

  insert(word: string): void {
    let node = this.root;
    for (const ch of word) {
      if (!node.children.has(ch)) node.children.set(ch, new TrieNode());
      node = node.children.get(ch)!;
    }
    node.isEnd = true;
  }

  search(word: string): boolean {
    const node = this.findNode(word);
    return node !== null && node.isEnd;
  }

  startsWith(prefix: string): boolean {
    return this.findNode(prefix) !== null;
  }

  private findNode(s: string): TrieNode | null {
    let node = this.root;
    for (const ch of s) {
      if (!node.children.has(ch)) return null;
      node = node.children.get(ch)!;
    }
    return node;
  }
}
```

```rust [Rust]
use std::collections::HashMap;

pub struct TrieNode {
    children: HashMap<char, TrieNode>,
    is_end: bool,
}

impl TrieNode {
    fn new() -> Self { TrieNode { children: HashMap::new(), is_end: false } }
}

pub struct Trie { root: TrieNode }

impl Trie {
    pub fn new() -> Self { Trie { root: TrieNode::new() } }

    pub fn insert(&mut self, word: &str) {
        let mut node = &mut self.root;
        for ch in word.chars() {
            node = node.children.entry(ch).or_insert_with(TrieNode::new);
        }
        node.is_end = true;
    }

    pub fn search(&self, word: &str) -> bool {
        self.find(word).map_or(false, |n| n.is_end)
    }

    pub fn starts_with(&self, prefix: &str) -> bool {
        self.find(prefix).is_some()
    }

    fn find(&self, s: &str) -> Option<&TrieNode> {
        let mut node = &self.root;
        for ch in s.chars() {
            match node.children.get(&ch) {
                Some(next) => node = next,
                None => return None,
            }
        }
        Some(node)
    }
}
```

```go [Go]
type TrieNode struct {
	children map[byte]*TrieNode
	isEnd    bool
}

type Trie struct {
	root *TrieNode
}

func NewTrie() *Trie {
	return &Trie{root: &TrieNode{children: make(map[byte]*TrieNode)}}
}

func (t *Trie) Insert(word string) {
	node := t.root
	for i := 0; i < len(word); i++ {
		ch := word[i]
		if _, ok := node.children[ch]; !ok {
			node.children[ch] = &TrieNode{children: make(map[byte]*TrieNode)}
		}
		node = node.children[ch]
	}
	node.isEnd = true
}

func (t *Trie) Search(word string) bool {
	node := t.find(word)
	return node != nil && node.isEnd
}

func (t *Trie) StartsWith(prefix string) bool {
	return t.find(prefix) != nil
}

func (t *Trie) find(s string) *TrieNode {
	node := t.root
	for i := 0; i < len(s); i++ {
		if next, ok := node.children[s[i]]; ok {
			node = next
		} else {
			return nil
		}
	}
	return node
}
```

```python [Python]
class TrieNode:
    def __init__(self):
        self.children: dict[str, TrieNode] = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self._find(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        return self._find(prefix) is not None

    def _find(self, s: str):
        node = self.root
        for ch in s:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai trie với insert/search/startsWith | `exercises/typescript/trie/01-basic.test.ts` |
| Trung bình | Autocomplete với kết quả xếp theo tần suất | `exercises/typescript/trie/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/trie/mod.rs` · Go `exercises/go/trie/trie_test.go` · Python `exercises/python/trie/test_trie.py`

## Khi nào nên dùng

- **Autocomplete / type-ahead** — tìm mọi hoàn thành cho prefix
- **Định tuyến IP** — match prefix dài nhất cho chuyển gói (FIB Linux)
- **Kiểm tra chính tả** — kiểm tra và gợi ý từ nhanh
- **Phân giải DNS** — tra cứu tên miền với nhãn phân cấp
- **Khử trùng lặp** — phát hiện chuỗi trùng hiệu quả

## Khi nào KHÔNG nên dùng

- **Chỉ tra cứu key chính xác** — hash map O(1) so với trie O(k)
- **Key số** — BST hoặc mảng đã sắp xếp tiết kiệm không gian hơn
- **Eo hẹp bộ nhớ** — trie có thể tốn nhiều bộ nhớ với phân bố key thưa
- **Key ngắn, duy nhất** — nếu key chia sẻ ít prefix, trie lãng phí node

## Thêm các ứng dụng production

- [Chromium](https://chromium.googlesource.com/chromium/src) — trie autocomplete URL
- [Package `net` Go](https://github.com/golang/go) — match tên miền
- [Apache Lucene](https://github.com/apache/lucene) — FST (finite state transducer) cho index term
- [iptables/nftables](https://github.com/torvalds/linux) — match IP set với trie

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Bloom Filter](/patterns/bloom-filter/) | Bloom filter lọc trước khi tra cứu trie tốn kém |
| [Registry](/patterns/registry/) | Trie có thể triển khai registry với định tuyến dựa trên prefix |
| [Skip List](/patterns/skip-list/) | Tra cứu sắp xếp thay thế — skip list sắp theo giá trị, trie theo ký tự key |

## Câu hỏi thử thách

::: details Câu 1: Bạn xây trie để lưu 100.000 từ tiếng Anh. Mỗi node có `Map<string, TrieNode>` với một entry mỗi ký tự con. Đồng nghiệp nói cái này tốn nhiều bộ nhớ hơn hash set đơn giản với cùng từ. Overhead bộ nhớ của trie có hợp lý không?
**Trả lời:** Cho tra cứu match chính xác thuần, không — hash set tiết kiệm bộ nhớ hơn và O(1). Overhead bộ nhớ trie chỉ hợp lý khi bạn cần thao tác prefix.

Trie ngây thơ với một node mỗi ký tự tạo nhiều object nhỏ với overhead map/con trỏ. Cho 100k từ tiếng Anh, hash set lưu 100k chuỗi; trie có thể tạo 500k+ node. Trie đáng giá khi use case yêu cầu tìm prefix ("tìm mọi từ bắt đầu bằng 'pre'"), autocomplete hoặc match prefix dài nhất — thao tác hash set không làm hiệu quả được. Nếu chỉ cần "từ chính xác này có trong set không?", dùng hash set.
:::

::: details Câu 2: Redis dùng radix tree (trie nén) thay vì trie chuẩn. "Nén" nghĩa là gì, và tại sao quan trọng cho bộ nhớ?
**Trả lời:** Trie nén (radix tree) gộp chuỗi node một con thành một node với nhãn đa ký tự, giảm đáng kể số node.

Trong trie chuẩn lưu "application", bạn tạo 11 node — một mỗi ký tự. Nếu không từ nào khác chia sẻ prefix "applicat", 8 node đầu mỗi cái có chính xác một con, lãng phí 8 node overhead. Radix tree nén thành một node với nhãn "applicat" theo sau bởi rẽ nhánh ở "i"→"on" và có thể các suffix khác. Triển khai `rax` của Redis lưu prefix nén inline trong struct node, giảm bộ nhớ 5-10 lần cho tập chuỗi điển hình với prefix chung dài.
:::

::: details Câu 3: Nhân Linux dùng trie cho tra cứu bảng định tuyến IP. Hash map cho match chính xác O(1). Sao kernel dùng trie?
**Trả lời:** Định tuyến IP yêu cầu match prefix dài nhất, không phải match chính xác — trie tự nhiên hỗ trợ điều này còn hash map thì không.

Khi kernel định tuyến gói tới `192.168.1.42`, nó cần tìm route khớp cụ thể nhất. Bảng định tuyến có thể chứa `0.0.0.0/0` (default), `192.168.0.0/16` và `192.168.1.0/24`. Match đúng là prefix dài nhất: `192.168.1.0/24`. Hash map cần kiểm tra mọi độ dài prefix khả dĩ (lên tới 32 cho IPv4), cần 32 tra cứu mỗi gói. Trie duyệt từ root tới node match sâu nhất một lần, tự nhiên tìm prefix dài nhất. Đó là lý do mọi OS lớn dùng biến thể trie cho định tuyến IP.
:::

::: details Câu 4: Hệ autocomplete của bạn lưu 10 triệu tên sản phẩm trong trie. Tìm prefix "ip" trả 50.000 kết quả. User chỉ thấy top 10. Bạn tránh thu thập 50.000 kết quả thế nào?
**Trả lời:** Lưu danh sách "top-k kết quả" ở mỗi node trie, tính trước khi chèn, nên truy vấn prefix trả kết quả đã xếp hạng trong O(k) mà không cần duyệt subtree.

Ngây thơ, tìm prefix cần duyệt toàn subtree dưới node prefix, thu thập mọi node `isEnd` — O(kết quả) lãng phí khi chỉ cần 10. Bằng cách duy trì priority queue giới hạn top-k kết quả tại mỗi node (cập nhật khi chèn), bạn có thể trả lời "top 10 cho prefix 'ip'" bằng cách đọc danh sách tại node 'p' dưới 'i'. Đánh đổi thời gian chèn và bộ nhớ lấy tốc độ truy vấn. Gợi ý tìm kiếm Google dùng cách tương tự với trie có trọng số tần suất.
:::
