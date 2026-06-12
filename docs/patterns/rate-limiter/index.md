---
title: "Pattern: Rate Limiter (Token Bucket)"
description: "Bảo vệ service khỏi quá tải bằng cách rút token từ một bucket refill ở tốc độ cố định — từ chối request khi rỗng."
difficulty: "intermediate"
---

# Pattern: Rate Limiter (Token Bucket)

<DifficultyBadge />

## Mô tả một câu

Bảo vệ service khỏi quá tải bằng cách rút token từ một bucket refill ở tốc độ cố định — từ chối request khi rỗng.

<DemoBadge />

## Tương tự thực tế

Cửa xoay ở ga tàu điện ngầm. Nó cho một người qua mỗi lần quẹt thẻ, ở nhịp được kiểm soát. Nếu đám đông xô vào, họ xếp hàng. Cửa xoay không tăng tốc — nó thi hành nhịp ổn định.

## Ý tưởng cốt lõi

Token bucket bắt đầu đầy với `capacity` token và refill ở `rate` token mỗi giây. Mỗi request tiêu thụ một token. Nếu bucket rỗng, request bị từ chối hoặc delay. Điều này tự nhiên cho phép burst (tới capacity) trong khi thi hành tốc độ trung bình.

```text
  Token Bucket (capacity=5, rate=2/giây)

  Time 0s:   [●][●][●][●][●]  5 token (đầy)
  Request:   [●][●][●][●][ ]  4 token (đã tiêu 1)
  Request:   [●][●][●][ ][ ]  3 token
  Request:   [●][●][ ][ ][ ]  2 token

  +1 giây:   [●][●][●][●][ ]  4 token (refill 2)
  +2 giây:   [●][●][●][●][●]  5 token (cap ở capacity)
```

| Biến thể | Hành vi |
|---------|----------|
| **Token Bucket** | Token tích luỹ; cho phép burst tới capacity |
| **Leaky Bucket** | Request rút ở tốc độ hằng; làm mịn burst |
| **Sliding Window** | Đếm request trong cửa sổ thời gian; không kiểm soát burst |
| **Fixed Window** | Đếm request mỗi khoảng thời gian; vấn đề burst ở biên |

| Thuộc tính | Giá trị |
|----------|-------|
| Check allow() | O(1) — tính token đã trôi qua, so với request |
| Chịu burst | Lên tới `capacity` request tức thì |
| Tốc độ duy trì | `refillRate` request mỗi giây |
| Bộ nhớ | O(1) — count token + timestamp mỗi limiter |

**Thử ngay** — gửi request và xem token rút khỏi bucket, rồi bật auto-refill:

<RateLimiterViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| Go x/time/rate | [rate.go#L57-L66](https://github.com/golang/time/blob/812b343c8714c317b0dad633efa6d103e554c006/rate/rate.go#L57-L66) | Struct `Limiter` — token bucket với `tokens`, `limit`, `burst` và timestamp `last`. `reserveN` (L337-L381) là thuật toán cốt lõi: tiến token theo thời gian trôi qua, trừ `n` yêu cầu, tính thời gian chờ. Dùng khắp hệ sinh thái Go. |
| Nginx | [ngx_http_limit_req_module.c#L405-L532](https://github.com/nginx/nginx/blob/d994f5b8220847eb8f7e4400be5f7e6eb4538e46/src/http/modules/ngx_http_limit_req_module.c#L405-L532) | `ngx_http_limit_req_lookup` — triển khai leaky bucket. L454: `excess = lr->excess - ctx->rate * ms / 1000 + 1000` rút phần thừa theo thời gian trôi qua và thêm một request. Chạy directive `limit_req` bảo vệ hàng triệu server Nginx. |

## Triển khai

::: code-group

```typescript [TypeScript]
class TokenBucket {
  private tokens: number;
  private lastRefill: number;

  constructor(
    private capacity: number,
    private refillRate: number,
  ) {
    this.tokens = capacity;
    this.lastRefill = Date.now();
  }

  private refill(): void {
    const now = Date.now();
    const elapsed = (now - this.lastRefill) / 1000;
    this.tokens = Math.min(this.capacity, this.tokens + elapsed * this.refillRate);
    this.lastRefill = now;
  }

  tryAcquire(tokens = 1): boolean {
    this.refill();
    if (this.tokens >= tokens) {
      this.tokens -= tokens;
      return true;
    }
    return false;
  }
}
```

```rust [Rust]
use std::time::Instant;

pub struct TokenBucket {
    capacity: f64,
    refill_rate: f64,
    tokens: f64,
    last_refill: Instant,
}

impl TokenBucket {
    pub fn new(capacity: f64, refill_rate: f64) -> Self {
        TokenBucket { capacity, refill_rate, tokens: capacity, last_refill: Instant::now() }
    }

    fn refill(&mut self) {
        let elapsed = self.last_refill.elapsed().as_secs_f64();
        self.tokens = (self.tokens + elapsed * self.refill_rate).min(self.capacity);
        self.last_refill = Instant::now();
    }

    pub fn try_acquire(&mut self, n: f64) -> bool {
        self.refill();
        if self.tokens >= n {
            self.tokens -= n;
            true
        } else {
            false
        }
    }
}
```

```go [Go]
type TokenBucket struct {
	capacity   float64
	refillRate float64
	tokens     float64
	lastRefill time.Time
}

func NewTokenBucket(capacity, refillRate float64) *TokenBucket {
	return &TokenBucket{capacity: capacity, refillRate: refillRate, tokens: capacity, lastRefill: time.Now()}
}

func (tb *TokenBucket) TryAcquire() bool {
	now := time.Now()
	elapsed := now.Sub(tb.lastRefill).Seconds()
	tb.tokens = min(tb.capacity, tb.tokens+elapsed*tb.refillRate)
	tb.lastRefill = now
	if tb.tokens >= 1 {
		tb.tokens--
		return true
	}
	return false
}

func min(a, b float64) float64 {
	if a < b {
		return a
	}
	return b
}
```

```python [Python]
import time

class TokenBucket:
    def __init__(self, capacity: float, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def try_acquire(self, tokens: float = 1) -> bool:
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai rate limiter token bucket | `exercises/typescript/rate-limiter/01-basic.test.ts` |
| Trung bình | Rate limiter counter cửa sổ trượt | `exercises/typescript/rate-limiter/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/rate_limiter/mod.rs` · Go `exercises/go/rate_limiter/rate_limiter_test.go` · Python `exercises/python/rate_limiter/test_rate_limiter.py`

## Khi nào nên dùng

- **Rate limit API** — bảo vệ endpoint khỏi lạm dụng (GitHub, Twitter, Stripe)
- **Tạo hình traffic mạng** — kiểm soát cấp phát băng thông (Linux tc, Nginx)
- **Bảo vệ tài nguyên** — giới hạn truy vấn database, I/O file hoặc thao tác CPU nặng
- **Dùng công bằng** — đảm bảo hệ đa khách hàng cấp quyền truy cập công bằng

## Khi nào KHÔNG nên dùng

- **Kiểm soát truy cập nhị phân** — nếu chỉ cần allow/deny, dùng xác thực, không phải rate limit
- **Đếm chính xác** — token bucket xấp xỉ; dùng counter cho giới hạn chính xác
- **Phân tán không phối hợp** — token bucket mỗi node không thi hành tốc độ toàn cục (dùng limiter nền Redis)
- **Đường nhạy độ trễ** — tính refill thêm overhead trên mỗi request

## Thêm các ứng dụng production

- [Linux TBF](https://github.com/torvalds/linux/blob/acb7500801e98639f6d8c2d796ed9f64cba83d3a/net/sched/sch_tbf.c#L98-L114) — kernel token bucket filter cho kiểm soát traffic
- [Guava RateLimiter](https://github.com/google/guava/blob/3e65944ec9207ca652128969fd1334e9920dde07/guava/src/com/google/common/util/concurrent/SmoothRateLimiter.java#L357-L369) — rate limit mượt với warm-up
- [Envoy](https://github.com/envoyproxy/envoy) — rate limit local/global cho service mesh
- [AWS API Gateway](https://github.com/aws/aws-sdk-js-v3) — throttling token bucket cho endpoint API

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Semaphore](/patterns/semaphore/) | Semaphore giới hạn concurrency; rate limiter giới hạn throughput theo thời gian |
| [Backpressure](/patterns/backpressure/) | Rate limit là dạng backpressure áp tại biên hệ thống |
| [Circuit Breaker](/patterns/circuit-breaker/) | Circuit breaker chặn mọi traffic khi lỗi; rate limiter kiểm soát khối lượng traffic khoẻ |
| [Consistent Hashing](/patterns/consistent-hashing/) | Consistent hashing phân tán state rate limit qua các node |
| [Retry with Backoff](/patterns/retry-backoff/) | Retry-backoff thích nghi hành vi client với phản hồi rate limiter |

## Câu hỏi thử thách

::: details Câu 1: API của bạn cho 100 request mỗi phút dùng counter fixed-window. Lúc 11:00:59 client gửi 100 request, và lúc 11:01:01 gửi thêm 100. Cả hai cửa sổ cho phép. Tốc độ thực tế trong 2 giây đó là gì, và token bucket sẽ xử lý khác thế nào?
**Trả lời:** Client đã gửi 200 request trong 2 giây (tốc độ hiệu quả 6.000/phút), vượt xa giới hạn 100/phút. Token bucket sẽ từ chối phần lớn burst thứ hai vì chỉ có ~3 token refill.

Đây là vấn đề "burst biên" với counter fixed-window. Cửa sổ reset ở biên sắc, cho phép double-burst ở khe. Token bucket với capacity=100 và rate=100/phút refill ở ~1,67 token/giây. Sau khi rút về 0 lúc 11:00:59, chỉ ~3 token có sẵn lúc 11:01:01 — 97 request còn lại sẽ bị từ chối. Counter cửa sổ trượt cũng giải bằng cách nội suy giữa các cửa sổ kề.
:::

::: details Câu 2: Bạn chạy 8 instance server API, mỗi cái có token bucket riêng cho 100 request/giây. Client phát hiện và phân tán request qua cả 8 server. Giới hạn rate hiệu quả họ trải nghiệm là gì?
**Trả lời:** Client có thể đạt 800 request/giây — 8x giới hạn dự kiến — vì token bucket mỗi node không thi hành tốc độ toàn cục.

Rate limit phân tán cần state chia sẻ. Giải pháp phổ biến: (1) store tập trung như Redis với `INCR` và `EXPIRE` atomic, (2) service rate-limit chuyên dụng (Envoy, Kong), hoặc (3) cách "chia ngân sách" nơi mỗi node nhận 1/n tổng tốc độ (100/8 = 12,5 req/s mỗi node). Cách 3 đơn giản nhưng mong manh — nếu traffic không phân tán đều, vài node lãng phí ngân sách trong khi cái khác từ chối request hợp lệ.
:::

::: details Câu 3: Token bucket của bạn có capacity=50 và refill rate=10/giây. Một batch job hợp pháp cần gửi 50 request một lúc, rồi chờ 10 giây, rồi gửi thêm 50. Token bucket có chứa được mẫu này không hay nên dùng thuật toán khác?
**Trả lời:** Token bucket xử lý hoàn hảo — thiết kế cho phép burst tới capacity trong khi thi hành tốc độ trung bình.

Lúc đầu, bucket đầy với 50 token, cho cả batch. Trong 10 giây tiếp, 100 token refill nhưng cap ở 50 (capacity). Batch thứ hai 50 cái rút bucket lại. Tốc độ trung bình là 100 request / 10 giây = 10/giây, khớp chính xác refill rate. Hành vi thân thiện burst này là lý do token bucket ưu tiên hơn leaky bucket cho tải bursty-nhưng-giới-hạn. Leaky bucket sẽ buộc 50 request rút ở 10/giây, mất 5 giây — không phù hợp mẫu batch.
:::

::: details Câu 4: Nginx dùng leaky bucket cho `limit_req`. `x/time/rate` của Go dùng token bucket. Cả hai giới hạn tốc độ request. Khi nào chọn leaky bucket hơn token bucket?
**Trả lời:** Chọn leaky bucket khi cần làm mịn traffic thành luồng ổn định, ngăn mọi burst đến service downstream.

Token bucket cho phép burst tới capacity — tuyệt cho API hướng user nơi traffic burst đôi khi là bình thường. Leaky bucket buộc tốc độ rút hằng, bảo vệ backend không xử lý được đỉnh traffic (ví dụ database thoái hoá khi ghi đồng thời). Nginx dùng leaky bucket vì reverse proxy nằm trước backend cần tải dự đoán, trạng thái ổn định. Đánh đổi: leaky bucket thêm độ trễ khi burst (request xếp hàng), trong khi token bucket từ chối request thừa ngay.
:::
