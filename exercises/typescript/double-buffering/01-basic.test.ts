import { describe, it, expect } from 'vitest';

/**
 * Double Buffering - Basic: Generic double buffer with swap.
 *
 * Implement a DoubleBuffer that maintains two copies of state,
 * allowing writes to the "next" buffer while "current" stays stable.
 */

class DoubleBuffer<T> {
  private buffers: [T, T];
  private currentIndex: 0 | 1 = 0;

  constructor(a: T, b: T) {
    this.buffers = [a, b];
  }

  current(): T {
    return this.buffers[this.currentIndex];
  }

  next(): T {
    return this.buffers[this.currentIndex === 0 ? 1 : 0];
  }

  swap(): void {
    this.currentIndex = this.currentIndex === 0 ? 1 : 0;
  }
}

describe('Double Buffering - Basic: Swap Mechanics', () => {
  it('should return initial current value', () => {
    const buf = new DoubleBuffer('frame-A', 'frame-B');
    expect(buf.current()).toBe('frame-A');
  });

  it('should return next (back) buffer', () => {
    const buf = new DoubleBuffer('frame-A', 'frame-B');
    expect(buf.next()).toBe('frame-B');
  });

  it('should swap current and next', () => {
    const buf = new DoubleBuffer('frame-A', 'frame-B');
    buf.swap();
    expect(buf.current()).toBe('frame-B');
    expect(buf.next()).toBe('frame-A');
  });

  it('should return to original after double swap', () => {
    const buf = new DoubleBuffer(1, 2);
    buf.swap();
    buf.swap();
    expect(buf.current()).toBe(1);
    expect(buf.next()).toBe(2);
  });

  it('should work with mutable objects', () => {
    const buf = new DoubleBuffer({ pixels: [0, 0] }, { pixels: [0, 0] });

    // Write to back buffer while front is stable
    const backBuffer = buf.next();
    backBuffer.pixels = [255, 128];

    // Front buffer unchanged
    expect(buf.current().pixels).toEqual([0, 0]);

    // Swap — now the written data is visible
    buf.swap();
    expect(buf.current().pixels).toEqual([255, 128]);
  });

  it('should reuse buffers (zero allocation)', () => {
    const objA = { value: 'a' };
    const objB = { value: 'b' };
    const buf = new DoubleBuffer(objA, objB);

    buf.swap();
    expect(buf.current()).toBe(objB); // same reference, not a copy
    expect(buf.next()).toBe(objA);

    buf.swap();
    expect(buf.current()).toBe(objA); // still the same objects
  });
});
