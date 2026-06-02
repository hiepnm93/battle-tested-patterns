import { describe, it, expect } from 'vitest';

/**
 * Work Stealing - Basic: Implement a work-stealing scheduler.
 *
 * TODO: Implement a scheduler where each worker has its own deque.
 * Workers pop from their own deque; idle workers steal from others.
 */

class WorkStealingScheduler {
  private queues: number[][];
  private results: number[] = [];

  constructor(workerCount: number) {
    // TODO: implement
    this.queues = Array.from({ length: workerCount }, () => []);
  }

  submit(task: number, workerIdx: number): void {
    // TODO: implement
    this.queues[workerIdx]!.push(task);
  }

  run(process: (task: number) => number): number[] {
    // TODO: implement
    const results: number[] = [];
    let anyWork = true;
    while (anyWork) {
      anyWork = false;
      for (let w = 0; w < this.queues.length; w++) {
        if (this.queues[w]!.length > 0) {
          anyWork = true;
          const task = this.queues[w]!.pop()!;
          results.push(process(task));
        } else {
          for (let other = 0; other < this.queues.length; other++) {
            if (other !== w && this.queues[other]!.length > 1) {
              anyWork = true;
              const stolen = this.queues[other]!.shift()!;
              results.push(process(stolen));
              break;
            }
          }
        }
      }
    }
    return results;
  }

  queueSize(workerIdx: number): number {
    return this.queues[workerIdx]!.length;
  }
}

// ─── Tests (do not modify below this line) ───────────────────────

describe('Work Stealing - Basic', () => {
  it('should process all tasks', () => {
    const scheduler = new WorkStealingScheduler(2);
    scheduler.submit(1, 0);
    scheduler.submit(2, 0);
    scheduler.submit(3, 1);

    const results = scheduler.run((t) => t * 10);
    expect(results.sort((a, b) => a - b)).toEqual([10, 20, 30]);
  });

  it('should steal work from busy workers', () => {
    const scheduler = new WorkStealingScheduler(3);
    scheduler.submit(1, 0);
    scheduler.submit(2, 0);
    scheduler.submit(3, 0);
    scheduler.submit(4, 0);

    const results = scheduler.run((t) => t);
    expect(results).toHaveLength(4);
    expect(results.sort((a, b) => a - b)).toEqual([1, 2, 3, 4]);
  });

  it('should handle empty scheduler', () => {
    const scheduler = new WorkStealingScheduler(2);
    const results = scheduler.run((t) => t);
    expect(results).toEqual([]);
  });

  it('should track queue sizes', () => {
    const scheduler = new WorkStealingScheduler(2);
    scheduler.submit(1, 0);
    scheduler.submit(2, 0);
    scheduler.submit(3, 1);

    expect(scheduler.queueSize(0)).toBe(2);
    expect(scheduler.queueSize(1)).toBe(1);
  });
});
