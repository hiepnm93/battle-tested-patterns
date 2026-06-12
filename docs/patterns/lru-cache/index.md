---
title: "Pattern: LRU Cache"
description: "Loại bỏ entry ít dùng gần nhất khi cache đầy — get và put O(1) qua hash map cộng doubly linked list."
difficulty: "intermediate"
---

# Pattern: LRU Cache

<DifficultyBadge />

## Mô tả một câu

Loại bỏ entry ít dùng gần nhất khi cache đầy — get và put O(1) qua hash map cộng doubly linked list.

<DemoBadge />

## Tương tự thực tế

Một bàn làm việc nhỏ có không gian giới hạn. Bạn giữ những cuốn sách dùng gần nhất trên bàn. Khi cần chỗ cho cuốn mới, bạn chuyển cuốn không động lâu nhất về kệ sách.

## Ý tưởng cốt lõi

LRU cache kết hợp hash map (cho tra cứu key O(1)) với doubly linked list (cho theo dõi mức gần đây O(1)). Mỗi truy cập, entry di chuyển ra đầu. Khi cache vượt capacity, entry ở cuối (ít dùng gần nhất) bị loại bỏ.

```text
  Gần nhất                                       Ít gần nhất
  ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐
  │  E  │◄──►│  D  │◄──►│  C  │◄──►│  B  │◄──►│  A  │  ← loại cái này
  └─────┘    └─────┘    └─────┘    └─────┘    └─────┘

  get("B") → di chuyển B ra đầu:
  ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐
  │  B  │◄──►│  E  │◄──►│  D  │◄──►│  C  │◄──►│  A  │
  └─────┘    └─────┘    └─────┘    └─────┘    └─────┘

  put("F") với capacity=5 → loại A, thêm F vào đầu
```

| Thuộc tính | Giá trị |
|----------|-------|
| get | O(1) — tra hash map + di chuyển ra đầu |
| put | O(1) — chèn hash map + loại nếu quá capacity |
| Chính sách loại bỏ | Ít Dùng Gần Nhất (đuôi danh sách) |
| Bộ nhớ | O(capacity) |

**Thử ngay** — put và get key để xem loại bỏ LRU hoạt động:

<LRUCacheViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| Go groupcache | [lru.go#L23-L104](https://github.com/golang/groupcache/blob/2c02b8208cf8c02a3e358cb1d9b60950647543fc/lru/lru.go#L23-L104) | Struct `Cache` (L23-L34) với doubly linked list + hash map. `Add` (L56-L71) chèn/cập nhật và di chuyển ra đầu; `Get` (L74-L83) di chuyển ra đầu khi hit; `RemoveOldest` (L96-L104) loại từ cuối. Do Brad Fitzpatrick (cha đẻ memcached). |
| Redis | [evict.c#L55-L83](https://github.com/redis/redis/blob/df63a65d4d4ee33ae67e9f101885074febe0bccb/src/evict.c#L55-L83) | LRU xấp xỉ — clock LRU giảm bit và ước lượng idle-time với wraparound. `evictionPoolPopulate` (L134-L225) lấy mẫu N key và chèn vào pool eviction đã sắp xếp. Đánh đổi kỹ thuật: overhead bộ nhớ O(1) ở quy mô lớn vs LRU chính xác. |

## Triển khai

::: code-group

```typescript [TypeScript]
class LRUCache<K, V> {
  private map = new Map<K, V>();

  constructor(private capacity: number) {}

  get(key: K): V | undefined {
    if (!this.map.has(key)) return undefined;
    const value = this.map.get(key)!;
    this.map.delete(key);
    this.map.set(key, value);
    return value;
  }

  put(key: K, value: V): void {
    if (this.map.has(key)) this.map.delete(key);
    this.map.set(key, value);
    if (this.map.size > this.capacity) {
      const oldest = this.map.keys().next().value!;
      this.map.delete(oldest);
    }
  }
}
```

```rust [Rust]
use std::collections::HashMap;

pub struct LRUCache {
    capacity: usize,
    order: Vec<String>,
    map: HashMap<String, String>,
}

impl LRUCache {
    pub fn new(capacity: usize) -> Self {
        LRUCache { capacity, order: Vec::new(), map: HashMap::new() }
    }

    pub fn get(&mut self, key: &str) -> Option<&str> {
        if !self.map.contains_key(key) { return None; }
        self.order.retain(|k| k != key);
        self.order.push(key.to_string());
        self.map.get(key).map(|v| v.as_str())
    }

    pub fn put(&mut self, key: &str, value: &str) {
        self.order.retain(|k| k != key);
        self.order.push(key.to_string());
        self.map.insert(key.to_string(), value.to_string());
        if self.map.len() > self.capacity {
            if let Some(oldest) = self.order.first().cloned() {
                self.order.remove(0);
                self.map.remove(&oldest);
            }
        }
    }
}
```

```go [Go]
type entry struct {
	key   string
	value any
}

type LRUCache struct {
	capacity int
	ll       *list.List
	cache    map[string]*list.Element
}

func NewLRUCache(capacity int) *LRUCache {
	return &LRUCache{capacity: capacity, ll: list.New(), cache: make(map[string]*list.Element)}
}

func (c *LRUCache) Get(key string) (any, bool) {
	if ele, ok := c.cache[key]; ok {
		c.ll.MoveToFront(ele)
		return ele.Value.(*entry).value, true
	}
	return nil, false
}

func (c *LRUCache) Put(key string, value any) {
	if ele, ok := c.cache[key]; ok {
		c.ll.MoveToFront(ele)
		ele.Value.(*entry).value = value
		return
	}
	ele := c.ll.PushFront(&entry{key, value})
	c.cache[key] = ele
	if c.ll.Len() > c.capacity {
		oldest := c.ll.Back()
		c.ll.Remove(oldest)
		delete(c.cache, oldest.Value.(*entry).key)
	}
}
```

```python [Python]
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: OrderedDict[str, object] = OrderedDict()

    def get(self, key: str):
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: str, value: object) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai LRU cache với get/put và loại bỏ | `exercises/typescript/lru-cache/01-basic.test.ts` |
| Trung bình | LRU cache nhận biết TTL với hết hạn | `exercises/typescript/lru-cache/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/lru_cache/mod.rs` · Go `exercises/go/lru_cache/lru_cache_test.go` · Python `exercises/python/lru_cache/test_lru_cache.py`

## Khi nào nên dùng

- **Cache truy vấn database** — cache truy vấn nóng, loại cái nguội
- **Phân giải DNS** — cache tra cứu gần đây
- **Trình duyệt web** — cache trang/tài nguyên với bộ nhớ giới hạn
- **Cache response API** — giữ response hay yêu cầu ấm
- **Hệ điều hành** — cache page, cache dentry, cache inode

## Khi nào KHÔNG nên dùng

- **Tải kháng quét** — quét bảng đầy loại bỏ mọi entry hữu ích (dùng LRU-K hoặc ARC)
- **Cần hết hạn theo thời gian** — LRU loại bỏ theo mức gần đây, không theo tuổi (thêm tầng TTL riêng)
- **Tần suất quan trọng hơn** — nếu item phổ biến bị loại bởi burst yêu cầu duy nhất, dùng LFU
- **Tăng không giới hạn OK** — nếu bộ nhớ không bị giới hạn, hash map đơn giản hơn

## Thêm các ứng dụng production

- [Redis](https://github.com/redis/redis) — `maxmemory-policy allkeys-lru` cho loại bỏ LRU
- [Guava Cache](https://github.com/google/guava) — `CacheBuilder.maximumSize()` với loại bỏ LRU
- [Python functools](https://github.com/python/cpython) — decorator `@lru_cache`
- [Caffeine](https://github.com/ben-manes/caffeine) — cache Java hiệu năng cao (Window TinyLfu, lấy cảm hứng từ LRU)

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Free List](/patterns/free-list/) | Loại bỏ LRU giải phóng node; free list tái chế chúng không gọi allocator |
| [Flyweight](/patterns/flyweight/) | Cả hai giảm bộ nhớ — LRU giới hạn kích thước cache, flyweight chia sẻ object giống nhau |
| [Consistent Hashing](/patterns/consistent-hashing/) | Cache phân tán dùng consistent hashing để định tuyến key tới instance LRU đúng |
| [Tombstone](/patterns/tombstone/) | Tombstone đánh dấu entry cache đã xoá trong LRU cache phân tán |
| [Bloom Filter](/patterns/bloom-filter/) | Bloom filter kiểm tra trước trước khi tra LRU cache tốn kém để tránh cache miss |
| [Interning / Symbol Table](/patterns/interning/) | Bảng intern có thể dùng loại bỏ LRU để giới hạn bộ nhớ |

## Câu hỏi thử thách

::: details Câu 1: LRU cache capacity 3. Thao tác: put(A), put(B), put(C), put(D), get(B). Trong cache có gì?
**Trả lời:** `{B, D, C}`

Sau put(A,B,C), cache đầy. put(D) loại A (ít dùng gần nhất). Giờ `{D, C, B}`. get(B) di chuyển B ra đầu. Thứ tự cuối gần nhất→ít gần: `B, D, C`.

Insight then chốt: `get()` tính là "dùng" — di chuyển entry ra đầu, không chỉ trả về nó.
:::

::: details Câu 2: Bạn có web server với LRU cache cho response API. Một bot crawl mọi trang một lần. Chuyện gì xảy ra?
**Trả lời:** Bot loại bỏ mọi entry cache nóng của bạn.

Mỗi trang được crawl truy cập một lần, đẩy ra đầu, và loại bỏ một trang hay dùng. Sau crawl, cache đầy trang không ai yêu cầu lại. Đây là vấn đề **kháng quét** — LRU dễ bị tổn thương trước quét tuần tự. Giải pháp: LRU-K (loại bỏ chỉ nếu truy cập < K lần), ARC (thích nghi), hoặc cache hai tầng.
:::

::: details Câu 3: Sao Redis dùng "LRU xấp xỉ" thay vì LRU chính xác?
**Trả lời:** LRU chính xác cần doubly linked list mỗi key — đó là 2 con trỏ (16 byte trên 64-bit) mỗi key chỉ để xếp thứ tự. Với hàng triệu key, đó là overhead đáng kể.

Redis thay vào đó lưu clock LRU 24-bit mỗi key (3 byte) và lấy mẫu N key ngẫu nhiên khi cần loại bỏ, loại cái có clock cũ nhất. Đánh đổi thứ tự loại bỏ hoàn hảo lấy overhead bộ nhớ O(1) mỗi key. Thực tế, lấy mẫu 10 key cho kết quả rất gần LRU chính xác.
:::

::: details Câu 4: Bạn có thể xây LRU cache O(1) mà không có doubly linked list không?
**Trả lời:** Có — dùng ngôn ngữ có hash map có thứ tự. Trong JavaScript, `Map` bảo toàn thứ tự chèn. Xoá và chèn lại khi truy cập để di chuyển sang "gần nhất". Đó chính xác là điều triển khai TypeScript trên làm.

Trong ngôn ngữ không có map có thứ tự (C, Go), bạn cần cách kinh điển hash map + doubly linked list. `groupcache` của Go làm vậy với `container/list`.
:::
