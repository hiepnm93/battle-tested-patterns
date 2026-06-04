type Handler = () => void;

class EventLoop {
  private handlers = new Map<number, Handler>();

  /** Register a handler for a file descriptor. */
  addHandler(fd: number, callback: Handler): void {
    this.handlers.set(fd, callback);
  }

  /** Remove a handler for a file descriptor. */
  removeHandler(fd: number): void {
    this.handlers.delete(fd);
  }

  /** Execute one tick: call all registered handlers once. */
  tick(): number {
    const count = this.handlers.size;
    for (const [, handler] of this.handlers) {
      handler();
    }
    return count;
  }

  /** Run the event loop for up to maxTicks. Stops early if no handlers. */
  run(maxTicks: number): number {
    let ticksRun = 0;
    for (let i = 0; i < maxTicks; i++) {
      if (this.handlers.size === 0) break;
      this.tick();
      ticksRun++;
    }
    return ticksRun;
  }

  get handlerCount(): number {
    return this.handlers.size;
  }
}
