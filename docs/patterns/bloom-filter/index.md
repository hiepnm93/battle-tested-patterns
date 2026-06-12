---
title: "Pattern: Bloom Filter"
description: "Kiểm tra thành viên tập trong O(k) thời gian không có âm tính giả — đánh đổi tỉ lệ dương tính giả điều chỉnh được."
difficulty: "intermediate"
---

# Pattern: Bloom Filter

<DifficultyBadge />

## Mô tả một câu

Kiểm tra thành viên tập trong O(k) thời gian không có âm tính giả — đánh đổi tỉ lệ dương tính giả điều chỉnh được.

<DemoBadge />

## Tương tự thực tế

Một bảo vệ có danh sách khách đôi khi cho người không phải khách vào. Nếu bảo vệ nói 'bạn KHÔNG có trong danh sách', đó là khẳng định. Nhưng nếu nói 'bạn có thể có trong danh sách', bạn vẫn phải kiểm với sổ đăng ký thực tế bên trong.

## Ý tưởng cốt lõi

Bloom filter là cấu trúc dữ liệu xác suất tiết kiệm không gian. Nó dùng mảng bit kích thước `m` và `k` hàm hash độc lập. Để **thêm** một phần tử, hash `k` lần và set các vị trí bit đó. Để **kiểm tra**, hash `k` lần và xem mọi vị trí có được set không.

```text
  hash1=2         hash2=5               hash3=9
     │               │                     │
     ▼               ▼                     ▼
  ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐
  │ 0│ 0│ 1│ 0│ 0│ 1│ 0│ 0│ 0│ 1│ 0│ 0│  m=12
  └──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘
    0  1  2  3  4  5  6  7  8  9 10 11

  add("apple")  → set bit 2, 5, 9
  test("apple") → đều set         → "có thể có"
  test("grape") → bit 7 không set → "chắc chắn không"
```

| Thuộc tính | Giá trị |
|----------|-------|
| Âm tính giả | **Không thể** — phần tử đã thêm luôn test dương |
| Dương tính giả | **Có thể** — phần tử chưa thêm có thể test dương |
| Tỉ lệ dương tính giả | ≈ `(1 - e^(-kn/m))^k` trong đó `n` = số phần tử đã chèn |
| Xoá | **Không hỗ trợ** — clear bit có thể ảnh hưởng phần tử khác |

**Thử ngay** — thêm item và kiểm tra thành viên để xem dương tính giả hoạt động:

<BloomFilterViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| LevelDB | [bloom.cc#L17-L80](https://github.com/google/leveldb/blob/7ee830d02b623e8ffe0b95d59a74db1e58da04c5/util/bloom.cc#L17-L80) | `BloomFilterPolicy` — dùng double-hashing (Kirsch-Mitzenmacher) với rotate-right-17 để set `k` bit mỗi key. `KeyMayMatch` trả false ngay nếu bit probed nào bằng 0. Tránh đọc đĩa cho key không tồn tại. |
| Chromium (Blink) | [selector_filter.h#L149-L175](https://github.com/chromium/chromium/blob/5cffea3f665b7762369a0fa84d2f208875e7225e/third_party/blink/renderer/core/css/selector_filter.h#L149-L175) | Bloom filter 8192-bit cho fast-rejection selector ancestor CSS — loại 60-70% rule CSS không cần match đầy đủ. Dùng hash có salt (tag/id/class/attr) để chống va chạm xuyên kiểu. |

## Triển khai

::: code-group

```typescript [TypeScript]
class BloomFilter {
  private bits: Uint8Array;
  private size: number;
  private hashCount: number;

  constructor(size: number, hashCount = 3) {
    this.size = size;
    this.hashCount = hashCount;
    this.bits = new Uint8Array(size);
  }

  private hashes(item: string): number[] {
    let h1 = 0;
    let h2 = 0;
    for (let i = 0; i < item.length; i++) {
      h1 = (h1 * 31 + item.charCodeAt(i)) | 0;
      h2 = (h2 * 37 + item.charCodeAt(i)) | 0;
    }
    const result: number[] = [];
    for (let i = 0; i < this.hashCount; i++) {
      result.push(((h1 + i * h2) % this.size + this.size) % this.size);
    }
    return result;
  }

  add(item: string): void {
    for (const pos of this.hashes(item)) {
      this.bits[pos] = 1;
    }
  }

  mightContain(item: string): boolean {
    return this.hashes(item).every((pos) => this.bits[pos] === 1);
  }
}
```

```rust [Rust]
pub struct BloomFilter {
    bits: Vec<bool>,
    size: usize,
    hash_count: usize,
}

impl BloomFilter {
    pub fn new(size: usize, hash_count: usize) -> Self {
        BloomFilter { bits: vec![false; size], size, hash_count }
    }

    fn hashes(&self, item: &str) -> Vec<usize> {
        let mut h1: i32 = 0;
        let mut h2: i32 = 0;
        for b in item.bytes() {
            h1 = h1.wrapping_mul(31).wrapping_add(b as i32);
            h2 = h2.wrapping_mul(37).wrapping_add(b as i32);
        }
        (0..self.hash_count)
            .map(|i| ((h1.wrapping_add((i as i32).wrapping_mul(h2))) as usize) % self.size)
            .collect()
    }

    pub fn add(&mut self, item: &str) {
        for pos in self.hashes(item) {
            self.bits[pos] = true;
        }
    }

    pub fn might_contain(&self, item: &str) -> bool {
        self.hashes(item).iter().all(|&pos| self.bits[pos])
    }
}
```

```go [Go]
type BloomFilter struct {
	bits      []bool
	size      int
	hashCount int
}

func NewBloomFilter(size, hashCount int) *BloomFilter {
	return &BloomFilter{bits: make([]bool, size), size: size, hashCount: hashCount}
}

func (bf *BloomFilter) hashes(item string) []int {
	h1, h2 := 0, 0
	for _, b := range []byte(item) {
		h1 = h1*31 + int(b)
		h2 = h2*37 + int(b)
	}
	result := make([]int, bf.hashCount)
	for i := range result {
		result[i] = ((h1 + i*h2) % bf.size + bf.size) % bf.size
	}
	return result
}

func (bf *BloomFilter) Add(item string) {
	for _, pos := range bf.hashes(item) {
		bf.bits[pos] = true
	}
}

func (bf *BloomFilter) MightContain(item string) bool {
	for _, pos := range bf.hashes(item) {
		if !bf.bits[pos] {
			return false
		}
	}
	return true
}
```

```python [Python]
class BloomFilter:
    def __init__(self, size: int, hash_count: int = 3):
        self.size = size
        self.hash_count = hash_count
        self.bits = [False] * size

    def _hashes(self, item: str) -> list[int]:
        h1, h2 = 0, 0
        for ch in item:
            h1 = (h1 * 31 + ord(ch)) & 0xFFFFFFFF
            h2 = (h2 * 37 + ord(ch)) & 0xFFFFFFFF
        return [(h1 + i * h2) % self.size for i in range(self.hash_count)]

    def add(self, item: str) -> None:
        for pos in self._hashes(item):
            self.bits[pos] = True

    def might_contain(self, item: str) -> bool:
        return all(self.bits[pos] for pos in self._hashes(item))
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai bloom filter với add/mightContain | `exercises/typescript/bloom-filter/01-basic.test.ts` |
| Trung bình | Spell checker dùng từ điển bloom filter | `exercises/typescript/bloom-filter/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/bloom_filter/mod.rs` · Go `exercises/go/bloom_filter/bloom_filter_test.go` · Python `exercises/python/bloom_filter/test_bloom_filter.py`

## Khi nào nên dùng

- **Tra key database** — bỏ qua đọc đĩa cho key chắc chắn không tồn tại (LevelDB, Cassandra, HBase)
- **Cache web** — tránh cache one-hit-wonder bằng cách kiểm tra URL đã thấy chưa
- **Bảo mật mạng** — kiểm tra URL có trong danh sách độc hại không cần lưu mọi URL
- **Spell checker** — từ chối nhanh "chắc chắn không phải từ" trước khi tra từ điển
- **Hệ phân tán** — giảm giao tiếp giữa node bằng cách lọc cục bộ trước

## Khi nào KHÔNG nên dùng

- **Cần xoá** — bloom filter chuẩn không hỗ trợ remove (dùng counting bloom filter)
- **Cần thành viên chính xác** — nếu dương tính giả không chấp nhận được, dùng hash set
- **Tập nhỏ** — cho < 1000 phần tử, hash set dùng bộ nhớ tương đương không có dương tính giả
- **Cần liệt kê phần tử** — bloom filter chỉ trả lời "X có trong tập?", không phải "trong tập có gì?"

## Thêm các ứng dụng production

- [PostgreSQL](https://github.com/postgres/postgres/blob/e18b0cb7344cb4bd28468f6c0aeeb9b9241d30aa/contrib/bloom/blutils.c#L265-L293) — bloom index cho lọc nhiều cột
- [Apache Cassandra](https://github.com/apache/cassandra) — bloom filter SSTable tránh đọc đĩa
- [bits-and-blooms/bloom](https://github.com/bits-and-blooms/bloom/blob/f0c3e57ab5ce07691a0a3124b9ed2db6df82ac9b/bloom.go#L77-L81) — thư viện bloom filter Go phổ biến (7k+ sao)
- [Bitcoin](https://github.com/bitcoin/bitcoin) — bloom filter SPV cho client nhẹ

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [LSM Tree (Log-Structured Merge Tree)](/patterns/lsm-tree/) | LSM tree gắn bloom filter vào mỗi SSTable để tránh đọc đĩa không cần |
| [Trie (Prefix Tree)](/patterns/trie/) | Bloom filter lọc sơ trước khi duyệt trie tốn kém |
| [LRU Cache](/patterns/lru-cache/) | Cả hai tăng tốc tra cứu — bloom filter loại âm, LRU cache lưu dương |
| [Interning / Symbol Table](/patterns/interning/) | Bloom filter kiểm tra trước khi tra bảng intern tốn kém |
| [Skip List](/patterns/skip-list/) | Bloom filter giảm đọc đĩa không cần trong lưu trữ nền skip-list |

## Câu hỏi thử thách

::: details Câu 1: Bạn triển khai bloom filter với m=1000 bit và k=3 hash để kiểm tra thành viên URL. Sau khi chèn 800 URL, tỉ lệ dương tính giả cao không chấp nhận được. Bạn kỳ vọng ~1%. Có gì sai?
**Trả lời:** Mảng bit bị bão hoà — 800 item trong 1000 bit nghĩa là hầu hết bit đã set 1, làm gần như mọi truy vấn trả "có thể có."

Công thức tỉ lệ dương tính giả `(1 - e^(-kn/m))^k` cho thấy với k=3, n=800, m=1000, khoảng 91% bit đã set, cho tỉ lệ dương tính giả ~75%. Cách sửa là tăng m. Cho tỉ lệ 1% với n=800 và k=3, bạn cần m ≈ 11.500 bit (~1,4 KB). Quy tắc thump: ~10 bit mỗi phần tử cho tỉ lệ 1%.
:::

::: details Câu 2: Đồng nghiệp đề nghị xoá item khỏi bloom filter bằng cách clear bit đã set khi chèn. Tại sao điều đó phá vỡ cấu trúc dữ liệu?
**Trả lời:** Clear bit cho một item có thể phá huỷ bằng chứng thành viên của item khác mà hash của chúng đi vào cùng vị trí bit.

Trong bloom filter, nhiều item chia sẻ bit. Nếu "apple" và "banana" cùng hash đến bit 5, clear bit 5 khi xoá "apple" tạo âm tính giả cho "banana" — vi phạm đảm bảo cơ bản không có âm tính giả của bloom filter. Counting bloom filter giải bằng cách lưu counter thay vì bit đơn, giảm khi xoá và chỉ clear khi counter về 0.
:::

::: details Câu 3: Hệ thống của bạn có hai bloom filter — một xây từ dataset server A và một từ dataset server B. Một truy vấn cần kiểm tra "key này có được server nào thấy chưa?" Bạn có thể trả lời không cần truy vấn từng filter riêng?
**Trả lời:** Có. OR bitwise hai mảng bit để tạo filter hợp trả lời "thấy bởi A hoặc B" trong một truy vấn.

Hoạt động được vì test thành viên bloom filter thuần là hàm của bit nào đã set. OR các mảng tạo filter mà một bit được set nếu nó đã set ở A hoặc B, đúng ngữ nghĩa hợp. Filter kết quả có tỉ lệ dương tính giả cao hơn (nhiều bit set hơn), nhưng không có âm tính giả được bảo toàn. Tính chất này làm bloom filter có khả năng ghép duy nhất — bạn không làm được điều này với hash set mà không chuyển mọi phần tử.
:::

::: details Câu 4: LevelDB dùng bloom filter để bỏ qua đọc đĩa cho key không tồn tại. Nếu bloom filter nói "có thể có" cho key thực sự không tồn tại, chi phí là gì? Nếu nói "không" cho key thực sự tồn tại thì sao?
**Trả lời:** Dương tính giả tốn một lần đọc đĩa không cần (lãng phí I/O nhưng kết quả đúng). Âm tính giả sẽ trả "key not found" cho key tồn tại — mất dữ liệu âm thầm.

Sự bất đối xứng này là lý do bloom filter đảm bảo không có âm tính giả. Dương tính giả chỉ nghĩa "đã kiểm tra đĩa và key không có" — hệ thống tự sửa với một I/O thêm. Nhưng nếu bloom filter có thể sinh âm tính giả, database sẽ bỏ hoàn toàn đọc đĩa và báo sai key không có. Đó là hư dữ liệu, không phải vấn đề hiệu năng. Toàn bộ giá trị bloom filter trong database phụ thuộc vào đảm bảo lỗi một phía này.
:::
