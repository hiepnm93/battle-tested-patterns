import { describe, it, expect } from 'vitest';

/**
 * Merge Iterator - Basic: Merge K sorted arrays into one sorted array.
 *
 * TODO: Implement mergeKSorted using a min-heap to efficiently
 * merge K pre-sorted arrays into a single sorted output.
 */

class MinHeap<T> {
  private data: T[] = [];
  constructor(private compare: (a: T, b: T) => number) {}

  push(val: T): void {
    // TODO: implement
    this.data.push(val);
    this.bubbleUp(this.data.length - 1);
  }

  pop(): T | undefined {
    // TODO: implement
    if (this.data.length === 0) return undefined;
    const top = this.data[0]!;
    const last = this.data.pop()!;
    if (this.data.length > 0) {
      this.data[0] = last;
      this.sinkDown(0);
    }
    return top;
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

function mergeKSorted(streams: number[][]): number[] {
  // TODO: use MinHeap to merge K sorted arrays
  const heap = new MinHeap<{ val: number; stream: number; index: number }>(
    (a, b) => a.val - b.val,
  );

  for (let s = 0; s < streams.length; s++) {
    if (streams[s]!.length > 0) {
      heap.push({ val: streams[s]![0]!, stream: s, index: 0 });
    }
  }

  const result: number[] = [];
  while (heap.size > 0) {
    const { val, stream, index } = heap.pop()!;
    result.push(val);
    const nextIndex = index + 1;
    if (nextIndex < streams[stream]!.length) {
      heap.push({ val: streams[stream]![nextIndex]!, stream, index: nextIndex });
    }
  }
  return result;
}

// ─── Tests (do not modify below this line) ───────────────────────

describe('Merge Iterator - Basic', () => {
  it('should merge two sorted arrays', () => {
    const result = mergeKSorted([[1, 3, 5], [2, 4, 6]]);
    expect(result).toEqual([1, 2, 3, 4, 5, 6]);
  });

  it('should merge three sorted arrays', () => {
    const result = mergeKSorted([[1, 5, 9], [2, 6, 7], [3, 4, 8]]);
    expect(result).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9]);
  });

  it('should handle empty arrays', () => {
    const result = mergeKSorted([[], [1, 2], [], [3]]);
    expect(result).toEqual([1, 2, 3]);
  });

  it('should handle all empty arrays', () => {
    const result = mergeKSorted([[], [], []]);
    expect(result).toEqual([]);
  });

  it('should handle single array', () => {
    const result = mergeKSorted([[1, 2, 3]]);
    expect(result).toEqual([1, 2, 3]);
  });

  it('should handle arrays of different lengths', () => {
    const result = mergeKSorted([[1], [2, 3, 4, 5], [6, 7]]);
    expect(result).toEqual([1, 2, 3, 4, 5, 6, 7]);
  });

  it('should handle duplicate values across streams', () => {
    const result = mergeKSorted([[1, 3, 5], [1, 3, 5], [2, 4, 6]]);
    expect(result).toEqual([1, 1, 2, 3, 3, 4, 5, 5, 6]);
  });

  it('should handle negative numbers', () => {
    const result = mergeKSorted([[-5, -1, 3], [-3, 0, 2]]);
    expect(result).toEqual([-5, -3, -1, 0, 2, 3]);
  });
});
