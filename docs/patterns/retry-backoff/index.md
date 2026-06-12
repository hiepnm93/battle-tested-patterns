---
title: "Pattern: Retry với Exponential Backoff"
description: "Khi một thao tác thất bại, retry với delay tăng dần cộng jitter ngẫu nhiên để tránh thundering herd."
difficulty: "beginner"
---

# Pattern: Retry với Exponential Backoff

<DifficultyBadge />

## Mô tả một câu

Khi một thao tác thất bại, retry với delay tăng dần cộng jitter ngẫu nhiên để tránh thundering herd.

<DemoBadge />

## Tương tự thực tế

Gọi một nhà hàng đông khách để đặt chỗ. Bạn gọi lần đầu, máy bận, đợi một phút, gọi lại. Vẫn bận? Đợi hai phút. Rồi bốn. Bạn cũng thay đổi thời gian một chút để mọi người đã gặp máy bận không cùng gọi lại đúng một lúc.

## Ý tưởng cốt lõi

Thay vì retry ngay (làm quá tải service đang lỗi) hoặc bỏ cuộc (mất request), exponential backoff nhân đôi thời gian chờ mỗi lần retry. Thêm jitter ngẫu nhiên hoá delay để hàng nghìn client không cùng retry đồng thời.

```text
  Thời gian ────────────────────────────────────────────►

  Thử 1  ✗ ├─┤ 1s
  Thử 2  ✗ ├───┤ 2s
  Thử 3  ✗ ├───────┤ 4s
  Thử 4  ✗ ├───────────────┤ 8s
  Thử 5  ✗ ├───────────────────────────────┤ 16s (cap)
  Thử 6  ✓

  Mỗi thanh = chờ trước khi retry kế tiếp (gấp đôi mỗi lần)
  + jitter: ngẫu nhiên trong mỗi thanh để tránh thundering herd
```

Công thức: `delay = min(base * 2^attempt + random(0, jitter), maxDelay)`

| Thuộc tính | Giá trị |
|----------|-------|
| Tăng delay | Cấp số nhân — gấp đôi mỗi lần thử |
| Delay max | Có cap (thường 30–60 giây) để giới hạn chờ tệ nhất |
| Jitter | Ngẫu nhiên để chặn thundering herd |
| Số lần thử | Có giới hạn (thường 3–10) để tránh vòng vô tận |

**Thử ngay** — gửi request và xem exponential backoff với jitter hoạt động:

<RetryBackoffViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| Kubernetes | [backoff.go#L30-L50](https://github.com/kubernetes/kubernetes/blob/586cc904093af4fe7492e564908a796f0b107f97/staging/src/k8s.io/apimachinery/pkg/util/wait/backoff.go#L30-L50) | Struct `Backoff` định nghĩa `Duration`, `Factor`, `Jitter`, `Steps`, `Cap`. `ExponentialBackoff` (dòng 475) retry với config này. Dùng cho backoff khởi động lại pod, retry API server, reconciliation controller. |
| gRPC-Go | [backoff.go#L56-L75](https://github.com/grpc/grpc-go/blob/f1864955bbb48efa131f6652933fa8b2189d9305/internal/backoff/backoff.go#L56-L75) | `Exponential.Backoff()` — tính delay cấp số nhân với jitter. Delay cơ sở gấp đôi mỗi retry, cap ở `MaxDelay`. `RunF` (L86-L109) là vòng lặp điều phối retry với huỷ context và hỗ trợ `ErrResetBackoff`. |

## Triển khai

::: code-group

```typescript [TypeScript]
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
```

```rust [Rust]
use std::time::Duration;

pub struct Backoff {
    pub max_retries: u32,
    pub base_delay: Duration,
    pub max_delay: Duration,
}

impl Backoff {
    pub fn delay_for(&self, attempt: u32) -> Duration {
        let exponential = self.base_delay.as_millis() as u64 * 2u64.pow(attempt);
        let capped = exponential.min(self.max_delay.as_millis() as u64);
        Duration::from_millis(capped)
    }
}
```

```go [Go]
package backoff

import (
	"math"
	"math/rand"
	"time"
)

type Config struct {
	MaxRetries int
	BaseDelay  time.Duration
	MaxDelay   time.Duration
	Jitter     float64
}

func Retry(fn func() error, cfg Config) error {
	var lastErr error
	for attempt := 0; attempt <= cfg.MaxRetries; attempt++ {
		lastErr = fn()
		if lastErr == nil {
			return nil
		}
		if attempt == cfg.MaxRetries {
			break
		}
		exp := float64(cfg.BaseDelay) * math.Pow(2, float64(attempt))
		jitter := exp * cfg.Jitter * rand.Float64()
		delay := time.Duration(math.Min(exp+jitter, float64(cfg.MaxDelay)))
		time.Sleep(delay)
	}
	return lastErr
}
```

```python [Python]
import time
import random

def retry_with_backoff(fn, max_retries=5, base_delay=1.0, max_delay=30.0, jitter=0.5):
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception as e:
            last_error = e
            if attempt == max_retries:
                break
            exponential = base_delay * (2 ** attempt)
            delay = min(exponential + exponential * jitter * random.random(), max_delay)
            time.sleep(delay)
    raise last_error
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai retry với backoff cấu hình được | `exercises/typescript/retry-backoff/01-basic.test.ts` |
| Trung bình | Retry tích hợp với circuit breaker | `exercises/typescript/retry-backoff/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/retry_backoff/mod.rs` · Go `exercises/go/retry_backoff/retry_backoff_test.go` · Python `exercises/python/retry_backoff/test_retry_backoff.py`

## Khi nào nên dùng

- **Request mạng** — cuộc gọi HTTP, kết nối database, RPC
- **Hệ phân tán** — cuộc gọi service-to-service có thể lỗi thoáng qua
- **API có rate limit** — backoff khi đụng rate limit (thường response 429)
- **Consumer queue** — retry xử lý thông điệp thất bại

## Khi nào KHÔNG nên dùng

- **Lỗi không thoáng qua** — 400 Bad Request không thành công khi retry; hãy kiểm tra input
- **Không đảm bảo idempotency** — retry POST không idempotent có thể tạo bản trùng
- **Độ trễ thấy được với người dùng** — backoff cấp số nhân nghĩa là chờ 30+ giây; hiển thị lỗi
- **Thao tác cục bộ** — file không tìm thấy, lỗi parse — không tự sửa khi retry

## Thêm các ứng dụng production

- [AWS SDK](https://github.com/aws/aws-sdk-js-v3)
- [Azure SDK](https://github.com/Azure/azure-sdk-for-js)
- [Google Cloud](https://github.com/googleapis/google-cloud-node)
- [Envoy](https://github.com/envoyproxy/envoy) — proxy
- [Celery](https://github.com/celery/celery) — task queue Python

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Circuit Breaker](/patterns/circuit-breaker/) | Circuit breaker cho biết khi nào dừng retry hoàn toàn |
| [Batch Processing](/patterns/batch-processing/) | Item batch thất bại có thể retry với backoff độc lập |
| [Rate Limiter (Token Bucket)](/patterns/rate-limiter/) | Backoff có jitter ngăn bão retry, tương tự mục tiêu của rate limit |

## Câu hỏi thử thách

::: details Câu 1: Bạn loại bỏ jitter trong logic retry để delay "dễ đoán". Trong kịch bản thundering herd, chuyện gì xảy ra?
**Trả lời:** Mọi client đã thất bại cùng lúc retry chính xác cùng khoảng thời gian, liên tục làm quá tải service đang hồi phục theo các đợt đồng bộ.

Không có jitter, 10.000 client nhận 503 ở t=0 đều retry ở t=1s, rồi t=2s, rồi t=4s — tạo các đỉnh traffic định kỳ ngăn hồi phục. Jitter trải retry qua cửa sổ delay nên service hồi phục thấy luồng nhỏ giọt mượt thay vì burst đồng bộ. Đó là lý do mọi thư viện retry production đều có jitter.
:::

::: details Câu 2: Service của bạn retry endpoint POST /create-order KHÔNG idempotent. Lần thử đầu time out nhưng thực sự đã thành công trên server. Chuyện gì khi retry?
**Trả lời:** Retry tạo bản trùng order. Khách bị tính tiền hai lần.

Timeout không có nghĩa request thất bại — nghĩa là bạn không biết nó có thành công không. Retry thao tác không idempotent có nguy cơ trùng. Cách sửa là làm thao tác idempotent bằng idempotency key: client sinh ID duy nhất và server khử trùng. Không có idempotency, không nên retry thao tác ghi.
:::

::: details Câu 3: Service downstream trả HTTP 400 Bad Request. Bạn có nên retry với exponential backoff?
**Trả lời:** Không. 400 là lỗi client cho thấy input sai. Retry cùng request sẽ ra cùng lỗi mỗi lần.

Retry với backoff được thiết kế cho lỗi thoáng qua — 503 Service Unavailable, 429 Too Many Requests, timeout mạng, reset kết nối. 400 nghĩa là "request của bạn sai định dạng", không tự sửa theo thời gian. Retry nó lãng phí tài nguyên và trì hoãn việc sửa thật sự (chỉnh input). Luôn phân loại lỗi trước khi quyết định retry.
:::

::: details Câu 4: Config retry của bạn dùng baseDelay=1s, maxDelay=30s, maxRetries=10. Một kỹ sư junior hỏi: "Sao không đặt maxRetries=1000 để không bao giờ mất request?" Sai ở đâu?
**Trả lời:** Với backoff cấp số nhân cap ở 30s và 1000 retry, client có thể dành tới 8+ giờ retry một request duy nhất, giữ tài nguyên suốt thời gian đó.

Số retry cao tiêu tốn slot pool kết nối, bộ nhớ, goroutine/thread và thường giữ transaction hoặc khoá database mở. Nếu service downstream thực sự sập, các retry đó không giúp — bạn cần circuit breaker để fail nhanh và đẩy tải đi. Thực tế, 3-5 retry với backoff đủ xử lý gián đoạn thoáng qua; lâu hơn nên xử lý bởi queue bền vững với ngữ nghĩa dead-letter.
:::
