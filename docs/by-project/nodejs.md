---
title: "Pattern trong hệ sinh thái Node.js"
description: "Pattern hệ sinh thái Node.js: observer (EventEmitter), backpressure (Streams), state machine (XState) và middleware chain (Koa)."
---

# Pattern trong hệ sinh thái Node.js

Node.js, Redux và XState minh hoạ các pattern hướng sự kiện và quản lý state ở quy mô lớn.

| Pattern | Dự án | Ở đâu | Tác dụng |
|---------|---------|-------|--------------|
| [Observer / Pub-Sub](/patterns/observer/) | Node.js | [`lib/events.js`](https://github.com/nodejs/node/blob/19c46abbefdb8711b913d7237b3c1299367f87d7/lib/events.js#L456-L520) | `EventEmitter` — nền tảng của kiến trúc hướng sự kiện trong Node |
| [Observer / Pub-Sub](/patterns/observer/) | Redux | [`createStore.ts`](https://github.com/reduxjs/redux/blob/1d761f471cf58faabe88c50ea16645212d986cd0/src/createStore.ts#L211-L280) | `subscribe()` + `dispatch()` — thông báo thay đổi state |
| [State Machine](/patterns/state-machine/) | XState | [`StateMachine.ts`](https://github.com/statelyai/xstate/blob/9d9b9f1439b773979c5120a793215f5aa4568d8f/packages/core/src/StateMachine.ts#L58-L120) | Thư viện finite state machine tiêu chuẩn ngành |
| [Backpressure](/patterns/backpressure/) | Node.js | [`writable.js`](https://github.com/nodejs/node/blob/19c46abbefdb8711b913d7237b3c1299367f87d7/lib/internal/streams/writable.js#L548-L585) | `writeOrBuffer()` — kiểm soát luồng `highWaterMark` + sự kiện `drain` |
| [Iterator / Đánh giá lười](/patterns/iterator/) | Node.js | [`lib/internal/streams/`](https://github.com/nodejs/node/tree/19c46abbefdb8711b913d7237b3c1299367f87d7/lib/internal/streams) | Async iterator cho stream — `for await (const chunk of stream)` |
| [Retry Backoff](/patterns/retry-backoff/) | Node.js | [`dns`](https://github.com/nodejs/node/blob/19c46abbefdb8711b913d7237b3c1299367f87d7/lib/dns.js), [`http`](https://github.com/nodejs/node/blob/19c46abbefdb8711b913d7237b3c1299367f87d7/lib/http.js) | Retry phân giải DNS với backoff cấp số nhân |
| [Dependency Graph](/patterns/dependency-graph/) | pnpm | [`graph-sequencer`](https://github.com/pnpm/pnpm/blob/46fd26afc9926b4391636a851ae32493f9b2c9ff/deps/graph-sequencer/src/index.ts#L22-L125) | Sắp xếp topo các package workspace để xác định thứ tự build |
| [Rate Limiter](/patterns/rate-limiter/) | Express | [`express-rate-limit`](https://github.com/express-rate-limit/express-rate-limit) | Middleware token bucket cho rate limit API |
| [Circuit Breaker](/patterns/circuit-breaker/) | opossum | [`lib/circuit.js`](https://github.com/nodeshift/opossum/blob/506c3c056781c2cc5a6c175f46259172edc29859/lib/circuit.js) | Circuit breaker Node.js cho phục hồi microservice |
| [Event Loop](/patterns/event-loop/) | Node.js (libuv) | [`deps/uv/src/unix/core.c`](https://github.com/nodejs/node/blob/19c46abbefdb8711b913d7237b3c1299367f87d7/deps/uv/src/unix/core.c) | `uv_run()` — ghép kênh I/O đơn luồng qua epoll/kqueue |
| [Middleware Chain](/patterns/middleware-chain/) | Koa.js | [`koa-compose`](https://github.com/koajs/compose/blob/9a2a426b32c614835b812ecb8de5af06c6c87f6f/index.js) | Ghép middleware thành pipeline mô hình hành tây với `async/await` |

## Cách chúng kết hợp: Một request HTTP

Khi server Express/Koa xử lý một request, các pattern kết hợp từ lớp mạng cho tới response:

<CompositionFlow variant="nodejs-request" />

Event loop là nền tảng: mọi thứ chạy trên một thread duy nhất và I/O không bao giờ block. Đó là lý do Node.js có thể xử lý hàng nghìn kết nối đồng thời — mỗi request dùng các pattern (middleware, observer, backpressure) thay vì sinh thêm thread.

## Đọc thêm

- [Node.js (GitHub)](https://github.com/nodejs/node) · [Redux (GitHub)](https://github.com/reduxjs/redux) · [XState (GitHub)](https://github.com/statelyai/xstate)
- [pnpm (GitHub)](https://github.com/pnpm/pnpm)
