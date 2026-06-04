type CleanupFn<T> = (value: T) => void;

interface RefCountedInner<T> {
  value: T;
  count: number;
  dropped: boolean;
  cleanup: CleanupFn<T>;
}

class RefCounted<T> {
  private inner: RefCountedInner<T>;
  private owned: boolean;

  constructor(value: T, cleanup: CleanupFn<T>) {
    this.inner = { value, count: 1, dropped: false, cleanup };
    this.owned = true;
  }

  /** Create a new owner sharing the same value. */
  clone(): RefCounted<T> {
    if (!this.owned) throw new Error('Cannot clone a dropped reference');
    this.inner.count++;
    const cloned = Object.create(RefCounted.prototype) as RefCounted<T>;
    cloned.inner = this.inner;
    cloned.owned = true;
    return cloned;
  }

  /** Release this owner's reference. Triggers cleanup when count hits 0. */
  drop(): void {
    if (!this.owned) return; // double-drop is a no-op
    this.owned = false;
    this.inner.count--;
    if (this.inner.count === 0 && !this.inner.dropped) {
      this.inner.dropped = true;
      this.inner.cleanup(this.inner.value);
    }
  }

  refCount(): number { return this.inner.count; }

  value(): T {
    if (!this.owned) throw new Error('Reference has been dropped');
    return this.inner.value;
  }
}
