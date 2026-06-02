import { describe, it, expect } from 'vitest';

/**
 * Dependency Graph - Basic: Implement topological sort.
 *
 * TODO: Implement a DependencyGraph with addEdge() and topologicalSort().
 * topologicalSort returns nodes in an order where every node comes after
 * its dependencies. Throws if a cycle is detected.
 */

class DependencyGraph<T> {
  private adjacency = new Map<T, Set<T>>();

  addNode(node: T): void {
    if (!this.adjacency.has(node)) this.adjacency.set(node, new Set());
  }

  addEdge(from: T, to: T): void {
    // TODO: implement — `from` depends on `to` (to must come before from)
    this.addNode(from);
    this.addNode(to);
    this.adjacency.get(from)!.add(to);
  }

  topologicalSort(): T[] {
    // TODO: implement (Kahn's algorithm)
    const inDegree = new Map<T, number>();
    for (const node of this.adjacency.keys()) inDegree.set(node, 0);
    for (const [, deps] of this.adjacency) {
      for (const dep of deps) {
        inDegree.set(dep, (inDegree.get(dep) ?? 0) + 1);
      }
    }

    const queue: T[] = [];
    for (const [node, degree] of inDegree) {
      if (degree === 0) queue.push(node);
    }

    const result: T[] = [];
    while (queue.length > 0) {
      const node = queue.shift()!;
      result.push(node);
      for (const dep of this.adjacency.get(node) ?? []) {
        const newDegree = inDegree.get(dep)! - 1;
        inDegree.set(dep, newDegree);
        if (newDegree === 0) queue.push(dep);
      }
    }

    if (result.length !== this.adjacency.size) {
      throw new Error('Cycle detected');
    }
    return result;
  }
}

// ─── Tests (do not modify below this line) ───────────────────────

describe('Dependency Graph - Basic', () => {
  it('should sort simple dependencies', () => {
    const g = new DependencyGraph<string>();
    g.addEdge('app', 'utils');
    g.addEdge('app', 'config');
    g.addEdge('utils', 'config');

    const order = g.topologicalSort();
    expect(order.indexOf('app')).toBeLessThan(order.indexOf('utils'));
    expect(order.indexOf('app')).toBeLessThan(order.indexOf('config'));
    expect(order.indexOf('utils')).toBeLessThan(order.indexOf('config'));
  });

  it('should handle independent nodes', () => {
    const g = new DependencyGraph<string>();
    g.addNode('a');
    g.addNode('b');
    g.addNode('c');

    const order = g.topologicalSort();
    expect(order).toHaveLength(3);
    expect(order).toContain('a');
    expect(order).toContain('b');
    expect(order).toContain('c');
  });

  it('should detect cycles', () => {
    const g = new DependencyGraph<string>();
    g.addEdge('a', 'b');
    g.addEdge('b', 'c');
    g.addEdge('c', 'a');

    expect(() => g.topologicalSort()).toThrow('Cycle detected');
  });

  it('should handle linear chain', () => {
    const g = new DependencyGraph<number>();
    g.addEdge(1, 2);
    g.addEdge(2, 3);
    g.addEdge(3, 4);

    const order = g.topologicalSort();
    expect(order.indexOf(1)).toBeLessThan(order.indexOf(2));
    expect(order.indexOf(2)).toBeLessThan(order.indexOf(3));
    expect(order.indexOf(3)).toBeLessThan(order.indexOf(4));
  });
});
