import { describe, it, expect } from 'vitest';

/**
 * Double Buffering - Intermediate: React-style fiber alternates.
 *
 * Implement createWorkInProgress that reuses an alternate fiber
 * instead of allocating a new one on every render.
 */

interface Fiber {
  tag: string;
  pendingProps: Record<string, unknown>;
  memoizedState: unknown;
  alternate: Fiber | null;
}

function createFiber(tag: string, props: Record<string, unknown>): Fiber {
  return { tag, pendingProps: props, memoizedState: null, alternate: null };
}

function createWorkInProgress(
  current: Fiber,
  pendingProps: Record<string, unknown>,
): Fiber {
  let wip = current.alternate;

  if (wip === null) {
    wip = createFiber(current.tag, pendingProps);
    wip.memoizedState = current.memoizedState;
    wip.alternate = current;
    current.alternate = wip;
  } else {
    wip.pendingProps = pendingProps;
    wip.memoizedState = current.memoizedState;
  }

  return wip;
}

describe('Double Buffering - Intermediate: Fiber Alternates', () => {
  it('should create alternate on first call', () => {
    const current = createFiber('div', { className: 'old' });
    current.memoizedState = 'state-v1';

    const wip = createWorkInProgress(current, { className: 'new' });

    expect(wip.tag).toBe('div');
    expect(wip.pendingProps).toEqual({ className: 'new' });
    expect(wip.memoizedState).toBe('state-v1');
    expect(wip.alternate).toBe(current);
    expect(current.alternate).toBe(wip);
  });

  it('should reuse alternate on subsequent calls (zero allocation)', () => {
    const current = createFiber('span', { text: 'v1' });
    const wip1 = createWorkInProgress(current, { text: 'v2' });

    // Simulate commit: swap current ↔ wip
    const committed = wip1; // wip becomes new current
    const wip2 = createWorkInProgress(committed, { text: 'v3' });

    // wip2 should be the original current object (reused)
    expect(wip2).toBe(current);
    expect(wip2.pendingProps).toEqual({ text: 'v3' });
  });

  it('should maintain mutual alternate links', () => {
    const a = createFiber('div', {});
    const b = createWorkInProgress(a, { updated: true });

    expect(a.alternate).toBe(b);
    expect(b.alternate).toBe(a);

    // After "commit", create wip from b
    const c = createWorkInProgress(b, { updated: false });

    // c should be a (reused), and links should still be mutual
    expect(c).toBe(a);
    expect(b.alternate).toBe(a);
    expect(a.alternate).toBe(b);
  });

  it('should carry memoizedState from current to wip', () => {
    const current = createFiber('Counter', {});
    current.memoizedState = { count: 42 };

    const wip = createWorkInProgress(current, {});
    expect(wip.memoizedState).toEqual({ count: 42 });
  });

  it('should update props without allocating new fiber', () => {
    const current = createFiber('Button', { label: 'v1' });
    const wip1 = createWorkInProgress(current, { label: 'v2' });
    const wipRef = wip1;

    // Reuse same wip with new props
    const wip2 = createWorkInProgress(current, { label: 'v3' });
    expect(wip2).toBe(wipRef); // same object
    expect(wip2.pendingProps).toEqual({ label: 'v3' });
  });
});
