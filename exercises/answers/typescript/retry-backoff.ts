interface BackoffConfig {
  maxRetries: number;
  baseDelay: number;
  maxDelay: number;
  jitter: number; // 0-1
}

async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  config: BackoffConfig = { maxRetries: 5, baseDelay: 1000, maxDelay: 30000, jitter: 0.5 },
): Promise<T> {
  let lastError: Error | undefined;

  for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      lastError = err as Error;
      if (attempt === config.maxRetries) break;

      const exponential = config.baseDelay * Math.pow(2, attempt);
      const jitter = exponential * config.jitter * Math.random();
      const delay = Math.min(exponential + jitter, config.maxDelay);

      await new Promise((r) => setTimeout(r, delay));
    }
  }

  throw lastError;
}
