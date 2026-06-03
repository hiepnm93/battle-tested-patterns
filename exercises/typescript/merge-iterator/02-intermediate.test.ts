import { describe, it, expect } from 'vitest';

/**
 * Merge Iterator - Intermediate: Merge with deduplication (latest-wins by key).
 *
 * TODO: Implement mergeWithDedup that merges K sorted streams of key-value
 * entries. When duplicate keys appear, keep only the entry from the
 * highest-numbered stream (latest wins). Streams are sorted by key.
 *
 * Real-world use: LSM-tree compaction (LevelDB, RocksDB) where newer
 * levels shadow older values for the same key.
 */

interface KVEntry {
  key: string;
  value: string;
}

class MinHeap<T> {
  private data: T[] = [];
  constructor(private compare: (a: T, b: T) => number) {}

  push(val: T): void {
    this.data.push(val);
    this.bubbleUp(this.data.length - 1);
  }

  pop(): T | undefined {
    if (this.data.length === 0) return undefined;
    const top = this.data[0]!;
    const last = this.data.pop()!;
    if (this.data.length > 0) {
      this.data[0] = last;
      this.sinkDown(0);
    }
    return top;
  }

  peek(): T | undefined {
    return this.data[0];
  }

  get size(): number {
    return this.data.length;
  }

  private bubbleUp(i: number): void {
    while (i > 0) {
      const parent = (i - 1) >> 1;
      if (this.compare(this.data[i]!, this.data[parent]!) >= 0) break;
      [this.data[i], this.data[parent]] = [this.data[parent]!, this.data[i]!];
      i = parent;
    }
  }

  private sinkDown(i: number): void {
    const n = this.data.length;
    while (true) {
      let smallest = i;
      const left = 2 * i + 1;
      const right = 2 * i + 2;
      if (left < n && this.compare(this.data[left]!, this.data[smallest]!) < 0) smallest = left;
      if (right < n && this.compare(this.data[right]!, this.data[smallest]!) < 0) smallest = right;
      if (smallest === i) break;
      [this.data[i], this.data[smallest]] = [this.data[smallest]!, this.data[i]!];
      i = smallest;
    }
  }
}

interface HeapEntry {
  key: string;
  value: string;
  stream: number; // higher stream number = newer data
  index: number;
}

function mergeWithDedup(streams: KVEntry[][]): KVEntry[] {
  // TODO: merge K sorted streams, dedup by key (highest stream number wins)
  const heap = new MinHeap<HeapEntry>((a, b) => {
    const keyCompare = a.key.localeCompare(b.key);
    if (keyCompare !== 0) return keyCompare;
    // For same key, higher stream number should come first (win)
    return b.stream - a.stream;
  });

  for (let s = 0; s < streams.length; s++) {
    if (streams[s]!.length > 0) {
      const entry = streams[s]![0]!;
      heap.push({ key: entry.key, value: entry.value, stream: s, index: 0 });
    }
  }

  const result: KVEntry[] = [];
  while (heap.size > 0) {
    const winner = heap.pop()!;

    // Skip all other entries with the same key (they are older)
    while (heap.size > 0 && heap.peek()!.key === winner.key) {
      const dup = heap.pop()!;
      const nextIdx = dup.index + 1;
      if (nextIdx < streams[dup.stream]!.length) {
        const next = streams[dup.stream]![nextIdx]!;
        heap.push({ key: next.key, value: next.value, stream: dup.stream, index: nextIdx });
      }
    }

    result.push({ key: winner.key, value: winner.value });

    // Advance the winning stream
    const nextIdx = winner.index + 1;
    if (nextIdx < streams[winner.stream]!.length) {
      const next = streams[winner.stream]![nextIdx]!;
      heap.push({ key: next.key, value: next.value, stream: winner.stream, index: nextIdx });
    }
  }

  return result;
}

// ─── Tests (do not modify below this line) ───────────────────────

describe('Merge Iterator - Intermediate: Deduplication', () => {
  it('should merge without duplicates when keys are unique', () => {
    const result = mergeWithDedup([
      [{ key: 'a', value: '1' }, { key: 'c', value: '3' }],
      [{ key: 'b', value: '2' }, { key: 'd', value: '4' }],
    ]);
    expect(result).toEqual([
      { key: 'a', value: '1' },
      { key: 'b', value: '2' },
      { key: 'c', value: '3' },
      { key: 'd', value: '4' },
    ]);
  });

  it('should keep latest value for duplicate keys (higher stream wins)', () => {
    const result = mergeWithDedup([
      [{ key: 'x', value: 'old' }],     // stream 0 (oldest)
      [{ key: 'x', value: 'new' }],     // stream 1 (newest)
    ]);
    expect(result).toEqual([{ key: 'x', value: 'new' }]);
  });

  it('should handle duplicates across three streams', () => {
    const result = mergeWithDedup([
      [{ key: 'a', value: 'v0' }, { key: 'b', value: 'v0' }], // stream 0
      [{ key: 'a', value: 'v1' }],                              // stream 1
      [{ key: 'b', value: 'v2' }, { key: 'c', value: 'v2' }], // stream 2
    ]);
    expect(result).toEqual([
      { key: 'a', value: 'v1' },  // stream 1 wins for 'a'
      { key: 'b', value: 'v2' },  // stream 2 wins for 'b'
      { key: 'c', value: 'v2' },
    ]);
  });

  it('should handle all streams having the same key', () => {
    const result = mergeWithDedup([
      [{ key: 'k', value: 'a' }],
      [{ key: 'k', value: 'b' }],
      [{ key: 'k', value: 'c' }],
    ]);
    // Stream 2 (highest) wins
    expect(result).toEqual([{ key: 'k', value: 'c' }]);
  });

  it('should handle empty streams', () => {
    const result = mergeWithDedup([
      [],
      [{ key: 'a', value: '1' }],
      [],
    ]);
    expect(result).toEqual([{ key: 'a', value: '1' }]);
  });

  it('should handle mixed unique and duplicate keys', () => {
    const result = mergeWithDedup([
      [{ key: 'a', value: 'old-a' }, { key: 'c', value: 'only-c' }],
      [{ key: 'a', value: 'new-a' }, { key: 'b', value: 'only-b' }],
    ]);
    expect(result).toEqual([
      { key: 'a', value: 'new-a' },
      { key: 'b', value: 'only-b' },
      { key: 'c', value: 'only-c' },
    ]);
  });

  it('should produce sorted output', () => {
    const result = mergeWithDedup([
      [{ key: 'b', value: '1' }, { key: 'd', value: '2' }],
      [{ key: 'a', value: '3' }, { key: 'c', value: '4' }],
      [{ key: 'b', value: '5' }, { key: 'e', value: '6' }],
    ]);
    const keys = result.map((e) => e.key);
    expect(keys).toEqual([...keys].sort());
  });
});
