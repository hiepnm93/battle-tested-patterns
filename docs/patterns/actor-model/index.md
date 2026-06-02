# Pattern: Actor Model

## One Liner

Each actor has a mailbox and processes messages sequentially — no shared state, no locks, just message passing for safe concurrency.

## Core Idea

An actor is a lightweight process with private state and a mailbox (message queue). Actors communicate exclusively by sending asynchronous messages. Each actor processes one message at a time, updating its state and optionally sending messages to other actors. This eliminates shared-state concurrency bugs by design.

```text
  Actor A                    Actor B                    Actor C
  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
  │ State: count=3   │      │ State: items=[]  │      │ State: total=0   │
  │                  │      │                  │      │                  │
  │ Mailbox:         │      │ Mailbox:         │      │ Mailbox:         │
  │ ┌──┬──┬──┐       │ send │ ┌──┬──┐          │      │ ┌──┐             │
  │ │m1│m2│m3│       │─────►│ │m4│m5│          │      │ │m6│             │
  │ └──┴──┴──┘       │      │ └──┴──┘          │      │ └──┘             │
  │ Processing: m1   │      │ Processing: m4   │      │ Idle             │
  └──────────────────┘      └──────────────────┘      └──────────────────┘
```

| Property | Value |
|----------|-------|
| Concurrency | No shared state — message passing only |
| Processing | Sequential per actor (one message at a time) |
| Failure isolation | Actor crash doesn't corrupt other actors |
| Scalability | Millions of lightweight actors (Erlang: 2KB per process) |

## Production Proof

| Project | Source | Usage |
|---------|--------|-------|
| Akka (Scala) | [Actor.scala#L476-L547](https://github.com/akka/akka/blob/main/akka-actor/src/main/scala/akka/actor/Actor.scala#L476-L547) | `trait Actor` — the core actor interface. Defines `context`, `self`, `sender()`, and `def receive: Actor.Receive` (L528) where every Akka actor specifies its message-handling behavior via a partial function. `aroundReceive` (L540-L546) is the dispatch hook. |
| Erlang/OTP | [erl_process.h#L1043-L1205](https://github.com/erlang/otp/blob/master/erts/emulator/beam/erl_process.h#L1043-L1205) | `struct process` — the BEAM VM's representation of an Erlang process (actor). Key fields: `sig_qs` (L1107, signal/message queues — the mailbox), `sig_inq` (L1168, concurrent signal input queue), `state` (L1165, atomic process state flags). Each process is a lightweight actor with its own heap and mailbox. |

## Implementation

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

## Exercises

| Level | Exercise | File |
|-------|----------|------|
| Basic | Implement an actor with mailbox and message processing | `exercises/typescript/actor-model/01-basic.test.ts` |

Run exercises: `pnpm test`

## When to Use

- **Distributed systems** — actors map naturally to network nodes (Erlang/OTP, Akka Cluster)
- **Game servers** — each entity (player, NPC, room) as an independent actor
- **IoT** — each device as an actor processing sensor events
- **Telecom** — Erlang's origin: millions of concurrent call sessions
- **Chat systems** — each conversation/room as an actor

## When NOT to Use

- **Tight data coupling** — if components need shared mutable state, message passing adds latency
- **Simple request-response** — a function call is simpler than an actor roundtrip
- **Computation-heavy, no concurrency** — actor overhead without concurrency benefit
- **Strong consistency** — actors provide eventual consistency; use transactions for ACID

## More Production Uses

- [Orleans (C#)](https://github.com/dotnet/orleans/blob/main/src/Orleans.Runtime/Catalog/ActivationData.cs#L31-L55) — virtual actor ("grain") with `RunMessageLoop` dispatch at L980-L1012
- [Proto.Actor (Go)](https://github.com/asynkron/protoactor-go/blob/dev/actor/message.go#L12-L14) — minimal `Actor` interface with single `Receive(c Context)` method
- [Actix (Rust)](https://github.com/actix/actix) — actor framework for Rust with typed messages
- [Microsoft DAPR](https://github.com/dapr/dapr) — virtual actors for microservices
