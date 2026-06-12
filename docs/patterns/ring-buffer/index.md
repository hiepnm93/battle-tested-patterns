---
title: "Pattern: Ring Buffer (Buffer vòng)"
description: "Buffer kích thước cố định vòng quanh qua số học modulo, cho enqueue và dequeue thời gian hằng mà không cấp phát bộ nhớ."
difficulty: "beginner"
---

# Pattern: Ring Buffer (Buffer vòng)

<DifficultyBadge />

## Mô tả một câu

Buffer kích thước cố định vòng quanh qua số học modulo, cho enqueue và dequeue thời gian hằng mà không cấp phát bộ nhớ.

<DemoBadge />

## Tương tự thực tế

Băng chuyền sushi trong nhà hàng. Băng có số đĩa cố định. Đầu bếp đặt đĩa mới ở một đầu, khách lấy đĩa khi nó đi qua. Khi băng đầy, đầu bếp phải chờ. Khi rỗng, khách phải chờ. Băng cứ vòng vô tận.

## Ý tưởng cốt lõi

Ring buffer dùng mảng cố định với hai con trỏ — `head` (vị trí đọc tiếp) và `tail` (vị trí ghi tiếp). Khi một con trỏ đạt cuối, nó vòng về đầu. Không dịch, không resize, không cấp phát.

```text
  Capacity: 8       head=2, tail=6

  ┌───┬───┬───┬───┬───┬───┬───┬───┐
  │   │   │ A │ B │ C │ D │   │   │
  └───┴───┴─▲─┴───┴───┴───┴─▲─┴───┘
            │               │
          head            tail

  Ghi 'E' tại tail (index 6), rồi tail = (6+1) % 8 = 7
  Đọc 'A' tại head (index 2), rồi head = (2+1) % 8 = 3
```

Wrap-around `index % capacity` là cái làm nó "ring" — không bao giờ hết chỗ trong mảng, chỉ ghi đè dữ liệu cũ (hoặc block, tuỳ triển khai).

| Thuộc tính | Giá trị |
|----------|-------|
| enqueue / write | O(1) — ghi tại tail, tiến con trỏ |
| dequeue / read | O(1) — đọc tại head, tiến con trỏ |
| Bộ nhớ | O(capacity) — cố định, cấp phát trước |
| Chính sách tràn | Block (queue giới hạn) hoặc ghi đè cũ nhất (log buffer) |

**Thử ngay** — enqueue và dequeue item để xem các con trỏ head/tail vòng quanh:

<RingBufferViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| LMAX Disruptor | [RingBuffer.java#L84-L130](https://github.com/LMAX-Exchange/disruptor/blob/c871ca49826a6be7ada6957f6fbafcfecf7b1f87/src/main/java/com/lmax/disruptor/RingBuffer.java#L84-L130) | `RingBuffer` của Disruptor là cấu trúc dữ liệu cốt lõi đằng sau LMAX Exchange — xử lý 6 triệu lệnh mỗi giây. Dùng kích thước luỹ thừa 2 để modulo bằng bitwise (`sequence & (bufferSize - 1)`). |
| Nhân Linux | [ring_buffer.h#L12-L70](https://github.com/torvalds/linux/blob/acb7500801e98639f6d8c2d796ed9f64cba83d3a/include/linux/ring_buffer.h#L12-L70) | Struct `ring_buffer_event` với `type_len` đóng gói vào 5 bit + delta timestamp 27 bit. Ring buffer mỗi CPU — `ring_buffer_read`/`ring_buffer_consume` tiến con trỏ đọc không lock. Tràn âm thầm ghi đè event cũ nhất. |

## Triển khai

::: code-group

```typescript [TypeScript]
class RingBuffer<T> {
  private buffer: (T | undefined)[];
  private head = 0;
  private tail = 0;
  private count = 0;
  private capacity: number;

  constructor(capacity: number) {
    this.capacity = capacity;
    this.buffer = new Array(capacity);
  }

  enqueue(item: T): boolean {
    if (this.count === this.capacity) return false;
    this.buffer[this.tail] = item;
    this.tail = (this.tail + 1) % this.capacity;
    this.count++;
    return true;
  }

  dequeue(): T | undefined {
    if (this.count === 0) return undefined;
    const item = this.buffer[this.head];
    this.buffer[this.head] = undefined;
    this.head = (this.head + 1) % this.capacity;
    this.count--;
    return item;
  }

  peek(): T | undefined {
    return this.count > 0 ? this.buffer[this.head] : undefined;
  }

  get size(): number { return this.count; }
  get isFull(): boolean { return this.count === this.capacity; }
  get isEmpty(): boolean { return this.count === 0; }
}
```

```rust [Rust]
pub struct RingBuffer<T> {
    buffer: Vec<Option<T>>,
    head: usize,
    tail: usize,
    count: usize,
    capacity: usize,
}

impl<T> RingBuffer<T> {
    pub fn new(capacity: usize) -> Self {
        let mut buffer = Vec::with_capacity(capacity);
        buffer.resize_with(capacity, || None);
        RingBuffer { buffer, head: 0, tail: 0, count: 0, capacity }
    }

    pub fn enqueue(&mut self, item: T) -> bool {
        if self.count == self.capacity { return false; }
        self.buffer[self.tail] = Some(item);
        self.tail = (self.tail + 1) % self.capacity;
        self.count += 1;
        true
    }

    pub fn dequeue(&mut self) -> Option<T> {
        if self.count == 0 { return None; }
        let item = self.buffer[self.head].take();
        self.head = (self.head + 1) % self.capacity;
        self.count -= 1;
        item
    }

    pub fn len(&self) -> usize { self.count }
    pub fn is_full(&self) -> bool { self.count == self.capacity }
}
```

```go [Go]
type RingBuffer[T any] struct {
	buf  []T
	head int
	tail int
	cnt  int
	cap  int
}

func NewRingBuffer[T any](capacity int) *RingBuffer[T] {
	return &RingBuffer[T]{buf: make([]T, capacity), cap: capacity}
}

func (r *RingBuffer[T]) Enqueue(item T) bool {
	if r.cnt == r.cap { return false }
	r.buf[r.tail] = item
	r.tail = (r.tail + 1) % r.cap
	r.cnt++
	return true
}

func (r *RingBuffer[T]) Dequeue() (T, bool) {
	var zero T
	if r.cnt == 0 { return zero, false }
	item := r.buf[r.head]
	r.head = (r.head + 1) % r.cap
	r.cnt--
	return item, true
}

func (r *RingBuffer[T]) Len() int { return r.cnt }
```

```python [Python]
class RingBuffer:
    def __init__(self, capacity: int):
        self._buf = [None] * capacity
        self._head = 0
        self._tail = 0
        self._count = 0
        self._cap = capacity

    def enqueue(self, item) -> bool:
        if self._count == self._cap:
            return False
        self._buf[self._tail] = item
        self._tail = (self._tail + 1) % self._cap
        self._count += 1
        return True

    def dequeue(self):
        if self._count == 0:
            return None
        item = self._buf[self._head]
        self._head = (self._head + 1) % self._cap
        self._count -= 1
        return item

    def __len__(self):
        return self._count
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai ring buffer với enqueue/dequeue | `exercises/typescript/ring-buffer/01-basic.test.ts` |
| Trung bình | Streaming moving average qua N giá trị cuối | `exercises/typescript/ring-buffer/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/ring_buffer/mod.rs` · Go `exercises/go/ring_buffer/ring_buffer_test.go` · Python `exercises/python/ring_buffer/test_ring_buffer.py`

## Khi nào nên dùng

- **Queue kích thước cố định** — buffer producer-consumer giới hạn
- **Dữ liệu streaming** — log buffer, frame audio/video, gói mạng
- **Concurrency lock-free** — với head/tail atomic, cho queue SPSC wait-free
- **Ngữ nghĩa ghi đè cũ nhất** — telemetry, cache N gần nhất
- **Nhúng / realtime** — không cấp phát heap, timing xác định

## Khi nào KHÔNG nên dùng

- **Tăng không giới hạn** — nếu không đoán được kích thước max, dùng linked list hoặc `Vec`/`deque`
- **Truy cập ngẫu nhiên theo key** — ring buffer tuần tự; dùng hash map
- **Phần tử kích thước thay đổi** — đóng gói item kích thước khác phức tạp; dùng message queue

## Thêm các ứng dụng production

- Linux [io_uring](https://github.com/axboe/liburing)
- [ZeroMQ](https://github.com/zeromq/libzmq)
- [Kafka](https://github.com/apache/kafka) — segment log
- [PortAudio](https://github.com/portaudio/portaudio/blob/b0fe9de7ec86ebe5a26086f1d662ab74d7ebfae4/src/common/pa_ringbuffer.c) — ring buffer SPSC lock-free cho audio realtime

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Backpressure](/patterns/backpressure/) | Ring buffer giới hạn tự nhiên tạo backpressure khi đầy |
| [Event Loop](/patterns/event-loop/) | Event loop dùng ring buffer cho queue event I/O |
| [Double Buffering](/patterns/double-buffering/) | Cả hai tránh cấp phát — ring buffer tái dùng slot, double buffering hoán đổi con trỏ |
| [Batch Processing](/patterns/batch-processing/) | Ring buffer gom event cho tiêu thụ theo lô |
| [Free List](/patterns/free-list/) | Cả hai cung cấp quản lý slot O(1) — ring buffer qua index modulo, free list qua chuỗi liên kết |

## Câu hỏi thử thách

::: details Câu 1: Bạn triển khai ring buffer capacity 8, nhưng không có trường `count` riêng — chỉ theo `head` và `tail`. Khi `head === tail`, không phân biệt được buffer đầy hay rỗng. Hệ thống production giải thế nào?
**Trả lời:** Cách phổ biến nhất là hoặc giữ count riêng, hoặc cấp phát capacity + 1 slot và coi `(tail + 1) % capacity === head` là đầy.

Chỉ với `head` và `tail`, cả state rỗng và đầy trông giống nhau (`head === tail`). LMAX Disruptor dùng sequence number tăng đơn điệu thay vì con trỏ vòng, nên `tail - head` cho count trực tiếp. Cách "lãng phí một slot" hy sinh một phần tử capacity nhưng tránh overhead duy trì bộ đếm atomic trong kịch bản đồng thời.
:::

::: details Câu 2: LMAX Disruptor yêu cầu capacity ring buffer là luỹ thừa 2. Đồng nghiệp nói kích thước nào cũng được vì bạn đang dùng `% capacity`. Vì sao LMAX khăng khăng luỹ thừa 2?
**Trả lời:** Kích thước luỹ thừa 2 cho phép thay thao tác modulo bằng bitwise AND (`index & (capacity - 1)`), nhanh hơn đáng kể.

Toán tử modulo `%` compile thành lệnh chia, mất 20-40 chu kỳ CPU trên hầu hết kiến trúc. Bitwise AND mất 1 chu kỳ. Trong hệ thống xử lý 6 triệu event mỗi giây, tối ưu này trên mỗi enqueue và dequeue cộng dồn lại. Chỉ hoạt động vì `n & (2^k - 1)` tương đương toán học với `n % 2^k` khi số chia là luỹ thừa 2.
:::

::: details Câu 3: Hệ logging của bạn dùng ring buffer cho log entry gần nhất. Trong sự cố production, bạn nhận thấy log cũ nhất cần debug đã bị ghi đè. Tăng buffer "đủ lớn" không thực tế. Bạn thay đổi kiến trúc nào?
**Trả lời:** Thêm consumer/drain flush entry vào lưu trữ bền vững trước khi bị ghi đè, biến ring buffer thành vùng staging thay vì store cuối.

Ring buffer vốn dĩ giới hạn — đó là điểm mạnh (bộ nhớ dự đoán được) và giới hạn (mất dữ liệu khi tải lâu dài). Pattern dùng bởi `io_uring` của Linux và trace buffer kernel là có consumer đọc entry và lưu lại. Ring buffer hấp thụ burst, và consumer xử lý throughput ổn định. Việc này tách quan tâm ghi-nhanh khỏi quan tâm lưu-mọi-thứ.
:::

::: details Câu 4: Bạn đang xây ring buffer single-producer, single-consumer (SPSC) cho pipeline audio. Producer ghi 48.000 sample/giây và consumer đọc theo block 1024 sample. Thỉnh thoảng consumer stall 50ms (ví dụ I/O đĩa). Bạn chọn capacity nào, và sai thì sao?
**Trả lời:** Ít nhất 48000 × 0,05 = 2.400 sample để sống sót stall 50ms, làm tròn lên luỹ thừa 2 tiếp theo (4.096). Thực tế, gấp đôi hoặc gấp bốn (8.192 hoặc 16.384) để xử lý stall liên tiếp.

Nếu buffer quá nhỏ, producer ghi đè sample chưa đọc (lỗi âm thanh) hoặc block (pipeline stall). Nếu quá lớn, bạn thêm độ trễ — consumer luôn đọc sample đã ghi từ quá khứ xa hơn. Hệ thống audio thường đặt buffer 2-3x thời lượng stall tối đa kỳ vọng làm biên an toàn. Đây là đánh đổi ring buffer cơ bản: capacity = mức chịu burst tối đa, và mỗi slot thêm cộng một chu kỳ sample vào độ trễ tệ nhất.
:::
