import { describe, it, expect } from 'vitest';

/**
 * Checkpointing - Basic: WAL with checkpoint and recovery.
 *
 * TODO: Implement a CheckpointableStore that:
 * - apply(op, key, value): logs to WAL and applies to state
 * - takeCheckpoint(): snapshots current state + WAL position
 * - simulateCrash(): wipes in-memory state
 * - recover(): restores from checkpoint + replays post-checkpoint WAL entries
 */

interface LogEntry {
  id: number;
  operation: string;
  data: Record<string, unknown>;
}

class CheckpointableStore {
  private state: Map<string, unknown> = new Map();
  private wal: LogEntry[] = [];
  private nextId = 1;
  private checkpoint: { state: Map<string, unknown>; walPosition: number } | null = null;

  apply(operation: string, key: string, value: unknown): void {
    // TODO: log to WAL then apply
    const entry: LogEntry = {
      id: this.nextId++,
      operation,
      data: { key, value },
    };
    this.wal.push(entry);
    this.executeOp(entry);
  }

  get(key: string): unknown {
    return this.state.get(key);
  }

  takeCheckpoint(): void {
    // TODO: snapshot state and WAL position
    this.checkpoint = {
      state: new Map(this.state),
      walPosition: this.wal.length,
    };
  }

  simulateCrash(): void {
    // TODO: wipe state but keep WAL and checkpoint
    this.state = new Map();
  }

  recover(): number {
    // TODO: restore from checkpoint, replay only post-checkpoint entries
    if (this.checkpoint) {
      this.state = new Map(this.checkpoint.state);
      let replayed = 0;
      for (let i = this.checkpoint.walPosition; i < this.wal.length; i++) {
        this.executeOp(this.wal[i]!);
        replayed++;
      }
      return replayed;
    }
    this.state = new Map();
    for (const entry of this.wal) {
      this.executeOp(entry);
    }
    return this.wal.length;
  }

  private executeOp(entry: LogEntry): void {
    const { key, value } = entry.data as { key: string; value: unknown };
    if (entry.operation === 'SET') {
      this.state.set(key, value);
    } else if (entry.operation === 'DELETE') {
      this.state.delete(key);
    }
  }

  get walLength(): number { return this.wal.length; }
  get stateSize(): number { return this.state.size; }
}

// ─── Tests (do not modify below this line) ───────────────────────

describe('Checkpointing - Basic', () => {
  it('should apply operations to state via WAL', () => {
    const store = new CheckpointableStore();
    store.apply('SET', 'x', 10);
    store.apply('SET', 'y', 20);

    expect(store.get('x')).toBe(10);
    expect(store.get('y')).toBe(20);
    expect(store.walLength).toBe(2);
  });

  it('should recover entire WAL when no checkpoint exists', () => {
    const store = new CheckpointableStore();
    store.apply('SET', 'a', 1);
    store.apply('SET', 'b', 2);
    store.apply('SET', 'c', 3);

    store.simulateCrash();
    expect(store.get('a')).toBeUndefined();

    const replayed = store.recover();
    expect(replayed).toBe(3);
    expect(store.get('a')).toBe(1);
    expect(store.get('b')).toBe(2);
    expect(store.get('c')).toBe(3);
  });

  it('should replay only post-checkpoint entries on recovery', () => {
    const store = new CheckpointableStore();
    store.apply('SET', 'a', 1);
    store.apply('SET', 'b', 2);
    store.takeCheckpoint(); // checkpoint at position 2

    store.apply('SET', 'c', 3);
    store.apply('SET', 'd', 4);

    store.simulateCrash();
    const replayed = store.recover();

    expect(replayed).toBe(2); // only c and d
    expect(store.get('a')).toBe(1); // from checkpoint
    expect(store.get('b')).toBe(2); // from checkpoint
    expect(store.get('c')).toBe(3); // replayed
    expect(store.get('d')).toBe(4); // replayed
  });

  it('should handle DELETE operations across checkpoint', () => {
    const store = new CheckpointableStore();
    store.apply('SET', 'x', 100);
    store.takeCheckpoint();

    store.apply('DELETE', 'x', null);

    store.simulateCrash();
    store.recover();

    expect(store.get('x')).toBeUndefined();
  });

  it('should handle multiple checkpoints — use the latest', () => {
    const store = new CheckpointableStore();
    store.apply('SET', 'a', 1);
    store.takeCheckpoint(); // checkpoint 1

    store.apply('SET', 'b', 2);
    store.takeCheckpoint(); // checkpoint 2 (replaces 1)

    store.apply('SET', 'c', 3);

    store.simulateCrash();
    const replayed = store.recover();

    expect(replayed).toBe(1); // only 'c'
    expect(store.get('a')).toBe(1);
    expect(store.get('b')).toBe(2);
    expect(store.get('c')).toBe(3);
  });

  it('should recover nothing when checkpoint is at WAL end', () => {
    const store = new CheckpointableStore();
    store.apply('SET', 'x', 1);
    store.takeCheckpoint();

    store.simulateCrash();
    const replayed = store.recover();

    expect(replayed).toBe(0);
    expect(store.get('x')).toBe(1); // from checkpoint
  });

  it('should handle overwrites correctly', () => {
    const store = new CheckpointableStore();
    store.apply('SET', 'counter', 0);
    store.takeCheckpoint();

    store.apply('SET', 'counter', 1);
    store.apply('SET', 'counter', 2);

    store.simulateCrash();
    store.recover();

    expect(store.get('counter')).toBe(2);
  });
});
