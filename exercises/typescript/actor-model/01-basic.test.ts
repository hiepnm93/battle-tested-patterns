import { describe, it, expect } from 'vitest';

/**
 * Actor Model - Basic: Implement a simple actor system.
 *
 * TODO: Implement an Actor with a mailbox that processes messages
 * sequentially. Actors communicate by sending messages, never sharing state.
 */

type MessageHandler<S> = (state: S, msg: unknown) => S;

class Actor<S> {
  private state: S;
  private mailbox: unknown[] = [];
  private processing = false;

  constructor(
    initialState: S,
    private handler: MessageHandler<S>,
  ) {
    // TODO: implement
    this.state = initialState;
  }

  send(msg: unknown): void {
    // TODO: implement
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

// ─── Tests (do not modify below this line) ───────────────────────

describe('Actor Model - Basic', () => {
  it('should process messages and update state', () => {
    const counter = new Actor(0, (state: number, msg: unknown) => {
      if (msg === 'inc') return state + 1;
      if (msg === 'dec') return state - 1;
      return state;
    });

    counter.send('inc');
    counter.send('inc');
    counter.send('dec');
    expect(counter.getState()).toBe(1);
  });

  it('should process messages in order', () => {
    const log: string[] = [];
    const logger = new Actor(log, (state: string[], msg: unknown) => {
      state.push(msg as string);
      return state;
    });

    logger.send('first');
    logger.send('second');
    logger.send('third');
    expect(logger.getState()).toEqual(['first', 'second', 'third']);
  });

  it('should isolate state between actors', () => {
    const a = new Actor(0, (s: number) => s + 1);
    const b = new Actor(100, (s: number) => s + 1);

    a.send(null);
    a.send(null);
    b.send(null);

    expect(a.getState()).toBe(2);
    expect(b.getState()).toBe(101);
  });

  it('should handle complex state', () => {
    interface TodoState { items: string[]; count: number }
    const todos = new Actor<TodoState>(
      { items: [], count: 0 },
      (state, msg) => {
        const { action, text } = msg as { action: string; text: string };
        if (action === 'add') {
          return { items: [...state.items, text], count: state.count + 1 };
        }
        return state;
      },
    );

    todos.send({ action: 'add', text: 'Buy milk' });
    todos.send({ action: 'add', text: 'Write code' });

    const state = todos.getState();
    expect(state.items).toEqual(['Buy milk', 'Write code']);
    expect(state.count).toBe(2);
  });
});
