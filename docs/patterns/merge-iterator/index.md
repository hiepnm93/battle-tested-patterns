---
title: "Pattern: Merge Iterator (K-Way Merge)"
description: 'Kết hợp K luồng đã sắp xếp thành một output đã sắp xếp dùng min-heap — "view hợp nhất" tổng quát qua nhiều nguồn dữ liệu.'
difficulty: "advanced"
---

# Pattern: Merge Iterator (K-Way Merge)

<DifficultyBadge />

## Mô tả một câu

Kết hợp K luồng đã sắp xếp thành một output đã sắp xếp dùng min-heap — "view hợp nhất" tổng quát qua nhiều nguồn dữ liệu.

<DemoBadge />

## Tương tự thực tế

Gộp các xếp bài thi đã sắp xếp từ các lớp khác nhau. Bạn nhìn bài trên cùng của mỗi xếp, lấy cái có số sinh viên thấp nhất, đặt vào xếp gộp, lặp lại. Bạn chỉ so sánh các bài trên cùng.

## Ý tưởng cốt lõi

Merge iterator duy trì min-heap kích thước K, mỗi entry theo dõi phần tử hiện tại và nó từ luồng nào. Mỗi cuộc gọi `next()`, pop phần tử nhỏ nhất, tiến luồng đó và push phần tử tiếp theo từ luồng đó vào heap. Điều này sinh output sắp xếp toàn cục trong O(n log K) thời gian, n là tổng phần tử.

```text
  Luồng 0: [1, 5, 9]
  Luồng 1: [2, 6, 7]
  Luồng 2: [3, 4, 8]

  Min-Heap (theo dõi nhỏ nhất từ mỗi luồng):
  ┌─────────────────────────┐
  │  pop min → push next    │
  │  ┌───┐                  │
  │  │ 1 │ ← Luồng 0        │
  │  ├───┤                  │
  │  │ 2 │ ← Luồng 1        │
  │  ├───┤                  │
  │  │ 3 │ ← Luồng 2        │
  │  └───┘                  │
  └─────────────────────────┘

  Output: 1, 2, 3, 4, 5, 6, 7, 8, 9
```

| Thuộc tính | Giá trị |
|----------|-------|
| Độ phức tạp thời gian | O(n log K) cho n tổng phần tử, K luồng |
| Độ phức tạp không gian | O(K) cho heap |
| Yêu cầu luồng | Mỗi luồng input phải đã sắp xếp |
| Đảm bảo output | Sắp xếp toàn cục, ổn định cho key bằng |

**Thử ngay** — thêm luồng đã sắp xếp và gộp thành một output sắp xếp toàn cục:

<MergeIteratorViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| LevelDB | [merger.cc#L17-L100](https://github.com/google/leveldb/blob/7ee830d02b623e8ffe0b95d59a74db1e58da04c5/table/merger.cc#L17-L100) | `MergingIterator` gộp nhiều iterator table đã sắp xếp (memtable + nhiều tầng SSTable) thành một view đã sắp xếp. `FindSmallest()` (L84-L100) quét children để tìm iterator có key hiện tại nhỏ nhất. Đây là đường đọc cốt lõi LevelDB — mọi `Get()` và `Seek()` đi qua merger này để trình bày view hợp nhất của dữ liệu rải qua nhiều file và bộ nhớ. |
| RocksDB | [merge_helper.cc#L87-L156](https://github.com/facebook/rocksdb/blob/7affaee1c49ebc80cb213ad86fe7d2a3ad447da2/db/merge_helper.cc#L87-L156) | `TimedFullMerge` triển khai toán tử merge kết hợp nhiều phiên bản của cùng key. Khi compaction, `MergeHelper::MergeUntil` đi qua iterator entry đã sắp xếp, gộp giá trị cho key trùng. Đây là cách RocksDB hỗ trợ thao tác merge người dùng định nghĩa (ví dụ append, increment) hiệu quả khi compaction. |

## Triển khai

::: code-group

```typescript [TypeScript]
class MinHeap<T> {
  private data: T[] = [];
  constructor(private compare: (a: T, b: T) => number) {}

  push(val: T): void {
    this.data.push(val);
    this.bubbleUp(this.data.length - 1);
  }

  pop(): T | undefined {
    if (this.data.length === 0) return undefined;
    const top = this.data[0]!;
    const last = this.data.pop()!;
    if (this.data.length > 0) {
      this.data[0] = last;
      this.sinkDown(0);
    }
    return top;
  }

  get size(): number { return this.data.length; }

  private bubbleUp(i: number): void {
    while (i > 0) {
      const parent = (i - 1) >> 1;
      if (this.compare(this.data[i]!, this.data[parent]!) >= 0) break;
      [this.data[i], this.data[parent]] = [this.data[parent]!, this.data[i]!];
      i = parent;
    }
  }

  private sinkDown(i: number): void {
    const n = this.data.length;
    while (true) {
      let smallest = i;
      const left = 2 * i + 1;
      const right = 2 * i + 2;
      if (left < n && this.compare(this.data[left]!, this.data[smallest]!) < 0) smallest = left;
      if (right < n && this.compare(this.data[right]!, this.data[smallest]!) < 0) smallest = right;
      if (smallest === i) break;
      [this.data[i], this.data[smallest]] = [this.data[smallest]!, this.data[i]!];
      i = smallest;
    }
  }
}

function mergeKSorted(streams: number[][]): number[] {
  const heap = new MinHeap<{ val: number; stream: number; index: number }>(
    (a, b) => a.val - b.val,
  );

  for (let s = 0; s < streams.length; s++) {
    if (streams[s]!.length > 0) {
      heap.push({ val: streams[s]![0]!, stream: s, index: 0 });
    }
  }

  const result: number[] = [];
  while (heap.size > 0) {
    const { val, stream, index } = heap.pop()!;
    result.push(val);
    const nextIndex = index + 1;
    if (nextIndex < streams[stream]!.length) {
      heap.push({ val: streams[stream]![nextIndex]!, stream, index: nextIndex });
    }
  }
  return result;
}
```

```rust [Rust]
use std::collections::BinaryHeap;
use std::cmp::Reverse;

pub fn merge_k_sorted(streams: &[Vec<i32>]) -> Vec<i32> {
    // (value, stream_index, element_index)
    let mut heap: BinaryHeap<Reverse<(i32, usize, usize)>> = BinaryHeap::new();

    for (s, stream) in streams.iter().enumerate() {
        if !stream.is_empty() {
            heap.push(Reverse((stream[0], s, 0)));
        }
    }

    let mut result = Vec::new();
    while let Some(Reverse((val, stream_idx, elem_idx))) = heap.pop() {
        result.push(val);
        let next_idx = elem_idx + 1;
        if next_idx < streams[stream_idx].len() {
            heap.push(Reverse((streams[stream_idx][next_idx], stream_idx, next_idx)));
        }
    }
    result
}
```

```go [Go]
package mergeiter

type heapEntry struct {
	val    int
	stream int
	index  int
}

type minHeap struct {
	data []heapEntry
}

func (h *minHeap) Len() int            { return len(h.data) }
func (h *minHeap) Less(i, j int) bool  { return h.data[i].val < h.data[j].val }
func (h *minHeap) Swap(i, j int)       { h.data[i], h.data[j] = h.data[j], h.data[i] }
func (h *minHeap) Push(x heapEntry)    { h.data = append(h.data, x); h.bubbleUp(len(h.data) - 1) }

func (h *minHeap) Pop() heapEntry {
	top := h.data[0]
	last := h.data[len(h.data)-1]
	h.data = h.data[:len(h.data)-1]
	if len(h.data) > 0 {
		h.data[0] = last
		h.sinkDown(0)
	}
	return top
}

func (h *minHeap) bubbleUp(i int) {
	for i > 0 {
		parent := (i - 1) / 2
		if h.data[i].val >= h.data[parent].val {
			break
		}
		h.data[i], h.data[parent] = h.data[parent], h.data[i]
		i = parent
	}
}

func (h *minHeap) sinkDown(i int) {
	n := len(h.data)
	for {
		smallest := i
		left, right := 2*i+1, 2*i+2
		if left < n && h.data[left].val < h.data[smallest].val {
			smallest = left
		}
		if right < n && h.data[right].val < h.data[smallest].val {
			smallest = right
		}
		if smallest == i {
			break
		}
		h.data[i], h.data[smallest] = h.data[smallest], h.data[i]
		i = smallest
	}
}

func MergeKSorted(streams [][]int) []int {
	h := &minHeap{}
	for s, stream := range streams {
		if len(stream) > 0 {
			h.Push(heapEntry{val: stream[0], stream: s, index: 0})
		}
	}

	var result []int
	for h.Len() > 0 {
		entry := h.Pop()
		result = append(result, entry.val)
		nextIdx := entry.index + 1
		if nextIdx < len(streams[entry.stream]) {
			h.Push(heapEntry{val: streams[entry.stream][nextIdx], stream: entry.stream, index: nextIdx})
		}
	}
	return result
}
```

```python [Python]
import heapq

def merge_k_sorted(streams: list[list[int]]) -> list[int]:
    heap: list[tuple[int, int, int]] = []  # (value, stream_idx, element_idx)

    for s, stream in enumerate(streams):
        if stream:
            heapq.heappush(heap, (stream[0], s, 0))

    result: list[int] = []
    while heap:
        val, stream_idx, elem_idx = heapq.heappop(heap)
        result.append(val)
        next_idx = elem_idx + 1
        if next_idx < len(streams[stream_idx]):
            heapq.heappush(heap, (streams[stream_idx][next_idx], stream_idx, next_idx))

    return result
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Gộp K mảng đã sắp xếp thành một mảng đã sắp xếp | `exercises/typescript/merge-iterator/01-basic.test.ts` |
| Trung bình | Gộp với khử trùng lặp (mới nhất thắng theo key) | `exercises/typescript/merge-iterator/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/merge_iterator/mod.rs` · Go `exercises/go/merge_iterator/merge_iterator_test.go` · Python `exercises/python/merge_iterator/test_merge_iterator.py`

## Khi nào nên dùng

- **Đọc LSM-tree** — gộp memtable + nhiều tầng SSTable thành một view đã sắp xếp (LevelDB, RocksDB)
- **Sort ngoại vi** — gộp run đã sắp xếp không vừa bộ nhớ
- **Tổng hợp log** — kết hợp log đã sắp xếp theo thời gian từ nhiều service
- **Database join** — merge-join các bảng đã sắp xếp trước
- **Search engine** — gộp posting list từ nhiều segment index

## Khi nào KHÔNG nên dùng

- **Input chưa sắp xếp** — gộp K-way yêu cầu luồng đã sắp xếp; sort trước hoặc dùng cách khác
- **K = 2** — gộp hai con trỏ đơn giản hơn và tránh overhead heap
- **Mẫu truy cập ngẫu nhiên** — merge iterator cho quét tuần tự, không phải tra điểm
- **K rất lớn với luồng nhỏ** — overhead heap lấn át khi luồng rất ngắn

## Thêm các ứng dụng production

- [TiKV](https://github.com/tikv/tikv) — merge iterator qua nhiều column family RocksDB
- [Apache Lucene](https://github.com/apache/lucene) — gộp segment khi tối ưu index
- [ClickHouse](https://github.com/ClickHouse/ClickHouse) — MergingSortedTransform để gộp data part đã sắp xếp
- [CockroachDB](https://github.com/cockroachdb/cockroach) — merge join và range scan qua nhiều range

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Min Heap](/patterns/min-heap/) | Min-heap là cấu trúc dữ liệu cốt lõi chạy gộp K-way |
| [LSM Tree (Log-Structured Merge Tree)](/patterns/lsm-tree/) | Compaction LSM gộp nhiều SSTable đã sắp xếp dùng merge iterator |
| [Iterator](/patterns/iterator/) | Merge iterator là kết hợp pattern iterator qua nhiều nguồn |
| [Skip List](/patterns/skip-list/) | Skip list cung cấp luồng input đã sắp xếp mà merge iterator tiêu thụ |
| [B+ Tree](/patterns/b-plus-tree/) | Merge iterator kết hợp khoảng đã sắp xếp từ nhiều quét lá B+ tree |

## Câu hỏi thử thách

::: details Câu 1: Bạn đang gộp 100 luồng đã sắp xếp, mỗi cái 1 triệu phần tử. Tổng số thao tác heap, và sao tốt hơn sort cả 100 triệu phần tử?
**Trả lời:** Khoảng 200 triệu thao tác heap (mỗi phần tử được push và pop một lần), mỗi cái tốn O(log 100) ~ 7 so sánh. Tổng: ~1,4 tỉ so sánh. Sort 100M phần tử với merge sort: O(100M × log(100M)) ~ 100M × 27 ~ 2,7 tỉ so sánh. Gộp K-way nhanh khoảng 2x.

Lợi thế then chốt không chỉ ít so sánh — mà là bản chất streaming. Gộp K-way dùng bộ nhớ O(K) bất kể tổng size dữ liệu. Bạn có thể gộp terabyte dữ liệu đã sắp xếp từ đĩa dùng chỉ vài KB space heap. Sort đầy đủ sẽ cần nạp tất cả vào bộ nhớ hoặc triển khai sort ngoại vi nhiều pass, vốn về cơ bản là gộp K-way.
:::

::: details Câu 2: MergingIterator của LevelDB dùng quét tuyến tính (FindSmallest) thay vì heap để tìm minimum. Khi nào thực sự nhanh hơn heap?
**Trả lời:** Khi K nhỏ (thường K < 10). Quét tuyến tính qua K phần tử tốn O(K) so sánh mỗi next() nhưng có cache locality tốt hơn và không đuổi con trỏ. Heap tốn O(log K) nhưng có hệ số hằng tệ hơn.

LevelDB thường gộp 2-7 tầng, nên K rất nhỏ. Ở K=4, quét tuyến tính làm 4 so sánh mỗi next() so với ~2 cho heap, nhưng tránh bookkeeping heap và có dự đoán nhánh tốt hơn. Cho K lớn (hàng trăm luồng, như trong sort ngoại vi), heap rõ ràng tốt hơn. Đây là tối ưu vi mô kinh điển nơi biết K điển hình quan trọng hơn độ phức tạp tiệm cận.
:::

::: details Câu 3: Merge iterator của bạn đang kết hợp luồng từ các shard database khác nhau. Hai shard trả cùng key "user:123" nhưng với giá trị và timestamp khác nhau. Merger nên xử lý thế nào?
**Trả lời:** Dùng timestamp làm tiebreaker: khi key bằng, entry với timestamp mới nhất thắng. Pop mọi entry với cùng key, chỉ giữ cái mới nhất.

Đây là chiến lược khử trùng lặp "latest-wins" dùng bởi LSM tree. Khi gộp, khi gặp key trùng, bạn so sequence number hoặc timestamp và giữ chỉ giá trị mới nhất. Trong LevelDB, entry mới hơn (sequence number cao hơn) che cái cũ. Điều này phải làm khi gộp — không phải sau — vì bạn cần biết entry mỗi cái từ luồng nào để xác định độ mới.
:::

::: details Câu 4: Bạn dùng merge iterator cho tổng hợp log realtime từ 50 microservice. Mỗi service sinh ~1000 event/giây. Output gộp đột nhiên rớt lại sau. Chuyện gì đang xảy ra?
**Trả lời:** Một luồng chậm/dừng đang chặn gộp. Heap không thể phát phần tử nào lớn hơn phần tử nhỏ nhất hiện tại qua mọi luồng, nên nếu một luồng dừng sinh, gộp dừng chờ nó.

Đây là "vấn đề kẻ chậm" trong gộp streaming. Giải pháp: (1) đặt timeout mỗi luồng — nếu không dữ liệu đến trong T ms, bỏ qua luồng đó tạm thời; (2) dùng watermark — phát mọi event dưới timestamp nhất định kể cả nếu vài luồng chưa báo cáo; (3) buffer và re-sort trong cửa sổ thay vì sắp xếp toàn cục nghiêm ngặt. Apache Flink và Google Dataflow dùng cách tiếp cận dựa trên watermark chính xác vì lý do này.
:::
