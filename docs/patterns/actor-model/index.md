---
title: "Pattern: Actor Model"
description: "Mỗi actor có mailbox và xử lý thông điệp tuần tự — không state chia sẻ, không lock, chỉ truyền thông điệp cho concurrency an toàn."
difficulty: "advanced"
---

# Pattern: Actor Model

<DifficultyBadge />

## Mô tả một câu

Mỗi actor có mailbox và xử lý thông điệp tuần tự — không state chia sẻ, không lock, chỉ truyền thông điệp cho concurrency an toàn.

<DemoBadge />

## Tương tự thực tế

Đồng nghiệp giao tiếp chỉ qua phong bì niêm phong trong hòm thư. Không ai bước vào văn phòng người khác — bạn viết thông điệp, bỏ vào hòm thư của họ và quay về công việc riêng. Mỗi người xử lý thư từng cái một.

## Ý tưởng cốt lõi

Actor là process nhẹ với state riêng và mailbox (queue thông điệp). Actor giao tiếp duy nhất qua gửi thông điệp bất đồng bộ. Mỗi actor xử lý một thông điệp một lúc, cập nhật state và tuỳ ý gửi thông điệp tới actor khác. Điều này loại bỏ bug concurrency state chia sẻ do thiết kế.

```text
  Actor A                    Actor B                    Actor C
  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
  │ State: count=3   │      │ State: items=[]  │      │ State: total=0   │
  │                  │      │                  │      │                  │
  │ Mailbox:         │      │ Mailbox:         │      │ Mailbox:         │
  │ ┌──┬──┬──┐       │ send │ ┌──┬──┐          │      │ ┌──┐             │
  │ │m1│m2│m3│       │─────►│ │m4│m5│          │      │ │m6│             │
  │ └──┴──┴──┘       │      │ └──┴──┘          │      │ └──┘             │
  │ Xử lý: m1        │      │ Xử lý: m4        │      │ Idle             │
  └──────────────────┘      └──────────────────┘      └──────────────────┘
```

| Thuộc tính | Giá trị |
|----------|-------|
| Concurrency | Không state chia sẻ — chỉ truyền thông điệp |
| Xử lý | Tuần tự mỗi actor (một thông điệp một lúc) |
| Cô lập lỗi | Actor crash không hư hỏng actor khác |
| Khả năng mở rộng | Hàng triệu actor nhẹ (Erlang: 2KB mỗi process) |

**Thử ngay** — gửi thông điệp giữa actor và quan sát xử lý mailbox và cô lập state:

<ActorModelViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| Akka (Scala) | [Actor.scala#L476-L547](https://github.com/akka/akka-core/blob/aded7b67a9dafcb32b8a5dc95f6debce3a97c0e9/akka-actor/src/main/scala/akka/actor/Actor.scala#L476-L547) | `trait Actor` — interface actor cốt lõi. Định nghĩa `context`, `self`, `sender()` và `def receive: Actor.Receive` (L528) nơi mỗi actor Akka chỉ định hành vi xử lý thông điệp qua hàm một phần. `aroundReceive` (L540-L546) là hook dispatch. |
| Erlang/OTP | [erl_process.h#L1043-L1205](https://github.com/erlang/otp/blob/c75602432b4eff922bcaf4a175144dc61adbd6d6/erts/emulator/beam/erl_process.h#L1043-L1205) | `struct process` — biểu diễn của BEAM VM cho process Erlang (actor). Trường then chốt: `sig_qs` (L1107, queue tín hiệu/thông điệp — mailbox), `sig_inq` (L1168, queue input tín hiệu đồng thời), `state` (L1165, cờ state process atomic). Mỗi process là actor nhẹ với heap và mailbox riêng. |

## Triển khai

::: code-group

```typescript [TypeScript]
type MessageHandler<S> = (state: S, msg: unknown) => S;

class Actor<S> {
  private state: S;
  private mailbox: unknown[] = [];
  private processing = false;

  constructor(initialState: S, private handler: MessageHandler<S>) {
    this.state = initialState;
  }

  send(msg: unknown): void {
    this.mailbox.push(msg);
    if (!this.processing) this.processMailbox();
  }

  private processMailbox(): void {
    this.processing = true;
    while (this.mailbox.length > 0) {
      const msg = this.mailbox.shift()!;
      this.state = this.handler(this.state, msg);
    }
    this.processing = false;
  }

  getState(): S {
    return this.state;
  }
}
```

```rust [Rust]
use std::collections::VecDeque;

pub struct Actor<M, S> {
    state: S,
    mailbox: VecDeque<M>,
}

impl<M, S> Actor<M, S> {
    pub fn new(initial_state: S) -> Self {
        Actor { state: initial_state, mailbox: VecDeque::new() }
    }

    pub fn send(&mut self, msg: M) {
        self.mailbox.push_back(msg);
    }

    pub fn process<F>(&mut self, handler: F)
    where F: Fn(&S, M) -> S {
        while let Some(msg) = self.mailbox.pop_front() {
            self.state = handler(&self.state, msg);
        }
    }

    pub fn state(&self) -> &S {
        &self.state
    }
}
```

```go [Go]
type Actor struct {
	state   interface{}
	mailbox chan interface{}
	handler func(state interface{}, msg interface{}) interface{}
}

func NewActor(initial interface{}, handler func(interface{}, interface{}) interface{}) *Actor {
	a := &Actor{
		state:   initial,
		mailbox: make(chan interface{}, 100),
		handler: handler,
	}
	go a.run()
	return a
}

func (a *Actor) Send(msg interface{}) {
	a.mailbox <- msg
}

func (a *Actor) run() {
	for msg := range a.mailbox {
		a.state = a.handler(a.state, msg)
	}
}
```

```python [Python]
from collections import deque
from typing import Any, Callable

class Actor:
    def __init__(self, initial_state: Any, handler: Callable[[Any, Any], Any]):
        self.state = initial_state
        self.handler = handler
        self._mailbox: deque[Any] = deque()
        self._processing = False

    def send(self, msg: Any) -> None:
        self._mailbox.append(msg)
        if not self._processing:
            self._process_mailbox()

    def _process_mailbox(self) -> None:
        self._processing = True
        while self._mailbox:
            msg = self._mailbox.popleft()
            self.state = self.handler(self.state, msg)
        self._processing = False

    def get_state(self) -> Any:
        return self.state
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai actor với mailbox và xử lý thông điệp | `exercises/typescript/actor-model/01-basic.test.ts` |
| Trung bình | Giám sát actor — cha khởi động lại con crash | `exercises/typescript/actor-model/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/actor_model/mod.rs` · Go `exercises/go/actor_model/actor_model_test.go` · Python `exercises/python/actor_model/test_actor_model.py`

## Khi nào nên dùng

- **Hệ phân tán** — actor map tự nhiên tới node mạng (Erlang/OTP, Akka Cluster)
- **Game server** — mỗi entity (player, NPC, phòng) như actor độc lập
- **IoT** — mỗi thiết bị như actor xử lý event sensor
- **Telecom** — nguồn gốc Erlang: hàng triệu phiên gọi đồng thời
- **Hệ chat** — mỗi conversation/room như actor

## Khi nào KHÔNG nên dùng

- **Ghép dữ liệu chặt** — nếu các thành phần cần state mutable chia sẻ, truyền thông điệp thêm độ trễ
- **Request-response đơn giản** — gọi hàm đơn giản hơn roundtrip actor
- **Nặng tính toán, không concurrency** — overhead actor không có lợi ích concurrency
- **Strong consistency** — actor cung cấp eventual consistency; dùng transaction cho ACID

## Thêm các ứng dụng production

- [Orleans (C#)](https://github.com/dotnet/orleans/blob/bab4fb03e99c978ae483c24d0d759f5b93222a74/src/Orleans.Runtime/Catalog/ActivationData.cs#L31-L55) — actor ảo ("grain") với dispatch `RunMessageLoop` ở L980-L1012
- [Proto.Actor (Go)](https://github.com/asynkron/protoactor-go/blob/288962e52f3f59533c8f463fc31f98b8d5d39e41/actor/message.go#L12-L14) — interface `Actor` tối giản với method `Receive(c Context)` đơn
- [Actix (Rust)](https://github.com/actix/actix) — framework actor cho Rust với thông điệp có kiểu
- [Microsoft DAPR](https://github.com/dapr/dapr) — actor ảo cho microservice

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Observer](/patterns/observer/) | Actor giao tiếp qua thông điệp, tương tự pattern publish/subscribe của observer |
| [Event Loop](/patterns/event-loop/) | Mỗi actor xử lý mailbox tuần tự, như event loop đơn luồng |
| [State Machine](/patterns/state-machine/) | Hành vi actor thường theo pattern state machine cho logic nội bộ |

## Câu hỏi thử thách

::: details Câu 1: Actor giao tiếp chỉ qua thông điệp bất đồng bộ, không state chia sẻ hay lock. Đồng nghiệp khẳng định "actor không thể deadlock vì không có lock." Có đúng không?
**Trả lời:** Actor vẫn có thể deadlock qua phụ thuộc thông điệp vòng, dù không có lock.

Nếu Actor A gửi thông điệp tới Actor B và chờ response, trong khi Actor B gửi thông điệp tới Actor A và chờ response, không ai có thể xử lý thông điệp của cái kia — cả hai mailbox chứa thông điệp chưa xử lý cần cái kia tiến hành. Logic tương đương deadlock dựa trên lock. Giảm nhẹ là tránh pattern request-reply đồng bộ giữa actor, dùng timeout trên mọi trao đổi thông điệp, hoặc thiết kế luồng thông điệp như DAG (đồ thị có hướng không chu trình) thay vì vòng.
:::

::: details Câu 2: Hệ actor của bạn có producer nhanh gửi 10.000 thông điệp/giây tới consumer chậm xử lý 100 thông điệp/giây. Mailbox của consumer tăng không giới hạn. Hệ actor nên xử lý back pressure này thế nào?
**Trả lời:** Mailbox giới hạn với tín hiệu back-pressure tường minh — khi mailbox đầy, sender phải hoặc drop thông điệp, block, hoặc nhận tín hiệu từ chối.

Mailbox không giới hạn là cạm bẫy phổ biến trong hệ actor — chúng đánh đổi bộ nhớ lấy liveness, cuối cùng gây crash OOM. Akka cung cấp `BoundedMailbox` block sender khi đầy, và flow-control qua Akka Streams (back-pressure reactive streams). Process Erlang có mailbox không giới hạn theo thiết kế nhưng dựa vào cây giám sát OTP để khởi động lại process tiêu thụ quá nhiều bộ nhớ. Insight kiến trúc là back-pressure là quan tâm thiết kế hệ thống, không chỉ quan tâm actor — bạn cần quyết định ở mỗi ranh giới producer-consumer chuyện gì xảy ra khi consumer không theo kịp.
:::

::: details Câu 3: Actor xử lý thông điệp thanh toán crash giữa chừng do bug. Thanh toán đã xử lý một phần (tiền bị trừ nhưng chưa cộng). Erlang/OTP xử lý actor crash mà không hư hỏng hệ thống thế nào?
**Trả lời:** Cây giám sát OTP khởi động lại actor crash với state tươi — insight then chốt là state actor là tạm và nguồn sự thật sống ở nơi khác (database, log thông điệp).

Triết lý "cứ để crash" của Erlang nghĩa actor không cố phục hồi từ lỗi bất ngờ — chúng chết, và process supervisor khởi động lại. Nhưng chỉ hoạt động nếu side effect của actor hoặc idempotent hoặc transactional. Cho case thanh toán, debit và credit nên bọc trong transaction database, hoặc actor nên dùng pattern outbox: ghi ý định vào log bền vững trước, rồi thực thi. Nếu crash giữa chừng, actor được khởi động lại replay log. Mô hình actor cô lập crash (actor khác không ảnh hưởng), nhưng bền vững và consistency vẫn cần thiết kế tường minh.
:::

::: details Câu 4: Erlang có thể chạy hàng triệu actor (process) trên một máy, mỗi cái chỉ ~2KB bộ nhớ. Triển khai Go trong doc này dùng goroutine với mailbox channel. Bạn có thể chạy 1 triệu actor Go cùng cách không?
**Trả lời:** Có cho số goroutine (Go hỗ trợ hàng triệu goroutine), nhưng mỗi channel trong triển khai cấp phát buffer 100 phần tử, và overhead channel kết hợp đáng kể.

Goroutine bắt đầu ở stack 2KB (từ Go 1.4), nên 1 triệu goroutine tốn ~2GB bộ nhớ stack riêng. Mỗi buffered channel thêm size buffer nhân size phần tử. Từ Go 1.14, goroutine được preempt bất đồng bộ qua signal, nên actor CPU-bound không bỏ đói actor khác. Khác biệt sâu hơn là garbage collection per-process của Erlang — pause GC mỗi actor độc lập và quy mô microsecond. GC Go toàn cục nhưng đồng thời, với pause STW thường dưới millisecond (thường dưới 100μs từ Go 1.8+). Đánh đổi thực là GC per-process Erlang giữ tác động pause cục bộ, trong khi GC đồng thời Go duyệt cả heap — đáng kể ở số actor cực lớn. Cho số actor thực sự khủng, BEAM VM của Erlang được xây cho mục đích này; Go có thể xấp xỉ nhưng với đánh đổi GC khác.
:::
