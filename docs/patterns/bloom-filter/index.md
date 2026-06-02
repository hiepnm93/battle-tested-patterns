# Pattern: Bloom Filter

## One Liner

Test set membership in O(k) time with zero false negatives — at the cost of a tunable false positive rate.

## Core Idea

A bloom filter is a space-efficient probabilistic data structure. It uses a bit array of size `m` and `k` independent hash functions. To **add** an element, hash it `k` times and set those bit positions. To **test**, hash it `k` times and check if all positions are set.

```text
  hash1=2         hash2=5               hash3=9
     │               │                     │
     ▼               ▼                     ▼
  ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐
  │ 0│ 0│ 1│ 0│ 0│ 1│ 0│ 0│ 0│ 1│ 0│ 0│  m=12
  └──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘
    0  1  2  3  4  5  6  7  8  9 10 11

  add("apple")  → set bits 2, 5, 9
  test("apple") → all set     → "maybe yes"
  test("grape") → bit 7 not set → "definitely no"
```

| Property | Value |
|----------|-------|
| False negatives | **Impossible** — added elements always test positive |
| False positives | **Possible** — non-added elements may test positive |
| False positive rate | ≈ `(1 - e^(-kn/m))^k` where `n` = elements inserted |
| Deletion | **Not supported** — clearing bits may affect other elements |

## Production Proof

| Project | Source | Usage |
|---------|--------|-------|
| LevelDB | [bloom.cc#L17-L80](https://github.com/google/leveldb/blob/main/util/bloom.cc#L17-L80) | `BloomFilterPolicy` — uses double-hashing (Kirsch-Mitzenmacher) with rotate-right-17 to set `k` bits per key. `KeyMayMatch` returns false immediately if any probed bit is zero. Avoids disk reads for keys that don't exist. |
| Chromium (Blink) | [selector_filter.h#L149-L175](https://github.com/chromium/chromium/blob/main/third_party/blink/renderer/core/css/selector_filter.h#L149-L175) | 8192-bit bloom filter for CSS ancestor selector fast-rejection — discards 60-70% of CSS rules without full matching. Uses salted hashing (tag/id/class/attr) to prevent cross-type collisions. |

## Implementation

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

## Exercises

| Level | Exercise | File |
|-------|----------|------|
| Basic | Implement a bloom filter with add/mightContain | `exercises/typescript/bloom-filter/01-basic.test.ts` |

Run exercises: `pnpm test`

## When to Use

- **Database key lookup** — skip disk reads for keys that definitely don't exist (LevelDB, Cassandra, HBase)
- **Web caching** — avoid caching one-hit-wonders by checking if a URL was seen before
- **Network security** — check if a URL is in a malicious list without storing all URLs
- **Spell checkers** — fast "definitely not a word" rejection before dictionary lookup
- **Distributed systems** — reduce inter-node communication by filtering locally first

## When NOT to Use

- **Need deletion** — standard bloom filters don't support removal (use counting bloom filters instead)
- **Need exact membership** — if false positives are unacceptable, use a hash set
- **Small sets** — for < 1000 elements, a hash set uses comparable memory with zero false positives
- **Need to enumerate elements** — bloom filters only answer "is X in the set?", not "what's in the set?"

## More Production Uses

- [PostgreSQL](https://github.com/postgres/postgres/blob/master/contrib/bloom/blutils.c#L265-L293) — bloom index for multi-column filtering
- [Apache Cassandra](https://github.com/apache/cassandra) — SSTable bloom filters to avoid disk reads
- [bits-and-blooms/bloom](https://github.com/bits-and-blooms/bloom/blob/master/bloom.go#L77-L81) — popular Go bloom filter library (7k+ stars)
- [Bitcoin](https://github.com/bitcoin/bitcoin) — SPV bloom filters for lightweight clients
