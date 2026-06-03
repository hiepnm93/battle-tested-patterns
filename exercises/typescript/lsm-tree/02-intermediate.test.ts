import { describe, it, expect } from 'vitest';

/**
 * LSM Tree - Intermediate: Multi-level compaction with size-triggered merge.
 *
 * TODO: Implement an LSM tree where:
 * - When the number of sorted runs exceeds maxRuns, compact all runs
 *   into a single merged run
 * - Compaction removes tombstones and deduplicates by keeping newest entry
 * - After compaction, runCount should be 0 or 1
 *
 * Real-world use: LevelDB/RocksDB compaction -- background merge of
 * SSTable files to bound read amplification and reclaim disk space.
 */

interface KVEntry {
  key: string;
  value: string | null;
  seq: number;
}

class Memtable {
  private entries: Map<string, KVEntry> = new Map();
  private _size = 0;

  put(key: string, value: string, seq: number): void {
    this.entries.set(key, { key, value, seq });
    this._size++;
  }

  delete(key: string, seq: number): void {
    this.entries.set(key, { key, value: null, seq });
    this._size++;
  }

  get(key: string): KVEntry | undefined {
    return this.entries.get(key);
  }

  get size(): number { return this._size; }

  flush(): KVEntry[] {
    const sorted = [...this.entries.values()].sort((a, b) => a.key.localeCompare(b.key));
    this.entries.clear();
    this._size = 0;
    return sorted;
  }
}

type SortedRun = KVEntry[];

class LSMTreeWithCompaction {
  private memtable = new Memtable();
  private runs: SortedRun[] = [];
  private seq = 0;
  private readonly flushThreshold: number;
  private readonly maxRuns: number;

  constructor(flushThreshold = 3, maxRuns = 3) {
    this.flushThreshold = flushThreshold;
    this.maxRuns = maxRuns;
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
    // TODO: implement
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
    if (this.runs.length > this.maxRuns) {
      this.compact();
    }
  }

  private compact(): void {
    // TODO: merge all runs, keep newest entry per key, remove tombstones
    const merged = new Map<string, KVEntry>();
    for (let i = this.runs.length - 1; i >= 0; i--) {
      for (const entry of this.runs[i]!) {
        merged.set(entry.key, entry);
      }
    }
    const compacted = [...merged.values()]
      .filter((e) => e.value !== null)
      .sort((a, b) => a.key.localeCompare(b.key));
    this.runs = compacted.length > 0 ? [compacted] : [];
  }

  get runCount(): number { return this.runs.length; }
}

// ─── Tests (do not modify below this line) ───────────────────────

describe('LSM Tree - Intermediate: Compaction', () => {
  it('should trigger compaction when runs exceed maxRuns', () => {
    const lsm = new LSMTreeWithCompaction(2, 2); // flush every 2, compact at 3 runs

    lsm.put('a', '1');
    lsm.put('b', '2'); // flush → run 1
    expect(lsm.runCount).toBe(1);

    lsm.put('c', '3');
    lsm.put('d', '4'); // flush → run 2
    expect(lsm.runCount).toBe(2);

    lsm.put('e', '5');
    lsm.put('f', '6'); // flush → run 3 → triggers compaction → run 1
    expect(lsm.runCount).toBe(1);
  });

  it('should preserve all values after compaction', () => {
    const lsm = new LSMTreeWithCompaction(2, 2);

    lsm.put('a', '1');
    lsm.put('b', '2'); // flush
    lsm.put('c', '3');
    lsm.put('d', '4'); // flush
    lsm.put('e', '5');
    lsm.put('f', '6'); // flush → compact

    expect(lsm.get('a')).toBe('1');
    expect(lsm.get('b')).toBe('2');
    expect(lsm.get('c')).toBe('3');
    expect(lsm.get('d')).toBe('4');
    expect(lsm.get('e')).toBe('5');
    expect(lsm.get('f')).toBe('6');
  });

  it('should keep newest value during compaction (dedup)', () => {
    const lsm = new LSMTreeWithCompaction(2, 2);

    lsm.put('a', 'v1');
    lsm.put('b', 'v1'); // flush
    lsm.put('a', 'v2');
    lsm.put('c', 'v1'); // flush: a has newer value
    lsm.put('a', 'v3');
    lsm.put('d', 'v1'); // flush → compact

    expect(lsm.get('a')).toBe('v3'); // newest wins
  });

  it('should remove tombstones during compaction', () => {
    const lsm = new LSMTreeWithCompaction(2, 2);

    lsm.put('a', '1');
    lsm.put('b', '2'); // flush
    lsm.delete('a');
    lsm.put('c', '3'); // flush: tombstone for 'a'
    lsm.put('d', '4');
    lsm.put('e', '5'); // flush → compact (tombstone removed)

    expect(lsm.get('a')).toBeUndefined();
    expect(lsm.get('b')).toBe('2');
  });

  it('should handle put-delete-put cycle across compactions', () => {
    const lsm = new LSMTreeWithCompaction(2, 2);

    lsm.put('x', 'first');
    lsm.put('y', '1'); // flush
    lsm.delete('x');
    lsm.put('z', '1'); // flush
    lsm.put('x', 'second');
    lsm.put('w', '1'); // flush → compact

    expect(lsm.get('x')).toBe('second');
  });

  it('should handle all keys deleted', () => {
    const lsm = new LSMTreeWithCompaction(2, 2);

    lsm.put('a', '1');
    lsm.put('b', '2'); // flush
    lsm.delete('a');
    lsm.delete('b'); // flush
    lsm.put('_pad1', 'x');
    lsm.put('_pad2', 'y'); // flush → compact

    expect(lsm.get('a')).toBeUndefined();
    expect(lsm.get('b')).toBeUndefined();
    // Compaction removed tombstones, only _pad entries remain
    expect(lsm.get('_pad1')).toBe('x');
  });

  it('should continue working normally after compaction', () => {
    const lsm = new LSMTreeWithCompaction(2, 2);

    // First compaction cycle
    lsm.put('a', '1');
    lsm.put('b', '2');
    lsm.put('c', '3');
    lsm.put('d', '4');
    lsm.put('e', '5');
    lsm.put('f', '6'); // compact

    // New writes after compaction
    lsm.put('g', '7');
    expect(lsm.get('g')).toBe('7');
    expect(lsm.get('a')).toBe('1');
  });
});
