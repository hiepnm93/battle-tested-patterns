---
title: "Pattern: Backpressure / Kiểm soát luồng"
description: "Làm chậm producer khi consumer không theo kịp — dùng buffer giới hạn và tín hiệu demand để tránh cạn kiệt tài nguyên."
difficulty: "intermediate"
---

# Pattern: Backpressure / Kiểm soát luồng

<DifficultyBadge />

## Mô tả một câu

Làm chậm producer khi consumer không theo kịp — dùng buffer giới hạn và tín hiệu demand để tránh cạn kiệt tài nguyên.

<DemoBadge />

## Tương tự thực tế

Bồi bàn nói với bếp 'chậm lại, bàn đầy rồi.' Thay vì xếp chồng đĩa nguội, bồi báo bếp giảm output cho tới khi khách ăn xong. Consumer kiểm soát nhịp của producer.

## Ý tưởng cốt lõi

Backpressure là cơ chế kiểm soát luồng nơi consumer báo producer chậm lại hoặc dừng. Không có nó, producer nhanh làm choáng ngợp consumer chậm, gây bộ nhớ tăng không giới hạn, mất thông điệp hoặc crash hệ thống. Then chốt: **buffer giới hạn** + **block/tín hiệu khi đầy**.

```text
  Producer                     Bounded Buffer                Consumer
  ─────────                   ──────────────                ─────────
  emit(data) ──────────►  ┌──┬──┬──┬──┬──┐  ──────────►  process(data)
                          │ 5│ 4│ 3│ 2│ 1│
  ◄─ WAIT (buffer đầy)    └──┴──┴──┴──┴──┘  request(n) ──►
                            capacity = 5
```

| Chiến lược | Cách hoạt động |
|----------|-------------|
| **Block** | Producer chờ đến khi buffer còn chỗ (channel Go, stream Node.js) |
| **Drop** | Bỏ item mới/cũ nhất khi buffer đầy (mất dữ liệu, cho metric) |
| **Signal** | Consumer gửi `request(n)` để pull đúng n item (Reactive Streams) |
| **Throttle** | Rate-limit producer (token bucket / leaky bucket) |

| Thuộc tính | Giá trị |
|----------|-------|
| Overhead tín hiệu | O(1) — flag boolean hoặc kiểm tra counter |
| Giới hạn buffer | Capacity cố định — tránh bộ nhớ tăng không giới hạn |
| Throughput | Tự điều chỉnh theo tốc độ consumer |
| Đánh đổi độ trễ | Tăng khi tải cao — producer chờ thay vì drop |

**Thử ngay** — khởi động producer và consumer để xem chuyện gì khi sản xuất vượt tiêu thụ:

<BackpressureViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| Node.js Streams | [writable.js#L548-L585](https://github.com/nodejs/node/blob/19c46abbefdb8711b913d7237b3c1299367f87d7/lib/internal/streams/writable.js#L548-L585) | `writeOrBuffer()` — L576 kiểm tra `state.length < state.highWaterMark`; khi buffer vượt ngưỡng, L579 đặt cờ `kNeedDrain` và L585 trả `false`, tín hiệu cho producer tạm dừng cho tới khi event `drain` bắn. |
| Reactive Streams | [Subscription.java#L14-L37](https://github.com/reactive-streams/reactive-streams-jvm/blob/a625d3aba756e9842ad1291a5b73f5db280b6168/api/src/main/java/org/reactivestreams/Subscription.java#L14-L37) | `request(long n)` (L29) — consumer tường minh yêu cầu `n` item từ producer. "Không event nào được gửi bởi Publisher cho tới khi demand được tín hiệu qua method này." Nền tảng của RxJava Flowable, Project Reactor và Akka Streams. |

## Triển khai

::: code-group

```typescript [TypeScript]
class BoundedQueue<T> {
  private buffer: T[] = [];
  private pushWaiters: Array<() => void> = [];
  private pullWaiters: Array<(value: T) => void> = [];

  constructor(private capacity: number) {}

  async push(item: T): Promise<void> {
    if (this.pullWaiters.length > 0) {
      this.pullWaiters.shift()!(item);
      return;
    }
    if (this.buffer.length >= this.capacity) {
      await new Promise<void>((r) => this.pushWaiters.push(r));
    }
    this.buffer.push(item);
  }

  async pull(): Promise<T> {
    if (this.buffer.length > 0) {
      const item = this.buffer.shift()!;
      if (this.pushWaiters.length > 0) this.pushWaiters.shift()!();
      return item;
    }
    return new Promise<T>((r) => this.pullWaiters.push(r));
  }
}
```

```rust [Rust]
use std::sync::{Arc, Mutex, Condvar};

pub struct BoundedQueue<T> {
    data: Mutex<Vec<T>>,
    capacity: usize,
    not_full: Condvar,
    not_empty: Condvar,
}

impl<T> BoundedQueue<T> {
    pub fn new(capacity: usize) -> Self {
        BoundedQueue {
            data: Mutex::new(Vec::new()),
            capacity,
            not_full: Condvar::new(),
            not_empty: Condvar::new(),
        }
    }

    pub fn push(&self, item: T) {
        let mut buf = self.data.lock().unwrap();
        while buf.len() >= self.capacity {
            buf = self.not_full.wait(buf).unwrap();
        }
        buf.push(item);
        self.not_empty.notify_one();
    }

    pub fn pull(&self) -> T {
        let mut buf = self.data.lock().unwrap();
        while buf.is_empty() {
            buf = self.not_empty.wait(buf).unwrap();
        }
        let item = buf.remove(0);
        self.not_full.notify_one();
        item
    }
}
```

```go [Go]
// Go: bounded channel cung cấp backpressure tự nhiên
func producer(ch chan<- int) {
	for i := 0; ; i++ {
		ch <- i // block khi channel đầy
	}
}

func consumer(ch <-chan int) {
	for v := range ch {
		fmt.Println(v) // xử lý theo nhịp consumer
	}
}

func Run() {
	ch := make(chan int, 10) // buffer giới hạn 10
	go producer(ch)
	consumer(ch)
}
```

```python [Python]
import asyncio

async def producer(queue: asyncio.Queue[int]):
    for i in range(100):
        await queue.put(i)  # block khi queue đầy

async def consumer(queue: asyncio.Queue[int]):
    while True:
        item = await queue.get()  # block khi queue rỗng
        await asyncio.sleep(0.1)  # giả lập xử lý chậm

async def main():
    queue: asyncio.Queue[int] = asyncio.Queue(maxsize=5)  # giới hạn
    await asyncio.gather(producer(queue), consumer(queue))
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai queue async giới hạn với flow control | `exercises/typescript/backpressure/01-basic.test.ts` |
| Trung bình | Channel async giới hạn với gửi/nhận block | `exercises/typescript/backpressure/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/backpressure/mod.rs` · Go `exercises/go/backpressure/backpressure_test.go` · Python `exercises/python/backpressure/test_backpressure.py`

## Khi nào nên dùng

- **Xử lý stream** — tránh nguồn dữ liệu nhanh làm choáng ngợp processor
- **Microservice** — bảo vệ service downstream khỏi quá tải
- **Pipeline I/O** — đọc đĩa nhanh hơn ghi mạng (hoặc ngược lại)
- **Hệ thống hướng sự kiện** — producer bắn event nhanh hơn handler xử lý

## Khi nào KHÔNG nên dùng

- **Chấp nhận mất dữ liệu** — nếu drop ok (metric, sampling), cứ drop không block
- **Hệ thống cùng tốc độ** — producer và consumer chạy cùng nhịp, backpressure thêm phức tạp không cần
- **Fire-and-forget** — nếu producer không cần chờ, dùng queue không giới hạn với giám sát
- **Ràng buộc realtime** — block producer có thể vi phạm SLA độ trễ

## Thêm các ứng dụng production

- [RxJava Flowable](https://github.com/ReactiveX/RxJava) — reactive stream nhận biết backpressure
- [Kafka](https://github.com/apache/kafka) — `buffer.memory` và `max.block.ms` của producer cho flow control
- [Linux TCP](https://github.com/torvalds/linux/blob/acb7500801e98639f6d8c2d796ed9f64cba83d3a/net/ipv4/tcp_output.c) — cửa sổ tắc nghẽn (`cwnd`) như backpressure
- [gRPC](https://github.com/grpc/grpc) — cửa sổ flow control trong HTTP/2

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Ring Buffer (Buffer vòng)](/patterns/ring-buffer/) | Ring buffer giới hạn là cơ chế phổ biến để triển khai backpressure |
| [Rate Limiter (Token Bucket)](/patterns/rate-limiter/) | Rate limit kiểm soát tốc độ nạp; backpressure tín hiệu cho producer chậm lại |
| [Semaphore](/patterns/semaphore/) | Semaphore có thể triển khai backpressure bằng cách giới hạn việc đang xử lý |
| [Batch Processing](/patterns/batch-processing/) | Batching làm mịn input bursty, bổ sung cho cơ chế backpressure |

## Câu hỏi thử thách

::: details Câu 1: Queue giới hạn của bạn đầy. Nên block producer hay drop item mới nhất? Quyết định thế nào?
**Trả lời:** Tuỳ việc mất dữ liệu có chấp nhận được không. Block khi mọi item đều quan trọng (giao dịch tài chính, hành động người dùng). Drop khi tươi quan trọng hơn đầy đủ (metric, telemetry sensor).

Block giữ mọi dữ liệu nhưng lan độ chậm lên upstream — nếu consumer chậm vĩnh viễn, producer stall và toàn pipeline dừng. Drop mất dữ liệu nhưng giữ producer phản hồi. Một lai phổ biến là "drop cũ nhất" cho dashboard giám sát (bạn muốn đọc mới nhất) và "block" cho event sourcing (không thể mất event). Lựa chọn là quyết định nghiệp vụ, không phải kỹ thuật.
:::

::: details Câu 2: Bạn đặt highWaterMark stream Node.js 1MB. Traffic tăng đột biến và bộ nhớ nhảy lên 500MB với 500 stream đồng thời. Có gì sai?
**Trả lời:** Mỗi stream cấp phát buffer kích thước highWaterMark riêng, nên 500 stream x 1MB = 500MB bộ nhớ buffer. highWaterMark là per-stream, không phải toàn cục.

highWaterMark không phải giới hạn toàn hệ thống — đó là ngưỡng mỗi stream tại đó `write()` trả `false`. Với nhiều stream đồng thời, tổng bộ nhớ là `concurrency x highWaterMark`. Cách sửa: hạ highWaterMark (16KB-64KB là điển hình), giới hạn concurrency, hoặc dùng budget bộ nhớ toàn cục động điều chỉnh ngưỡng mỗi stream.
:::

::: details Câu 3: Backpressure khác rate limit thế nào? Đồng đội nói chúng giống nhau.
**Trả lời:** Rate limit cap throughput ở tốc độ cố định bất kể khả năng consumer. Backpressure điều chỉnh động dựa trên khả năng thực sự của consumer.

Rate limit nói "tối đa 100 request/giây" kể cả nếu consumer xử lý được 200. Backpressure nói "gửi nhanh như consumer xử lý được, bất kể tốc độ đó là gì ngay bây giờ." Rate limit là chính sách; backpressure là cơ chế phản hồi. Chúng có thể bổ sung: rate limit ở API gateway, backpressure trong pipeline xử lý. Nhưng chúng giải các bài toán khác — rate limit chống lạm dụng, backpressure tránh cạn tài nguyên.
:::

::: details Câu 4: Một dev Go nói "tôi không cần backpressure, tôi chỉ dùng buffered channel." Có đúng không?
**Trả lời:** Buffered channel CHÍNH LÀ backpressure. Channel giới hạn block sender khi đầy, đó chính xác là chiến lược backpressure "block".

Dev đó đã dùng backpressure rồi — chỉ không nhận ra bằng tên. `ch := make(chan int, 10)` tạo buffer giới hạn 10. Khi buffer đầy, `ch <- item` block goroutine, làm chậm producer khớp consumer. Câu hỏi then chốt là kích thước buffer có được chọn tốt: quá nhỏ thì block không cần khi burst nhỏ; quá lớn thì trì hoãn tín hiệu phản hồi, cho bộ nhớ tăng.
:::
