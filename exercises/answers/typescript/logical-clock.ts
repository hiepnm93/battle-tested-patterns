class LamportClock {
  private time = 0;

  /** Increment the clock for a local event. */
  tick(): void {
    this.time++;
  }

  /** Record a send event and return the timestamp. */
  send(): number {
    this.time++;
    return this.time;
  }

  /** Receive a message with a remote timestamp. */
  receive(remoteTimestamp: number): void {
    this.time = Math.max(this.time, remoteTimestamp) + 1;
  }

  /** Current clock value. */
  now(): number {
    return this.time;
  }
}
