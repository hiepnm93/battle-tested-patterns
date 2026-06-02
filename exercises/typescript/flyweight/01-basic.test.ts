import { describe, it, expect } from 'vitest';

/**
 * Flyweight / Interning - Basic: String interner.
 *
 * TODO: Implement an Interner that returns the same object
 * reference for equal keys, avoiding duplicate allocations.
 */

class Interner<T> {
  private pool = new Map<string, T>();

  /** Return cached instance or create and cache a new one */
  intern(key: string, create: () => T): T {
    if (this.pool.has(key)) return this.pool.get(key)!; // TODO: implement
    const value = create();
    this.pool.set(key, value);
    return value;
  }

  has(key: string): boolean {
    return this.pool.has(key); // TODO: implement
  }

  get size(): number {
    return this.pool.size; // TODO: implement
  }
}

// ─── Tests (do not modify below this line) ───────────────────────

describe('Flyweight - Basic: String Interner', () => {
  it('should return same reference for same key', () => {
    const interner = new Interner<{ name: string }>();
    const a = interner.intern('alice', () => ({ name: 'alice' }));
    const b = interner.intern('alice', () => ({ name: 'alice-duplicate' }));
    expect(a).toBe(b); // same reference
    expect(a.name).toBe('alice'); // factory not called second time
  });

  it('should return different objects for different keys', () => {
    const interner = new Interner<number>();
    const a = interner.intern('x', () => 1);
    const b = interner.intern('y', () => 2);
    expect(a).not.toBe(b);
    expect(a).toBe(1);
    expect(b).toBe(2);
  });

  it('should track pool size', () => {
    const interner = new Interner<string>();
    expect(interner.size).toBe(0);
    interner.intern('a', () => 'A');
    interner.intern('b', () => 'B');
    interner.intern('a', () => 'A2'); // duplicate, not added
    expect(interner.size).toBe(2);
  });

  it('should report whether key exists', () => {
    const interner = new Interner<number>();
    expect(interner.has('x')).toBe(false);
    interner.intern('x', () => 42);
    expect(interner.has('x')).toBe(true);
  });

  it('should save memory by reusing instances', () => {
    const interner = new Interner<string>();
    let created = 0;
    const factory = () => { created++; return 'shared'; };

    interner.intern('key', factory);
    interner.intern('key', factory);
    interner.intern('key', factory);

    expect(created).toBe(1); // factory called only once
  });
});
