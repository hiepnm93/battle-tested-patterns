import { describe, it, expect } from 'vitest';

/**
 * LSM Tree - Basic: In-memory memtable with flush to sorted runs.
 *
 * TODO: Implement a simple LSM tree with:
 * - put(key, value): write to memtable
 * - get(key): read from memtable first, then sorted runs
 * - delete(key): write a tombstone
 * - Auto-flush memtable to a sorted run when it reaches a size threshold
 */

interface KVEntry {
  key: string;
  value: string | null; // null = tombstone
  seq: number;
}

class Memtable {
  private entries: Map<string, KVEntry> = new Map();
  private _size = 0;

  put(key: string, value: string, seq: number): void {
    // TODO: implement
    this.entries.set(key, { key, value, seq });
    this._size++;
  }

  delete(key: string, seq: number): void {
    // TODO: implement
    this.entries.set(key, { key, value: null, seq });
    this._size++;
  }

  get(key: string): KVEntry | undefined {
    // TODO: implement
    return this.entries.get(key);
  }

  get size(): number { return this._size; }

  flush(): KVEntry[] {
    // TODO: return sorted entries and clear memtable
    const sorted = [...this.entries.values()].sort((a, b) => a.key.localeCompare(b.key));
    this.entries.clear();
    this._size = 0;
    return sorted;
  }
}

type SortedRun = KVEntry[];

class LSMTree {
  private memtable = new Memtable();
  private runs: SortedRun[] = [];
  private seq = 0;
  private readonly flushThreshold: number;

  constructor(flushThreshold = 4) {
    this.flushThreshold = flushThreshold;
  }

  put(key: string, value: string): void {
    // TODO: implement
    this.memtable.put(key, value, this.seq++);
    if (this.memtable.size >= this.flushThreshold) {
      this.flushMemtable();
    }
  }

  delete(key: string): void {
    // TODO: implement
    this.memtable.delete(key, this.seq++);
    if (this.memtable.size >= this.flushThreshold) {
      this.flushMemtable();
    }
  }

  get(key: string): string | undefined {
    // TODO: check memtable first, then sorted runs newest-first
    const memEntry = this.memtable.get(key);
    if (memEntry) return memEntry.value ?? undefined;

    for (const run of this.runs) {
      const entry = this.binarySearch(run, key);
      if (entry) return entry.value ?? undefined;
    }
    return undefined;
  }

  private binarySearch(run: SortedRun, key: string): KVEntry | undefined {
    let lo = 0, hi = run.length - 1;
    while (lo <= hi) {
      const mid = (lo + hi) >> 1;
      const cmp = run[mid]!.key.localeCompare(key);
      if (cmp === 0) return run[mid];
      if (cmp < 0) lo = mid + 1;
      else hi = mid - 1;
    }
    return undefined;
  }

  private flushMemtable(): void {
    const run = this.memtable.flush();
    this.runs.unshift(run);
  }

  get runCount(): number { return this.runs.length; }
}

// ─── Tests (do not modify below this line) ───────────────────────

describe('LSM Tree - Basic', () => {
  it('should put and get values from memtable', () => {
    const lsm = new LSMTree(10); // high threshold, no flush
    lsm.put('a', '1');
    lsm.put('b', '2');

    expect(lsm.get('a')).toBe('1');
    expect(lsm.get('b')).toBe('2');
    expect(lsm.get('c')).toBeUndefined();
  });

  it('should overwrite existing keys', () => {
    const lsm = new LSMTree(10);
    lsm.put('a', 'old');
    lsm.put('a', 'new');

    expect(lsm.get('a')).toBe('new');
  });

  it('should handle delete with tombstone', () => {
    const lsm = new LSMTree(10);
    lsm.put('a', '1');
    lsm.delete('a');

    expect(lsm.get('a')).toBeUndefined();
  });

  it('should flush memtable when threshold is reached', () => {
    const lsm = new LSMTree(3); // flush after 3 entries
    expect(lsm.runCount).toBe(0);

    lsm.put('a', '1');
    lsm.put('b', '2');
    lsm.put('c', '3'); // triggers flush

    expect(lsm.runCount).toBe(1);
  });

  it('should read from flushed sorted runs', () => {
    const lsm = new LSMTree(2);
    lsm.put('a', '1');
    lsm.put('b', '2'); // flush

    // Data now in sorted run, memtable is empty
    expect(lsm.get('a')).toBe('1');
    expect(lsm.get('b')).toBe('2');
  });

  it('should prefer memtable over sorted runs for same key', () => {
    const lsm = new LSMTree(2);
    lsm.put('a', 'old');
    lsm.put('x', 'pad'); // flush: a=old, x=pad go to run

    lsm.put('a', 'new'); // now in memtable

    expect(lsm.get('a')).toBe('new');
  });

  it('should handle delete after flush', () => {
    const lsm = new LSMTree(2);
    lsm.put('a', '1');
    lsm.put('b', '2'); // flush

    lsm.delete('a'); // tombstone in memtable

    expect(lsm.get('a')).toBeUndefined();
    expect(lsm.get('b')).toBe('2');
  });

  it('should handle multiple flushes', () => {
    const lsm = new LSMTree(2);
    lsm.put('a', '1');
    lsm.put('b', '2'); // flush 1

    lsm.put('c', '3');
    lsm.put('d', '4'); // flush 2

    expect(lsm.runCount).toBe(2);
    expect(lsm.get('a')).toBe('1');
    expect(lsm.get('d')).toBe('4');
  });
});
