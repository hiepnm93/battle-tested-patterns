import { describe, it, expect } from 'vitest';

/**
 * Consistent Hashing - Basic: Implement a hash ring.
 *
 * TODO: Implement a HashRing that distributes keys across nodes.
 * Adding/removing a node should only remap ~1/n of the keys.
 */

class HashRing {
  private ring = new Map<number, string>();
  private sortedKeys: number[] = [];

  constructor(private replicas = 100) {} // TODO: implement

  private hash(key: string): number {
    let h = 2166136261;
    for (let i = 0; i < key.length; i++) {
      h ^= key.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  }

  addNode(node: string): void {
    // TODO: implement
    for (let i = 0; i < this.replicas; i++) {
      const h = this.hash(`${node}:${i}`);
      this.ring.set(h, node);
      this.sortedKeys.push(h);
    }
    this.sortedKeys.sort((a, b) => a - b);
  }

  removeNode(node: string): void {
    // TODO: implement
    for (let i = 0; i < this.replicas; i++) {
      const h = this.hash(`${node}:${i}`);
      this.ring.delete(h);
    }
    this.sortedKeys = this.sortedKeys.filter((k) => this.ring.has(k));
  }

  getNode(key: string): string | undefined {
    // TODO: implement
    if (this.sortedKeys.length === 0) return undefined;
    const h = this.hash(key);
    for (const k of this.sortedKeys) {
      if (k >= h) return this.ring.get(k);
    }
    return this.ring.get(this.sortedKeys[0]!);
  }
}

// ─── Tests (do not modify below this line) ───────────────────────

describe('Consistent Hashing - Basic', () => {
  it('should assign keys to nodes', () => {
    const ring = new HashRing(50);
    ring.addNode('server-1');
    ring.addNode('server-2');

    const node = ring.getNode('my-key');
    expect(node).toBeDefined();
    expect(['server-1', 'server-2']).toContain(node);
  });

  it('should return undefined for empty ring', () => {
    const ring = new HashRing();
    expect(ring.getNode('key')).toBeUndefined();
  });

  it('should distribute keys across nodes', () => {
    const ring = new HashRing(100);
    ring.addNode('A');
    ring.addNode('B');
    ring.addNode('C');

    const counts: Record<string, number> = { A: 0, B: 0, C: 0 };
    for (let i = 0; i < 300; i++) {
      const node = ring.getNode(`key-${i}`)!;
      counts[node] = (counts[node] ?? 0) + 1;
    }
    expect(counts['A']).toBeGreaterThan(0);
    expect(counts['B']).toBeGreaterThan(0);
    expect(counts['C']).toBeGreaterThan(0);
  });

  it('should minimize remapping when a node is removed', () => {
    const ring = new HashRing(100);
    ring.addNode('A');
    ring.addNode('B');
    ring.addNode('C');

    const before = Array.from({ length: 100 }, (_, i) => ring.getNode(`k${i}`));
    ring.removeNode('C');
    const after = Array.from({ length: 100 }, (_, i) => ring.getNode(`k${i}`));

    let changed = 0;
    for (let i = 0; i < 100; i++) {
      if (before[i] !== after[i]) changed++;
    }
    expect(changed).toBeLessThan(60);
  });

  it('should be consistent for same key', () => {
    const ring = new HashRing(50);
    ring.addNode('X');
    ring.addNode('Y');

    const node1 = ring.getNode('stable-key');
    const node2 = ring.getNode('stable-key');
    expect(node1).toBe(node2);
  });
});
