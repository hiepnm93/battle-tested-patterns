# 模式：指数退避重试 (Retry with Backoff)

## 一句话

操作失败时以指数增长的延迟重试，加随机抖动避免惊群效应。

## 核心思想

不立即重试（会压垮故障服务），也不直接放弃，而是每次重试加倍等待时间。加抖动让成千上万客户端不同时重试。

```text
尝试 1: 失败 → 等 1s + 抖动
尝试 2: 失败 → 等 2s + 抖动
尝试 3: 失败 → 等 4s + 抖动
尝试 4: 失败 → 等 8s + 抖动（封顶）
尝试 5: 成功 ✓
```

## 生产验证

| 项目 | 源码 | 用途 |
|------|------|------|
| Kubernetes | [backoff.go#L30-L50](https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/apimachinery/pkg/util/wait/backoff.go#L30-L50) | `Backoff` 结构定义退避参数。`ExponentialBackoff`（行475）实现重试。用于 pod 重启、API 服务器重试。 |
| gRPC | [connection-backoff.md](https://github.com/grpc/grpc/blob/master/doc/connection-backoff.md) | gRPC 连接退避规范：初始 1s，乘以 1.6，抖动 ±20%，封顶 120s。全球每个 gRPC 连接都实现此算法。 |

## 实现

::: code-group

```typescript [TypeScript]
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries = 5, baseDelay = 1000, maxDelay = 30000,
): Promise<T> {
  let lastError: Error | undefined;
  for (let i = 0; i <= maxRetries; i++) {
    try { return await fn(); }
    catch (err) {
      lastError = err as Error;
      if (i === maxRetries) break;
      const delay = Math.min(baseDelay * Math.pow(2, i), maxDelay);
      await new Promise((r) => setTimeout(r, delay));
    }
  }
  throw lastError;
}
```

```python [Python]
import time, random

def retry_with_backoff(fn, max_retries=5, base=1.0, cap=30.0):
    for attempt in range(max_retries + 1):
        try: return fn()
        except Exception as e:
            if attempt == max_retries: raise
            delay = min(base * 2**attempt + random.random(), cap)
            time.sleep(delay)
```

:::

## 练习

| 难度 | 练习 | 文件 |
|------|------|------|
| 基础 | 实现可配置退避的重试 | `exercises/typescript/retry-backoff/01-basic.test.ts` |

## 何时使用

- **网络请求** — HTTP、数据库连接、RPC
- **分布式系统** — 可能暂时失败的服务间调用
- **限流 API** — 命中频率限制时退避（429 响应）

## 何时不用

- **非瞬时错误** — 400 Bad Request 重试也不会成功
- **非幂等操作** — 重试非幂等 POST 可能创建重复数据
- **用户等待场景** — 指数退避意味着 30+ 秒等待

## 其他使用者

AWS SDK, Azure SDK, Google Cloud 客户端, Envoy, Istio, Celery, Sidekiq.
