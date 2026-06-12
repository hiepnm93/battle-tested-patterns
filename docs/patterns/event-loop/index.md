---
title: "Pattern: Event Loop / Reactor"
description: "Vòng lặp đơn luồng ghép kênh I/O qua epoll/kqueue, dispatch event sẵn sàng tới callback — hàng nghìn kết nối không cần thread."
difficulty: "intermediate"
---

# Pattern: Event Loop / Reactor

<DifficultyBadge />

## Mô tả một câu

Vòng lặp đơn luồng ghép kênh I/O qua epoll/kqueue, dispatch event sẵn sàng tới callback — hàng nghìn kết nối không cần thread.

<DemoBadge />

## Tương tự thực tế

Một lễ tân xử lý văn phòng bận. Cô ấy không thể nói với hai người gọi cùng lúc, nhưng đặt mỗi người chờ, xử lý task nhanh, và quay lại từng người gọi. Không gì dừng — nếu task tốn thời gian, cô ghi chú và đi tiếp.

## Ý tưởng cốt lõi

Thay vì dành một thread cho mỗi kết nối (context switch tốn, bộ nhớ cao), pattern reactor dùng một thread block trên cơ chế polling OS (`epoll`, `kqueue`, `IOCP`). Khi file descriptor đã đăng ký sẵn sàng, vòng lặp dispatch tới callback liên quan. Đây là cách Node.js xử lý 10.000+ kết nối đồng thời trên một thread.

```text
  ┌─────────────────────────────────────────────────┐
  │                  Event Loop                     │
  │                                                 │
  │  ┌──────────┐    ┌──────────┐    ┌──────────┐   │
  │  │ Đăng ký  │    │  Poll    │    │ Dispatch │   │
  │  │ quan tâm │───►│ (block)  │───►│ handler  │   │
  │  │ (fds)    │    │          │    │ sẵn sàng │   │
  │  └──────────┘    └──────────┘    └────┬─────┘   │
  │       ▲                               │         │
  │       └───────────────────────────────┘         │
  │                   lặp                           │
  └─────────────────────────────────────────────────┘

  Chi tiết pha (mô hình libuv):
  ┌────────┐  ┌──────────┐  ┌──────┐  ┌───────┐  ┌───────┐
  │ Timer  │─►│ Callback │─►│ Poll │─►│ Check │─►│ Close │──► lần tiếp
  │        │  │ pending  │  │      │  │       │  │       │
  └────────┘  └──────────┘  └──────┘  └───────┘  └───────┘
```

| Thuộc tính | Giá trị |
|----------|-------|
| Mô hình concurrency | Đơn luồng, I/O non-blocking |
| Kết nối | Hàng nghìn mỗi thread (giới hạn bởi file descriptor, không phải thread) |
| Độ trễ | Thấp cho việc I/O-bound; một callback chậm chặn tất cả |
| Bộ nhớ | O(kết nối) cho state, không phải O(kết nối * kích thước stack) |

**Thử ngay** — thêm task vào call stack và queue, rồi đi qua thứ tự thực thi event loop:

<EventLoopViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| libuv | [core.c#L427-L492](https://github.com/libuv/libuv/blob/f6b713398e464a9f166328765be1703fd860981f/src/unix/core.c#L427-L492) | `uv_run` (L427-L492) là hàm event loop chính dùng bởi Node.js. Xử lý timer, callback pending, poll I/O (`uv__io_poll`), chạy check handle và đóng handle trong một vòng `while`. Hỗ trợ ba mode chạy: `UV_RUN_DEFAULT` (chạy tới khi không còn handle active), `UV_RUN_ONCE`, `UV_RUN_NOWAIT`. |
| Redis | [ae.c#L360-L468](https://github.com/redis/redis/blob/df63a65d4d4ee33ae67e9f101885074febe0bccb/src/ae.c#L360-L468) | `aeProcessEvents` (L360-L468) là cốt lõi event loop Redis. Tính timer gần nhất, gọi `aeApiPoll` (trừu tượng epoll/kqueue/select) với timeout đó, rồi dispatch event file và event timer. Redis đạt 100K+ ops/giây trên một thread vì event loop không bao giờ block trên thao tác riêng. |

## Triển khai

::: code-group

```typescript [TypeScript]
type Handler = () => void;

class EventLoop {
  private handlers = new Map<number, Handler>();

  /** Đăng ký handler cho file descriptor. */
  addHandler(fd: number, callback: Handler): void {
    this.handlers.set(fd, callback);
  }

  /** Xoá handler cho file descriptor. */
  removeHandler(fd: number): void {
    this.handlers.delete(fd);
  }

  /** Thực thi một tick: gọi mọi handler đã đăng ký một lần. */
  tick(): number {
    const count = this.handlers.size;
    for (const [, handler] of this.handlers) {
      handler();
    }
    return count;
  }

  /** Chạy event loop tới maxTicks. Dừng sớm nếu không có handler. */
  run(maxTicks: number): number {
    let ticksRun = 0;
    for (let i = 0; i < maxTicks; i++) {
      if (this.handlers.size === 0) break;
      this.tick();
      ticksRun++;
    }
    return ticksRun;
  }

  get handlerCount(): number {
    return this.handlers.size;
  }
}
```

```rust [Rust]
use std::collections::HashMap;

pub struct EventLoop {
    handlers: HashMap<i32, Box<dyn FnMut()>>,
}

impl EventLoop {
    pub fn new() -> Self {
        EventLoop { handlers: HashMap::new() }
    }

    pub fn add_handler(&mut self, fd: i32, handler: impl FnMut() + 'static) {
        self.handlers.insert(fd, Box::new(handler));
    }

    pub fn remove_handler(&mut self, fd: i32) {
        self.handlers.remove(&fd);
    }

    pub fn tick(&mut self) -> usize {
        let count = self.handlers.len();
        for handler in self.handlers.values_mut() {
            handler();
        }
        count
    }

    pub fn run(&mut self, max_ticks: usize) -> usize {
        let mut ticks_run = 0;
        for _ in 0..max_ticks {
            if self.handlers.is_empty() {
                break;
            }
            self.tick();
            ticks_run += 1;
        }
        ticks_run
    }
}
```

```go [Go]
type EventLoop struct {
	handlers map[int]func()
}

func NewEventLoop() *EventLoop {
	return &EventLoop{handlers: make(map[int]func())}
}

func (el *EventLoop) AddHandler(fd int, handler func()) {
	el.handlers[fd] = handler
}

func (el *EventLoop) RemoveHandler(fd int) {
	delete(el.handlers, fd)
}

func (el *EventLoop) Tick() int {
	count := len(el.handlers)
	for _, handler := range el.handlers {
		handler()
	}
	return count
}

func (el *EventLoop) Run(maxTicks int) int {
	ticksRun := 0
	for i := 0; i < maxTicks; i++ {
		if len(el.handlers) == 0 {
			break
		}
		el.Tick()
		ticksRun++
	}
	return ticksRun
}
```

```python [Python]
from typing import Callable

class EventLoop:
    def __init__(self) -> None:
        self._handlers: dict[int, Callable[[], None]] = {}

    def add_handler(self, fd: int, callback: Callable[[], None]) -> None:
        self._handlers[fd] = callback

    def remove_handler(self, fd: int) -> None:
        self._handlers.pop(fd, None)

    def tick(self) -> int:
        count = len(self._handlers)
        for handler in list(self._handlers.values()):
            handler()
        return count

    def run(self, max_ticks: int) -> int:
        ticks_run = 0
        for _ in range(max_ticks):
            if not self._handlers:
                break
            self.tick()
            ticks_run += 1
        return ticks_run
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai event loop mini với đăng ký handler và tick/run | `exercises/typescript/event-loop/01-basic.test.ts` |
| Trung bình | Mở rộng với hỗ trợ timer (timer một-lần xen kẽ với I/O) | `exercises/typescript/event-loop/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/event_loop/mod.rs` · Go `exercises/go/event_loop/event_loop_test.go` · Python `exercises/python/event_loop/test_event_loop.py`

## Khi nào nên dùng

- **Server nhiều kết nối** — web server, chat server, API gateway nơi hàng nghìn kết nối phần lớn rảnh (chờ I/O)
- **Tải I/O-bound** — network proxy, load balancer, pool kết nối database nơi việc CPU mỗi request là tối thiểu
- **Giao tiếp realtime** — server WebSocket, server game, hệ thông báo nơi độ trễ thấp mỗi message quan trọng hơn throughput
- **Nhúng/eo hẹp tài nguyên** — khi không thể chịu overhead bộ nhớ một thread mỗi kết nối (mỗi thread = 1-8 MB stack)

## Khi nào KHÔNG nên dùng

- **Việc CPU-bound** — event loop đơn luồng block trên tính toán. Nếu cần hash mật khẩu, resize ảnh hoặc chạy ML inference, dùng thread pool hoặc worker process song song với event loop.
- **Request-response đơn giản** — nếu có < 100 kết nối đồng thời và mỗi request đơn giản, thread-mỗi-request đơn giản hơn và dễ debug. Event loop thêm phức tạp (quản lý callback, state machine) không lợi ích.
- **Yêu cầu thứ tự nghiêm ngặt** — khi event phải xử lý đúng thứ tự đến không xen kẽ, vòng lặp tuần tự hoặc consumer queue đơn giản rõ hơn.

## Thêm các ứng dụng production

- [Node.js](https://github.com/nodejs/node) — event loop dựa trên libuv chạy toàn runtime Node.js
- [Nginx](https://github.com/nginx/nginx) — worker process mỗi cái chạy event loop với epoll/kqueue
- [Tokio](https://github.com/tokio-rs/tokio) — runtime async Rust xây trên mio (reactor đa nền tảng)
- [Netty](https://github.com/netty/netty) — event loop Java NIO cho networking hiệu năng cao

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Cooperative Scheduling](/patterns/cooperative-scheduling/) | Event loop yêu cầu cooperative scheduling — handler không được block |
| [Observer](/patterns/observer/) | Event loop dispatch event tới observer/callback đã đăng ký |
| [Ring Buffer (Buffer vòng)](/patterns/ring-buffer/) | Queue event thường triển khai như ring buffer |
| [Actor Model](/patterns/actor-model/) | Mỗi actor về cơ bản là event loop đơn luồng trên mailbox |
| [Min-Heap / Priority Queue](/patterns/min-heap/) | Event loop dùng min-heap để lập lịch callback timer theo deadline sớm nhất |

## Câu hỏi thử thách

::: details Câu 1: Server Node.js xử lý 5.000 kết nối WebSocket bình thường, nhưng thêm một endpoint tính số Fibonacci chặn TẤT CẢ kết nối. Tại sao?
**Trả lời:** Event loop đơn luồng. Khi tính Fibonacci (CPU-bound, đồng bộ), event loop không thể xử lý event I/O nào. Cả 5.000 kết nối WebSocket bị đông cứng tới khi tính toán xong.

Giải pháp: (1) chuyển việc CPU sang pool `worker_threads`, (2) chia tính toán thành đoạn với `setImmediate()` để yield lại event loop giữa đoạn, (3) dùng microservice riêng cho tính toán nặng. Đây là đánh đổi cơ bản của mô hình event loop — đa nhiệm hợp tác nghĩa một actor xấu chặn mọi người.
:::

::: details Câu 2: Redis dùng event loop đơn luồng cho thực thi command (với I/O thread tuỳ chọn từ Redis 6.0), nhưng xử lý 100K+ thao tác mỗi giây. Sao vậy?
**Trả lời:** Thao tác Redis cực nhanh — hầu hết là tra hash table O(1) hoặc sorted set O(log N) mất microsecond. Overhead event loop không đáng kể so với thời gian I/O mạng.

Nút thắt không phải CPU mà mạng: đọc/ghi socket, parse protocol và serialize response. Vì Redis dùng I/O non-blocking qua `aeProcessEvents`, nó xử lý một command mỗi event (đọc → parse → thực thi → ghi) và lập tức chuyển sang socket sẵn sàng tiếp. Không context switching, không tranh chấp lock, và toàn bộ dataset vừa bộ nhớ — throughput tuần tự thuần.
:::

::: details Câu 3: `uv_run` của libuv có ba mode: DEFAULT, ONCE, NOWAIT. Khi nào dùng mỗi cái?
**Trả lời:**

- **DEFAULT**: Hoạt động bình thường — chạy tới khi mọi handle/request xong. Đây là cái `node app.js` dùng. Process sống tới khi không còn timer, server hoặc callback pending.
- **ONCE**: Xử lý một vòng event rồi trả. Hữu ích khi nhúng libuv trong event loop khác (ví dụ vòng lặp chính của game engine cũng cần xử lý event Node.js).
- **NOWAIT**: Như ONCE nhưng không bao giờ block trên I/O poll. Chỉ xử lý event đã sẵn sàng. Hữu ích cho polling trong vòng lặp chặt nơi block sẽ gây mất frame hoặc deadline.

Khác biệt then chốt: DEFAULT block vô hạn, ONCE block một vòng, NOWAIT không bao giờ block.
:::

::: details Câu 4: Sao Nginx dùng nhiều worker process mỗi cái có event loop riêng, thay vì một event loop duy nhất?
**Trả lời:** Một event loop trên một core CPU lãng phí các core khác. Nginx spawn N worker process (thường một mỗi core CPU), mỗi cái chạy event loop độc lập riêng.

Điều này cho bạn: (1) tận dụng đa core không có bug threading state chia sẻ, (2) cô lập process — một worker crash không kéo cái khác xuống, (3) reload không downtime — worker mới bắt đầu với config mới khi worker cũ rút. Tuỳ chọn socket `SO_REUSEPORT` cho mọi worker accept kết nối trên cùng port, với kernel cân bằng tải qua chúng.
:::
