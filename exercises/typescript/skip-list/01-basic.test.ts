import { describe, it, expect } from 'vitest';

/**
 * Skip List - Basic: Implement a probabilistic sorted data structure.
 *
 * TODO: Implement a SkipList with insert(), search(), and delete().
 * A skip list uses multiple layers of linked lists with random promotion
 * to achieve O(log n) average search/insert/delete.
 */

class SkipNode {
  forward: (SkipNode | null)[];
  constructor(
    public key: number,
    public value: string,
    level: number,
  ) {
    this.forward = new Array(level + 1).fill(null);
  }
}

class SkipList {
  private maxLevel = 16;
  private level = 0;
  private header: SkipNode;
  private p = 0.5;

  constructor() {
    // TODO: implement
    this.header = new SkipNode(-Infinity, '', this.maxLevel);
  }

  private randomLevel(): number {
    let lvl = 0;
    while (lvl < this.maxLevel && Math.random() < this.p) lvl++;
    return lvl;
  }

  insert(key: number, value: string): void {
    // TODO: implement
    const update: (SkipNode | null)[] = new Array(this.maxLevel + 1).fill(null);
    let current = this.header;

    for (let i = this.level; i >= 0; i--) {
      while (current.forward[i] && current.forward[i]!.key < key) {
        current = current.forward[i]!;
      }
      update[i] = current;
    }

    const next = current.forward[0];
    if (next && next.key === key) {
      next.value = value;
      return;
    }

    const newLevel = this.randomLevel();
    if (newLevel > this.level) {
      for (let i = this.level + 1; i <= newLevel; i++) update[i] = this.header;
      this.level = newLevel;
    }

    const node = new SkipNode(key, value, newLevel);
    for (let i = 0; i <= newLevel; i++) {
      node.forward[i] = update[i]!.forward[i] ?? null;
      update[i]!.forward[i] = node;
    }
  }

  search(key: number): string | undefined {
    // TODO: implement
    let current = this.header;
    for (let i = this.level; i >= 0; i--) {
      while (current.forward[i] && current.forward[i]!.key < key) {
        current = current.forward[i]!;
      }
    }
    const next = current.forward[0];
    return next && next.key === key ? next.value : undefined;
  }

  delete(key: number): boolean {
    // TODO: implement
    const update: (SkipNode | null)[] = new Array(this.maxLevel + 1).fill(null);
    let current = this.header;

    for (let i = this.level; i >= 0; i--) {
      while (current.forward[i] && current.forward[i]!.key < key) {
        current = current.forward[i]!;
      }
      update[i] = current;
    }

    const target = current.forward[0];
    if (!target || target.key !== key) return false;

    for (let i = 0; i <= this.level; i++) {
      if (update[i]!.forward[i] !== target) break;
      update[i]!.forward[i] = target.forward[i] ?? null;
    }
    while (this.level > 0 && !this.header.forward[this.level]) this.level--;
    return true;
  }
}

// ─── Tests (do not modify below this line) ───────────────────────

describe('Skip List - Basic', () => {
  it('should insert and search elements', () => {
    const sl = new SkipList();
    sl.insert(3, 'three');
    sl.insert(1, 'one');
    sl.insert(2, 'two');

    expect(sl.search(1)).toBe('one');
    expect(sl.search(2)).toBe('two');
    expect(sl.search(3)).toBe('three');
  });

  it('should return undefined for missing keys', () => {
    const sl = new SkipList();
    sl.insert(1, 'one');
    expect(sl.search(99)).toBeUndefined();
  });

  it('should update value on duplicate insert', () => {
    const sl = new SkipList();
    sl.insert(1, 'old');
    sl.insert(1, 'new');
    expect(sl.search(1)).toBe('new');
  });

  it('should delete elements', () => {
    const sl = new SkipList();
    sl.insert(1, 'one');
    sl.insert(2, 'two');
    sl.insert(3, 'three');

    expect(sl.delete(2)).toBe(true);
    expect(sl.search(2)).toBeUndefined();
    expect(sl.search(1)).toBe('one');
    expect(sl.search(3)).toBe('three');
  });

  it('should return false when deleting non-existent key', () => {
    const sl = new SkipList();
    expect(sl.delete(42)).toBe(false);
  });
});
