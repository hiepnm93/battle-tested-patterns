import { describe, it, expect } from 'vitest';

/**
 * MVCC - Basic: Implement multi-version concurrency control.
 *
 * TODO: Implement an MVCCStore where each write creates a new version.
 * Reads at a specific timestamp see the latest version <= that timestamp.
 */

interface Version<T> {
  timestamp: number;
  value: T;
  deleted: boolean;
}

class MVCCStore<T> {
  private store = new Map<string, Version<T>[]>();

  put(key: string, value: T, timestamp: number): void {
    // TODO: implement
    if (!this.store.has(key)) this.store.set(key, []);
    this.store.get(key)!.push({ timestamp, value, deleted: false });
  }

  get(key: string, timestamp: number): T | undefined {
    // TODO: implement
    const versions = this.store.get(key);
    if (!versions) return undefined;
    let result: Version<T> | undefined;
    for (const v of versions) {
      if (v.timestamp <= timestamp && (!result || v.timestamp > result.timestamp)) {
        result = v;
      }
    }
    if (!result || result.deleted) return undefined;
    return result.value;
  }

  delete(key: string, timestamp: number): void {
    // TODO: implement
    if (!this.store.has(key)) this.store.set(key, []);
    this.store.get(key)!.push({ timestamp, value: undefined as T, deleted: true });
  }
}

// ─── Tests (do not modify below this line) ───────────────────────

describe('MVCC - Basic', () => {
  it('should read the latest version at a timestamp', () => {
    const store = new MVCCStore<number>();
    store.put('x', 1, 100);
    store.put('x', 2, 200);
    store.put('x', 3, 300);

    expect(store.get('x', 150)).toBe(1);
    expect(store.get('x', 250)).toBe(2);
    expect(store.get('x', 350)).toBe(3);
  });

  it('should return undefined before first write', () => {
    const store = new MVCCStore<string>();
    store.put('k', 'v', 100);
    expect(store.get('k', 50)).toBeUndefined();
  });

  it('should handle deletes as tombstones', () => {
    const store = new MVCCStore<string>();
    store.put('k', 'alive', 100);
    store.delete('k', 200);

    expect(store.get('k', 150)).toBe('alive');
    expect(store.get('k', 250)).toBeUndefined();
  });

  it('should support multiple keys independently', () => {
    const store = new MVCCStore<number>();
    store.put('a', 1, 100);
    store.put('b', 2, 100);

    expect(store.get('a', 100)).toBe(1);
    expect(store.get('b', 100)).toBe(2);
    expect(store.get('c', 100)).toBeUndefined();
  });

  it('should return exact timestamp match', () => {
    const store = new MVCCStore<string>();
    store.put('k', 'v1', 100);
    expect(store.get('k', 100)).toBe('v1');
  });
});
