# 模式：Actor 模型

## 一句话

每个 Actor 拥有一个信箱并按顺序处理消息——没有共享状态，没有锁，仅通过消息传递实现安全并发。

## 核心思想

Actor 是拥有私有状态和信箱（消息队列）的轻量级进程。Actor 之间仅通过发送异步消息通信。每个 Actor 一次处理一条消息，更新状态并可选地向其他 Actor 发送消息。这从设计上消除了共享状态并发 bug。

```text
  Actor A                    Actor B                    Actor C
  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
  │ State: count=3   │      │ State: items=[]  │      │ State: total=0   │
  │                  │      │                  │      │                  │
  │ 信箱:            │      │ 信箱:            │      │ 信箱:            │
  │ ┌──┬──┬──┐       │ send │ ┌──┬──┐          │      │ ┌──┐             │
  │ │m1│m2│m3│       │─────►│ │m4│m5│          │      │ │m6│             │
  │ └──┴──┴──┘       │      │ └──┴──┘          │      │ └──┘             │
  │ 处理中: m1       │      │ 处理中: m4       │      │ 空闲             │
  └──────────────────┘      └──────────────────┘      └──────────────────┘
```

| 属性 | 值 |
|------|------|
| 并发 | 无共享状态 — 仅消息传递 |
| 处理 | 每个 Actor 串行（一次一条消息） |
| 故障隔离 | Actor 崩溃不会损坏其他 Actor |
| 可扩展性 | 数百万轻量级 Actor（Erlang: 每进程 2KB） |

## 生产验证

| 项目 | 源码 | 用途 |
|------|------|------|
| Akka (Scala) | [Actor.scala#L476-L547](https://github.com/akka/akka/blob/main/akka-actor/src/main/scala/akka/actor/Actor.scala#L476-L547) | `trait Actor` — 核心 Actor 接口。定义 `context`、`self`、`sender()` 和 `def receive: Actor.Receive`（L528），每个 Akka Actor 通过偏函数指定其消息处理行为。`aroundReceive`（L540-L546）是分发钩子。 |
| Erlang/OTP | [erl_process.h#L1043-L1205](https://github.com/erlang/otp/blob/master/erts/emulator/beam/erl_process.h#L1043-L1205) | `struct process` — BEAM 虚拟机中 Erlang 进程（Actor）的表示。关键字段：`sig_qs`（L1107，信号/消息队列 — 信箱）、`sig_inq`（L1168，并发信号输入队列）、`state`（L1165，原子进程状态标志）。每个进程是拥有自己堆和信箱的轻量级 Actor。 |

## 实现

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

```rust [Rust]
pub struct Actor<S> {
    state: S,
    mailbox: Vec<Box<dyn std::any::Any>>,
}

impl<S> Actor<S> {
    pub fn new(initial_state: S) -> Self {
        Actor { state: initial_state, mailbox: Vec::new() }
    }

    pub fn send<M: std::any::Any>(&mut self, msg: M) {
        self.mailbox.push(Box::new(msg));
    }

    pub fn process<F>(&mut self, handler: F)
    where F: Fn(&S, &dyn std::any::Any) -> S {
        while let Some(msg) = if self.mailbox.is_empty() { None } else { Some(self.mailbox.remove(0)) } {
            self.state = handler(&self.state, msg.as_ref());
        }
    }

    pub fn state(&self) -> &S {
        &self.state
    }
}
```

:::

## 练习

| 难度 | 练习 | 文件 |
|------|------|------|
| 基础 | 实现带信箱和消息处理的 Actor | `exercises/typescript/actor-model/01-basic.test.ts` |

## 何时使用

- **分布式系统** — Actor 自然映射到网络节点（Erlang/OTP、Akka Cluster）
- **游戏服务器** — 每个实体（玩家、NPC、房间）作为独立 Actor
- **物联网** — 每个设备作为处理传感器事件的 Actor
- **电信** — Erlang 的起源：数百万并发通话会话
- **聊天系统** — 每个对话/聊天室作为一个 Actor

## 何时不用

- **紧密数据耦合** — 组件需要共享可变状态时，消息传递增加延迟
- **简单请求-响应** — 函数调用比 Actor 往返更简单
- **计算密集无并发** — 没有并发收益的 Actor 开销
- **强一致性** — Actor 提供最终一致性；ACID 需要事务

## 更多生产案例

- [Orleans (C#)](https://github.com/dotnet/orleans/blob/main/src/Orleans.Runtime/Catalog/ActivationData.cs#L31-L55) — 虚拟 Actor（"grain"），`RunMessageLoop` 消息分发在 L980-L1012
- [Proto.Actor (Go)](https://github.com/asynkron/protoactor-go/blob/dev/actor/message.go#L12-L14) — 极简 `Actor` 接口，仅一个 `Receive(c Context)` 方法
- [Actix (Rust)](https://github.com/actix/actix) — Rust 的类型化消息 Actor 框架
- [Microsoft DAPR](https://github.com/dapr/dapr) — 微服务的虚拟 Actor
