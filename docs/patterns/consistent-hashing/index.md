---
title: "Pattern: Consistent Hashing"
description: "Phân tán key qua các node trên vòng ảo sao cho thêm hoặc xoá node chỉ remap ~1/n key."
difficulty: "advanced"
---

# Pattern: Consistent Hashing

<DifficultyBadge />

## Mô tả một câu

Phân tán key qua các node trên vòng ảo sao cho thêm hoặc xoá node chỉ remap ~1/n key.

<DemoBadge />

## Tương tự thực tế

Phân vùng giao hàng trên bản đồ thành phố hình tròn. Mỗi shipper phụ trách một phần của vòng tròn. Khi shipper mới gia nhập, họ tiếp quản chỉ phần kề nhỏ — các shipper khác hầu như không cảm nhận. Khi một người rời, chỉ shipper kế tiếp lấp khoảng trống.

## Ý tưởng cốt lõi

Hashing modular truyền thống (`hash(key) % n`) remap gần như mọi key khi `n` đổi. Consistent hashing đặt cả node và key trên vòng tròn. Mỗi key map tới node theo chiều kim đồng hồ đầu tiên từ vị trí của nó. Thêm hoặc xoá node chỉ ảnh hưởng key trong cung giữa nó và tiền nhiệm.

```text
  Vòng hash (0 đến 2^32, vòng quanh):

  0         Node A    ●k1     Node B          ●k2     Node C    2^32→0
  ├───────────┼─────────┼───────┼───────────────┼───────┼─────────┤
              ▲         │       ▲               │       ▲         │
              │         │       │               │       │         │
              │         └───►───┘               └───►───┘         │
              │              ↑                       ↑            │
              │         k1→Node B              k2→Node C          │
              └───────────────────────────────────────────────────┘
                              k3 vòng quanh → Node A

  ●k1 = key "user:42"     → node kế tiếp theo CW = Node B
  ●k2 = key "session:99"  → node kế tiếp theo CW = Node C
  ●k3 = key "order:7" (giữa Node C và 2^32) → vòng quanh → Node A
```

| Thuộc tính | Giá trị |
|----------|-------|
| Remap key khi add/remove | ~1/n (vs 100% với hash modular) |
| Virtual node (replica) | Cải thiện cân bằng — mỗi node vật lý map tới k vị trí trên vòng |
| Lookup | O(log n) qua tìm nhị phân trên vòng đã sắp xếp |

**Thử ngay** — thêm key, rồi thêm/xoá node để xem phân phối lại key tối thiểu:

<ConsistentHashViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| Go groupcache | [consistenthash.go#L28-L81](https://github.com/golang/groupcache/blob/2c02b8208cf8c02a3e358cb1d9b60950647543fc/consistenthash/consistenthash.go#L28-L81) | Struct `Map` (L28-L33) với sorted keys và hashMap. `Add` (L53-L62) chèn virtual node. `Get` (L65-L81) dùng tìm nhị phân `sort.Search` để tìm node gần nhất theo chiều kim đồng hồ. Do Brad Fitzpatrick (cha đẻ memcached). |
| HAProxy | [lb_chash.c#L415-L491](https://github.com/haproxy/haproxy/blob/fb38e40ad5751090992cde15d919866b1e91b8aa/src/lb_chash.c#L415-L491) | `chash_get_server_hash` — tìm server gần nhất trên vòng consistent hash dùng elastic binary tree (eb-tree) cho tra cứu O(log n). Hỗ trợ cân bằng bounded-loads và check eligibility server. |

## Triển khai

::: code-group

```typescript [TypeScript]
class HashRing {
  private ring = new Map<number, string>();
  private sortedKeys: number[] = [];

  constructor(private replicas = 100) {}

  private hash(key: string): number {
    let h = 2166136261;
    for (let i = 0; i < key.length; i++) {
      h ^= key.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  }

  addNode(node: string): void {
    for (let i = 0; i < this.replicas; i++) {
      const h = this.hash(`${node}:${i}`);
      this.ring.set(h, node);
      this.sortedKeys.push(h);
    }
    this.sortedKeys.sort((a, b) => a - b);
  }

  removeNode(node: string): void {
    for (let i = 0; i < this.replicas; i++) {
      this.ring.delete(this.hash(`${node}:${i}`));
    }
    this.sortedKeys = this.sortedKeys.filter((k) => this.ring.has(k));
  }

  getNode(key: string): string | undefined {
    if (this.sortedKeys.length === 0) return undefined;
    const h = this.hash(key);
    for (const k of this.sortedKeys) {
      if (k >= h) return this.ring.get(k);
    }
    return this.ring.get(this.sortedKeys[0]!);
  }
}
```

```rust [Rust]
pub struct HashRing {
    replicas: usize,
    keys: Vec<u32>,
    ring: std::collections::HashMap<u32, String>,
}

impl HashRing {
    pub fn new(replicas: usize) -> Self {
        HashRing { replicas, keys: Vec::new(), ring: std::collections::HashMap::new() }
    }

    fn hash(key: &str) -> u32 {
        let mut h: u32 = 2166136261;
        for b in key.bytes() {
            h ^= b as u32;
            h = h.wrapping_mul(16777619);
        }
        h
    }

    pub fn add_node(&mut self, node: &str) {
        for i in 0..self.replicas {
            let h = Self::hash(&format!("{}:{}", node, i));
            self.ring.insert(h, node.to_string());
            self.keys.push(h);
        }
        self.keys.sort();
    }

    pub fn get_node(&self, key: &str) -> Option<&str> {
        if self.keys.is_empty() { return None; }
        let h = Self::hash(key);
        let idx = self.keys.partition_point(|&k| k < h);
        let idx = if idx >= self.keys.len() { 0 } else { idx };
        self.ring.get(&self.keys[idx]).map(|s| s.as_str())
    }
}
```

```go [Go]
type HashRing struct {
	replicas int
	keys     []int
	hashMap  map[int]string
}

func fnv1a(s string) int {
	h := 2166136261
	for i := 0; i < len(s); i++ {
		h ^= int(s[i])
		h *= 16777619
	}
	if h < 0 {
		h = -h
	}
	return h
}

func NewHashRing(replicas int) *HashRing {
	return &HashRing{replicas: replicas, hashMap: make(map[int]string)}
}

func (r *HashRing) AddNode(node string) {
	for i := 0; i < r.replicas; i++ {
		h := fnv1a(fmt.Sprintf("%s:%d", node, i))
		r.keys = append(r.keys, h)
		r.hashMap[h] = node
	}
	sort.Ints(r.keys)
}

func (r *HashRing) GetNode(key string) string {
	if len(r.keys) == 0 {
		return ""
	}
	h := fnv1a(key)
	idx := sort.SearchInts(r.keys, h)
	if idx >= len(r.keys) {
		idx = 0
	}
	return r.hashMap[r.keys[idx]]
}
```

```python [Python]
import bisect

class HashRing:
    def __init__(self, replicas: int = 100):
        self.replicas = replicas
        self.ring: dict[int, str] = {}
        self.sorted_keys: list[int] = []

    def _hash(self, key: str) -> int:
        h = 2166136261
        for ch in key:
            h ^= ord(ch)
            h = (h * 16777619) & 0xFFFFFFFF
        return h

    def add_node(self, node: str) -> None:
        for i in range(self.replicas):
            h = self._hash(f"{node}:{i}")
            self.ring[h] = node
            bisect.insort(self.sorted_keys, h)

    def get_node(self, key: str) -> str | None:
        if not self.sorted_keys:
            return None
        h = self._hash(key)
        idx = bisect.bisect_left(self.sorted_keys, h)
        if idx >= len(self.sorted_keys):
            idx = 0
        return self.ring[self.sorted_keys[idx]]
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai hash ring với addNode/getNode | `exercises/typescript/consistent-hashing/01-basic.test.ts` |
| Trung bình | Vòng consistent hash với virtual node | `exercises/typescript/consistent-hashing/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/consistent_hashing/mod.rs` · Go `exercises/go/consistent_hashing/consistent_hashing_test.go` · Python `exercises/python/consistent_hashing/test_consistent_hashing.py`

## Khi nào nên dùng

- **Cache phân tán** — định tuyến key tới server cache, giảm invalidation cache khi mở rộng
- **Cân bằng tải** — phân phối request với gián đoạn tối thiểu khi backend đổi
- **Database sharded** — gán partition dữ liệu cho node
- **CDN** — định tuyến content tới edge server dựa trên hash URL

## Khi nào KHÔNG nên dùng

- **Topology tĩnh** — nếu node không bao giờ đổi, hash modular đơn giản hơn
- **Cluster nhỏ** — với < 5 node, random hoặc round-robin có thể đủ
- **Thứ tự nghiêm ngặt** — consistent hashing không bảo toàn thứ tự key
- **Cần phân phối đều** — không có virtual node, phân phối có thể không đều

## Thêm các ứng dụng production

- [serialx/hashring](https://github.com/serialx/hashring/blob/22c0c7ab6b1be4be7b950bae8b117767da7b18b6/hashring.go#L31-L37) — hash ring Go với node có trọng số
- [Apache Cassandra](https://github.com/apache/cassandra) — partitioner dùng consistent hashing cho token ring
- [Amazon DynamoDB](https://www.allthingsdistributed.com/2007/10/amazons_dynamo.html) — bài báo gốc về consistent hashing trong production
- [Memcached](https://github.com/memcached/memcached) — consistent hashing phía client (thuật toán ketama)

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Registry](/patterns/registry/) | Registry khám phá service; consistent hashing định tuyến tới chúng |
| [LRU Cache](/patterns/lru-cache/) | LRU cache phân tán dùng consistent hashing để định tuyến key tới node đúng |
| [Rate Limiter (Token Bucket)](/patterns/rate-limiter/) | Rate limit mỗi node trong cluster consistent hashing |

## Câu hỏi thử thách

::: details Câu 1: Bạn có hash ring với 3 node vật lý, mỗi cái 1 virtual node (không replica). Một node sở hữu 60% không gian key trong khi các cái khác mỗi cái 20%. Virtual node sửa thế nào, và sao groupcache mặc định count replica cao?
**Trả lời:** Virtual node trải mỗi node vật lý qua nhiều vị trí trên ring, làm phân phối hội tụ về đều khi số virtual node tăng.

Với chỉ 1 vị trí mỗi node, độ dài cung giữa node được xác định bởi giá trị hash — về cơ bản ngẫu nhiên, dẫn tới phương sai cao. Với 100-200 virtual node mỗi node vật lý, luật số lớn kích hoạt và mỗi node vật lý sở hữu xấp xỉ 1/n vòng. Groupcache mặc định count replica cao vì đồng đều thống kê cần nhiều mẫu. Đánh đổi là bộ nhớ: nhiều virtual node hơn nghĩa mảng sorted key và map ring lớn hơn.
:::

::: details Câu 2: Node B crash và bị xoá khỏi ring 5 node. Node nào hấp thụ traffic của nó? Mỗi node còn lại có chia tải đều không?
**Trả lời:** Chỉ node theo chiều kim đồng hồ ngay từ B trên ring hấp thụ mọi key của B — ba node khác hoàn toàn không bị ảnh hưởng.

Đây vừa là sức mạnh vừa điểm yếu của consistent hashing. Khi B bị xoá, key map tới B giờ "rơi xuống" node CW tiếp theo. Không có virtual node, một node hấp thụ 100% tải tái phân phối, có thể gấp đôi traffic. Với virtual node, nhiều vị trí ring của B được phân tán, nên key của nó rải qua nhiều node kế nhiệm — gần với chia đều. Đây là lý do then chốt virtual node tồn tại: biến lỗi "một hàng xóm hấp thụ tất cả" thành lỗi "nhiều hàng xóm chia tải".
:::

::: details Câu 3: Cluster cache của bạn dùng consistent hashing. Một ra mắt sản phẩm mới làm một key cụ thể ("homepage_banner") nhận 100x tốc độ request thường. Consistent hashing map nó tới Node C, giờ quá tải trong khi node khác idle. Consistent hashing có giải vấn đề hotspot không?
**Trả lời:** Không. Consistent hashing phân tán key đều qua node, nhưng không thể phân tán tải đều khi key riêng có tốc độ request khác nhau lớn.

Consistent hashing giải vấn đề *gán* key, không phải vấn đề *độ phổ biến* của key. Một hot key đơn luôn map tới một node. Giải pháp gồm: read replica (cache hot key trên nhiều node), cân bằng tải cấp request (định tuyến read cho hot key ngẫu nhiên), hoặc tách key ("homepage_banner" thành "homepage_banner:1" tới "homepage_banner:10" trải qua node). Mở rộng bounded-loads cho consistent hashing giải bằng cách chuyển hướng traffic tràn sang node tiếp theo trên ring.
:::

::: details Câu 4: Bạn cần migrate cluster cache từ 3 node sang 5 node với downtime bằng 0. Khi migrate, cả node cũ và mới cùng tồn tại. Key remap tới node mới trả cache miss dù dữ liệu tồn tại trên node cũ. Xử lý thế nào?
**Trả lời:** Dùng double-read khi migrate: tra cứu key trên ring mới trước, và khi miss, fallback sang ring cũ.

Consistent hashing đảm bảo remap tối thiểu (~1/n key di chuyển), nhưng key di chuyển sẽ miss trên node mới tới khi được điền. Chiến lược migrate là: (1) tính chủ key trên cả ring cũ và mới, (2) đọc từ node mới trước, (3) khi miss, đọc từ node cũ và backfill node mới. Khi mọi key đã migrate (hoặc TTL hết tự nhiên), xoá ring cũ. Đây là cách hệ thống như Memcached (thuật toán ketama) và Cassandra dùng khi reshard — vòng consistent hash định nghĩa state đích, nhưng giai đoạn chuyển xử lý khoảng trống. (Lưu ý: Redis Cluster dùng scheme hash 16.384 slot cố định, không phải consistent hashing.)
:::
