---
title: "Pattern: Middleware / Pipeline Chain"
description: "Ghép handler, mỗi cái bọc cái tiếp theo — tiền xử lý, gọi next, hậu xử lý — tạo pipeline hai chiều."
difficulty: "intermediate"
---

# Pattern: Middleware / Pipeline Chain

<DifficultyBadge />

## Mô tả một câu

Ghép handler, mỗi cái bọc cái tiếp theo — tiền xử lý, gọi next, hậu xử lý — tạo pipeline hai chiều.

<DemoBadge />

## Tương tự thực tế

Trạm kiểm tra an ninh sân bay. Túi của bạn qua X-quang (log), rồi máy dò kim loại (auth), rồi kiểm tra giấy tờ (validation). Mỗi trạm làm một việc và đẩy bạn tới cái tiếp theo. Bất kỳ trạm nào cũng có thể từ chối bạn.

## Ý tưởng cốt lõi

Mỗi middleware nhận một context và hàm `next()`. Gọi `next()` chuyển điều khiển tới middleware tiếp trong chain. Sau khi `next()` trả về, middleware có thể chạy logic hậu xử lý. Không gọi `next()` short-circuit chain. Điều này tạo "mô hình hành tây" nơi request chảy vào trong và response chảy ra ngoài.

```text
  Request ──────────────────────────────────────► Response

  ┌─────────────────────────────────────────────────┐
  │  Middleware A (logging)                         │
  │  ┌─────────────────────────────────────────┐    │
  │  │  Middleware B (auth)                    │    │
  │  │  ┌─────────────────────────────────┐    │    │
  │  │  │  Middleware C (handler)         │    │    │
  │  │  │                                 │    │    │
  │  │  │  xử lý request → response       │    │    │
  │  │  │                                 │    │    │
  │  │  └─────────────────────────────────┘    │    │
  │  │  hậu xử lý (thêm header auth)           │    │
  │  └─────────────────────────────────────────┘    │
  │  hậu xử lý (log thời lượng)                     │
  └─────────────────────────────────────────────────┘

  Thứ tự thực thi:
  A.pre → B.pre → C.pre → C.post → B.post → A.post
```

| Thuộc tính | Giá trị |
|----------|-------|
| Ghép | O(n) middleware thực thi mỗi request |
| Short-circuit | Middleware nào cũng có thể bỏ qua phần còn lại bằng cách không gọi `next()` |
| Chia sẻ context | Mọi middleware chia sẻ cùng object context mutable |
| Hướng | Hai chiều — tiền xử lý khi đi vào, hậu xử lý khi đi ra |

**Thử ngay** — gửi request qua middleware chain và xem nó chảy tới rồi quay ngược:

<MiddlewareChainViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| gRPC-Go | [server.go#L1224-L1260](https://github.com/grpc/grpc-go/blob/f1864955bbb48efa131f6652933fa8b2189d9305/server.go#L1224-L1260) | `chainUnaryServerInterceptors` (L1224) chain interceptor thành một handler. `getChainUnaryHandler` (L1252) xây chain đệ quy — mỗi interceptor nhận request và hàm `handler` (tương đương `next`). Dùng cho xác thực, log, tracing và rate limit trong service gRPC production. |
| Koa.js | [application.js#L152-L204](https://github.com/koajs/koa/blob/78efdc87df1f8d49a494f313d478814d67c3f00f/lib/application.js#L152-L204) | `use()` (L152-L157) push middleware vào mảng. `callback()` (L168) ghép chúng qua `koa-compose` thành một hàm. `handleRequest` (L198-L205) thực thi chain đã ghép. Koa tiên phong mô hình hành tây async — mỗi `await next()` tạo stack frame, cho phép try/catch/finally sạch quanh middleware downstream. |

## Triển khai

::: code-group

```typescript [TypeScript]
type Middleware<T> = (ctx: T, next: () => void) => void;

class Pipeline<T> {
  private middlewares: Middleware<T>[] = [];

  /** Thêm middleware vào cuối chain. */
  use(middleware: Middleware<T>): void {
    this.middlewares.push(middleware);
  }

  /** Thực thi middleware chain với context cho. */
  execute(ctx: T): void {
    let index = 0;

    const next = (): void => {
      if (index < this.middlewares.length) {
        const mw = this.middlewares[index]!;
        index++;
        mw(ctx, next);
      }
    };

    next();
  }
}
```

```rust [Rust]
use std::collections::HashMap;

type Ctx = HashMap<String, String>;
type Next<'a> = Box<dyn FnOnce(&mut Ctx) + 'a>;
type MiddlewareFn = Box<dyn Fn(&mut Ctx, Next<'_>)>;

pub struct Pipeline {
    middlewares: Vec<MiddlewareFn>,
}

impl Pipeline {
    pub fn new() -> Self {
        Pipeline { middlewares: Vec::new() }
    }

    pub fn use_mw(&mut self, mw: impl Fn(&mut Ctx, Next<'_>) + 'static) {
        self.middlewares.push(Box::new(mw));
    }

    pub fn execute(&self, ctx: &mut Ctx) {
        self.run(ctx, 0);
    }

    fn run(&self, ctx: &mut Ctx, index: usize) {
        if index < self.middlewares.len() {
            let mw = &self.middlewares[index];
            let next: Next<'_> = Box::new(|c: &mut Ctx| {
                self.run(c, index + 1);
            });
            mw(ctx, next);
        }
    }
}
```

```go [Go]
type Handler func(ctx map[string]any)

type Middleware func(ctx map[string]any, next Handler)

func Chain(middlewares ...Middleware) Handler {
	return func(ctx map[string]any) {
		var run func(i int)
		run = func(i int) {
			if i < len(middlewares) {
				middlewares[i](ctx, func(c map[string]any) {
					run(i + 1)
				})
			}
		}
		run(0)
	}
}
```

```python [Python]
from typing import Any, Callable

Ctx = dict[str, Any]
NextFn = Callable[[], None]
MiddlewareFn = Callable[[Ctx, NextFn], None]

class Pipeline:
    def __init__(self) -> None:
        self._middlewares: list[MiddlewareFn] = []

    def use(self, middleware: MiddlewareFn) -> None:
        self._middlewares.append(middleware)

    def execute(self, ctx: Ctx) -> None:
        index = 0

        def next_fn() -> None:
            nonlocal index
            if index < len(self._middlewares):
                mw = self._middlewares[index]
                index += 1
                mw(ctx, next_fn)

        next_fn()
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Xây pipeline middleware đồng bộ với use/execute và short-circuit | `exercises/typescript/middleware-chain/01-basic.test.ts` |
| Trung bình | Mở rộng với middleware async, bắt lỗi và cleanup mô hình hành tây | `exercises/typescript/middleware-chain/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/middleware_chain/mod.rs` · Go `exercises/go/middleware_chain/middleware_chain_test.go` · Python `exercises/python/middleware_chain/test_middleware_chain.py`

## Khi nào nên dùng

- **Xử lý request HTTP** — xác thực, log, CORS, nén, rate limit thành lớp có thể ghép (Express, Koa, Gin, ASP.NET)
- **Interceptor RPC** — interceptor gRPC cho tracing, auth, retry và metric bọc mọi cuộc gọi không sửa logic nghiệp vụ
- **Pipeline build/compile** — loader Webpack, transform Babel, plugin PostCSS mỗi cái xử lý và chuyển tới cái tiếp
- **Xử lý command CLI** — parse argument, validation, sinh help như middleware trước handler command thực

## Khi nào KHÔNG nên dùng

- **Fan-out event (một-tới-nhiều)** — nếu cần nhiều handler độc lập cho cùng event, dùng pattern Observer. Middleware là chain (một đường), không phải broadcast.
- **Biến đổi không state** — nếu mỗi bước chỉ biến đổi dữ liệu không cần bọc bước kế (không pre/post), dùng pipeline `array.map().filter().reduce()` đơn giản. Sức mạnh middleware là bọc hai chiều; không có nó, bạn trả phức tạp vô ích.
- **Hot path then chốt hiệu năng** — mỗi middleware thêm cuộc gọi hàm và cấp phát closure. Trong vòng lặp xử lý hàng triệu item, overhead quan trọng. Dùng gọi hàm trực tiếp.

## Thêm các ứng dụng production

- [Express.js](https://github.com/expressjs/express) — `app.use()` chain middleware xử lý request HTTP
- [Redux](https://github.com/reduxjs/redux) — `applyMiddleware` bọc `dispatch` cho log, thunk, saga
- [ASP.NET Core](https://github.com/dotnet/aspnetcore) — pipeline middleware `IApplicationBuilder.Use()`
- [Gin](https://github.com/gin-gonic/gin) — framework HTTP Go với middleware `Use()` và `c.Next()`/`c.Abort()`

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Iterator](/patterns/iterator/) | Middleware chain lặp qua handler như iterator trên chuỗi |
| [Observer](/patterns/observer/) | Middleware có thể quan sát và sửa đổi request/response chảy qua pipeline |
| [Vtable](/patterns/vtable/) | Mỗi middleware là con trỏ hàm triển khai interface chung, như entry vtable |
| [Registry](/patterns/registry/) | Registry có thể lưu và quản lý các thành phần middleware trong chain |

## Câu hỏi thử thách

::: details Câu 1: Bạn có middleware A (log), B (auth), C (handler). Một user gửi request với token bất hợp lệ. B từ chối bằng cách KHÔNG gọi next(). Hậu xử lý của A thấy gì?
**Trả lời:** Hậu xử lý của A vẫn chạy. Khi B không gọi `next()`, C không bao giờ thực thi. Nhưng hàm B trả bình thường về A (vì A đã gọi `next()` mà gọi B). Code A sau cuộc gọi `next()` thực thi như thường.

Đây là mô hình hành tây trong hành động: A bọc B bọc C. Ngay cả khi B short-circuit, bọc của A vẫn còn nguyên. Đó là lý do middleware log hoạt động đúng kể cả cho request bị từ chối — nó ghi thời lượng và status bất kể middleware downstream có chạy không.
:::

::: details Câu 2: Bạn đổi thứ tự middleware auth và rate-limiter. Vấn đề bảo mật nào có thể tạo ra?
**Trả lời:** Nếu rate-limit chạy trước auth, request không xác thực tiêu thụ quota rate-limit. Kẻ tấn công có thể vắt kiệt rate limit cho user hợp pháp bằng cách gửi lũ request bất hợp lệ, gây từ chối dịch vụ cho user đã xác thực.

Nếu auth chạy trước, request bất hợp lệ bị từ chối ngay (rẻ) và không bao giờ tới rate limiter. Rate limiter sau đó chỉ đếm request đã xác thực, là hành vi đúng. **Thứ tự middleware là vấn đề bảo mật**, không chỉ tính đúng.
:::

::: details Câu 3: Koa dùng middleware `async/await`. Express dùng kiểu callback `(req, res, next)`. Khác biệt thực tế gì cho xử lý lỗi?
**Trả lời:** Trong Koa, `await next()` nghĩa lỗi từ middleware downstream tự lan qua promise rejection. Một try/catch trong middleware ngoài bắt mọi lỗi downstream:

```javascript
app.use(async (ctx, next) => {
  try { await next(); }
  catch (err) { ctx.status = 500; }
});
```

Trong Express, lỗi phải tường minh chuyển qua `next(err)`, và một error handler đặc biệt 4 tham số `(err, req, res, next)` phải được đăng ký. Nếu middleware ném đồng bộ hoặc callback async reject không gọi `next(err)`, lỗi mất và request treo.

Mô hình async/await làm pattern hành tây tự nhiên — try/catch/finally map trực tiếp tới setup/handle/cleanup.
:::

::: details Câu 4: Bạn có thể triển khai thứ tự middleware chạy chỉ cho route cụ thể (như `app.get('/api', authMiddleware, handler)` của Express) không?
**Trả lời:** Có — thêm predicate cho mỗi middleware kiểm tra context trước khi thực thi. Pipeline bọc mỗi middleware trong điều kiện:

```javascript
function routeMiddleware(path, mw) {
  return (ctx, next) => {
    if (ctx.path.startsWith(path)) { mw(ctx, next); }
    else { next(); } // bỏ qua middleware này
  };
}
```

Express triển khai điều này bằng cách duy trì stack middleware riêng mỗi route. Khi request đến, tìm route khớp và chỉ chạy chain middleware của route đó. Đây cơ bản là cây pipeline thay vì một chain phẳng duy nhất.
:::
