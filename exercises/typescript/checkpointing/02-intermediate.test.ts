import { describe, it, expect } from 'vitest';

/**
 * Checkpointing - Intermediate: Incremental checkpoint (only dirty pages).
 *
 * TODO: Implement an IncrementalCheckpointStore that:
 * - Tracks which keys have been modified since last checkpoint ("dirty" keys)
 * - takeCheckpoint() only saves dirty keys to the checkpoint, not the entire state
 * - Maintains a base snapshot + incremental diffs
 * - recover() applies base snapshot + all incremental diffs + remaining WAL
 *
 * Real-world use: PostgreSQL incremental checkpoint (only write dirty buffers),
 * Redis RDB-AOF hybrid persistence.
 */

interface LogEntry {
  id: number;
  operation: string;
  key: string;
  value: unknown;
}

interface IncrementalSnapshot {
  // Keys and values that changed since the previous checkpoint
  diff: Map<string, unknown | null>; // null = deleted
  walPosition: number;
}

class IncrementalCheckpointStore {
  private state: Map<string, unknown> = new Map();
  private wal: LogEntry[] = [];
  private nextId = 1;
  private dirtyKeys: Set<string> = new Set();
  private baseSnapshot: Map<string, unknown> = new Map(); // initial full snapshot
  private incrementals: IncrementalSnapshot[] = [];
  private hasBase = false;

  apply(operation: string, key: string, value: unknown): void {
    // TODO: log, apply, and track dirty key
    const entry: LogEntry = { id: this.nextId++, operation, key, value };
    this.wal.push(entry);
    this.executeOp(entry);
    this.dirtyKeys.add(key);
  }

  get(key: string): unknown {
    return this.state.get(key);
  }

  /**
   * Take an incremental checkpoint.
   * First call: full snapshot (base).
   * Subsequent calls: only dirty keys since last checkpoint.
   */
  takeCheckpoint(): { type: 'full' | 'incremental'; keyCount: number } {
    // TODO: implement
    if (!this.hasBase) {
      // First checkpoint: full snapshot
      this.baseSnapshot = new Map(this.state);
      this.hasBase = true;
      this.dirtyKeys.clear();
      this.incrementals = [];
      // Record WAL position for the base
      this.incrementals.push({
        diff: new Map(), // empty diff, base has everything
        walPosition: this.wal.length,
      });
      return { type: 'full', keyCount: this.baseSnapshot.size };
    }

    // Incremental: only save dirty keys
    const diff = new Map<string, unknown | null>();
    for (const key of this.dirtyKeys) {
      if (this.state.has(key)) {
        diff.set(key, this.state.get(key)!);
      } else {
        diff.set(key, null); // deleted
      }
    }
    this.incrementals.push({
      diff,
      walPosition: this.wal.length,
    });
    const keyCount = this.dirtyKeys.size;
    this.dirtyKeys.clear();
    return { type: 'incremental', keyCount };
  }

  simulateCrash(): void {
    this.state = new Map();
    this.dirtyKeys.clear();
  }

  /**
   * Recover: load base snapshot, apply all incremental diffs,
   * then replay WAL entries after the last checkpoint.
   */
  recover(): { replayed: number; fromCheckpoint: boolean } {
    // TODO: implement
    if (!this.hasBase) {
      // No checkpoint: replay entire WAL
      this.state = new Map();
      for (const entry of this.wal) {
        this.executeOp(entry);
      }
      return { replayed: this.wal.length, fromCheckpoint: false };
    }

    // Load base snapshot
    this.state = new Map(this.baseSnapshot);

    // Apply incremental diffs in order
    for (const inc of this.incrementals) {
      for (const [key, value] of inc.diff) {
        if (value === null) {
          this.state.delete(key);
        } else {
          this.state.set(key, value);
        }
      }
    }

    // Replay WAL after last checkpoint
    const lastWalPos = this.incrementals[this.incrementals.length - 1]!.walPosition;
    let replayed = 0;
    for (let i = lastWalPos; i < this.wal.length; i++) {
      this.executeOp(this.wal[i]!);
      replayed++;
    }

    return { replayed, fromCheckpoint: true };
  }

  private executeOp(entry: LogEntry): void {
    if (entry.operation === 'SET') {
      this.state.set(entry.key, entry.value);
    } else if (entry.operation === 'DELETE') {
      this.state.delete(entry.key);
    }
  }

  get walLength(): number { return this.wal.length; }
  get stateSize(): number { return this.state.size; }
  get dirtyCount(): number { return this.dirtyKeys.size; }
  get checkpointCount(): number { return this.hasBase ? this.incrementals.length : 0; }
}

// ─── Tests (do not modify below this line) ───────────────────────

describe('Checkpointing - Intermediate: Incremental Checkpoint', () => {
  it('should take a full checkpoint on first call', () => {
    const store = new IncrementalCheckpointStore();
    store.apply('SET', 'a', 1);
    store.apply('SET', 'b', 2);

    const result = store.takeCheckpoint();
    expect(result.type).toBe('full');
    expect(result.keyCount).toBe(2);
  });

  it('should take incremental checkpoint with only dirty keys', () => {
    const store = new IncrementalCheckpointStore();
    store.apply('SET', 'a', 1);
    store.apply('SET', 'b', 2);
    store.apply('SET', 'c', 3);
    store.takeCheckpoint(); // full: 3 keys

    store.apply('SET', 'a', 10); // modify only 'a'

    const result = store.takeCheckpoint();
    expect(result.type).toBe('incremental');
    expect(result.keyCount).toBe(1); // only 'a' was dirty
  });

  it('should recover from base + incremental checkpoints', () => {
    const store = new IncrementalCheckpointStore();
    store.apply('SET', 'x', 1);
    store.apply('SET', 'y', 2);
    store.takeCheckpoint(); // full

    store.apply('SET', 'x', 10); // update x
    store.takeCheckpoint(); // incremental: x=10

    store.apply('SET', 'z', 3); // after last checkpoint

    store.simulateCrash();
    const result = store.recover();

    expect(result.fromCheckpoint).toBe(true);
    expect(result.replayed).toBe(1); // only z
    expect(store.get('x')).toBe(10); // from incremental
    expect(store.get('y')).toBe(2);  // from base
    expect(store.get('z')).toBe(3);  // from WAL replay
  });

  it('should handle deletes in incremental checkpoint', () => {
    const store = new IncrementalCheckpointStore();
    store.apply('SET', 'a', 1);
    store.apply('SET', 'b', 2);
    store.takeCheckpoint(); // full

    store.apply('DELETE', 'a', null);
    store.takeCheckpoint(); // incremental: a=deleted

    store.simulateCrash();
    store.recover();

    expect(store.get('a')).toBeUndefined();
    expect(store.get('b')).toBe(2);
  });

  it('should recover entire WAL when no checkpoint exists', () => {
    const store = new IncrementalCheckpointStore();
    store.apply('SET', 'a', 1);
    store.apply('SET', 'b', 2);

    store.simulateCrash();
    const result = store.recover();

    expect(result.fromCheckpoint).toBe(false);
    expect(result.replayed).toBe(2);
    expect(store.get('a')).toBe(1);
  });

  it('should handle multiple incremental checkpoints', () => {
    const store = new IncrementalCheckpointStore();
    store.apply('SET', 'a', 1);
    store.takeCheckpoint(); // full

    store.apply('SET', 'b', 2);
    store.takeCheckpoint(); // incremental 1

    store.apply('SET', 'c', 3);
    store.takeCheckpoint(); // incremental 2

    store.apply('SET', 'd', 4);

    store.simulateCrash();
    const result = store.recover();

    expect(result.replayed).toBe(1); // only 'd'
    expect(store.get('a')).toBe(1);
    expect(store.get('b')).toBe(2);
    expect(store.get('c')).toBe(3);
    expect(store.get('d')).toBe(4);
  });

  it('should track dirty keys correctly across operations', () => {
    const store = new IncrementalCheckpointStore();
    store.apply('SET', 'a', 1);
    store.apply('SET', 'b', 2);
    store.takeCheckpoint();

    expect(store.dirtyCount).toBe(0); // cleared after checkpoint

    store.apply('SET', 'a', 10);
    store.apply('SET', 'c', 3);
    expect(store.dirtyCount).toBe(2);

    store.takeCheckpoint();
    expect(store.dirtyCount).toBe(0);
  });

  it('should recover nothing when last checkpoint is at WAL end', () => {
    const store = new IncrementalCheckpointStore();
    store.apply('SET', 'x', 1);
    store.takeCheckpoint();

    store.simulateCrash();
    const result = store.recover();

    expect(result.replayed).toBe(0);
    expect(store.get('x')).toBe(1);
  });
});
