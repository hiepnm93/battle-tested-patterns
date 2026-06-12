---
title: "Pattern: Logical Clock / Epoch"
description: "Bộ đếm tăng đơn điệu sắp xếp sự kiện không cần wall-clock — cho phép snapshot nhất quán và phát hiện cũ."
difficulty: "advanced"
---

# Pattern: Logical Clock / Epoch

<DifficultyBadge />

## Mô tả một câu

Bộ đếm tăng đơn điệu sắp xếp sự kiện không cần wall-clock — cho phép snapshot nhất quán và phát hiện cũ.

<DemoBadge />

## Tương tự thực tế

Đánh số thông điệp trong group chat nơi mọi người ở múi giờ khác. Thay vì dùng wall-clock (khác nhau), bạn đóng dấu mỗi thông điệp bằng số thứ tự tôn trọng 'tôi thấy thông điệp của bạn trước khi gửi của tôi' — thứ tự nhân quả, không phải đồng hồ.

## Ý tưởng cốt lõi

Wall clock không tin cậy trong hệ phân tán — chúng trôi, nhảy khi đồng bộ NTP và khác giữa máy. Logical clock là một số nguyên đơn giản chỉ tăng. Quy tắc Lamport: tăng khi event local, lấy `max(local, remote) + 1` khi nhận thông điệp. Điều này đảm bảo: nếu event A có nhân quả trước event B, thì `clock(A) < clock(B)`.

```text
  Process P1          Process P2
  ─────────           ─────────
  tick → 1
  tick → 2
  send(2) ──────────► receive(2)
                      max(0, 2)+1 = 3
                      tick → 4
  receive(4) ◄─────── send(4)
  max(2, 4)+1 = 5
  tick → 6

  Thứ tự nhân quả: P1:1 → P1:2 → P2:3 → P2:4 → P1:5 → P1:6
```

| Thuộc tính | Giá trị |
|----------|-------|
| Tăng | O(1) — counter++ |
| Nhận | O(1) — max + 1 |
| Đảm bảo | Nếu A → B (nhân quả), thì clock(A) < clock(B) |
| Giới hạn | Đảo lại KHÔNG đúng: clock(A) < clock(B) không hàm ý A → B |

**Thử ngay** — thực hiện event local và gửi thông điệp giữa process để xem Lamport clock:

<LogicalClockViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| etcd | [kvstore.go#L53-L72](https://github.com/etcd-io/etcd/blob/e9b62f804766edf77cfa918d600cb6fb2c56b401/server/storage/mvcc/kvstore.go#L53-L72) | Struct `store` (L53) với `currentRev int64` (L72) — bộ đếm revision đơn điệu. Tăng trong [kvstore_txn.go#L214](https://github.com/etcd-io/etcd/blob/e9b62f804766edf77cfa918d600cb6fb2c56b401/server/storage/mvcc/kvstore_txn.go#L214) (`tw.s.currentRev++`) mỗi transaction ghi. Watch và snapshot dùng revision này cho đọc nhất quán — "cho tôi mọi thứ sau revision 42." |
| LevelDB | [dbformat.h#L62-L66](https://github.com/google/leveldb/blob/7ee830d02b623e8ffe0b95d59a74db1e58da04c5/db/dbformat.h#L62-L66) | `SequenceNumber` (L62) là `uint64_t` tăng mỗi thao tác ghi. `kMaxSequenceNumber` (L66) dành 8 bit để đóng gói info kiểu cùng sequence. Dùng để sắp xếp ghi trong WAL, xác định hiển thị snapshot và giải xung đột key khi compaction. |

## Triển khai

::: code-group

```typescript [TypeScript]
class LamportClock {
  private time = 0;

  /** Tăng clock cho event local. */
  tick(): void {
    this.time++;
  }

  /** Ghi event gửi và trả timestamp. */
  send(): number {
    this.time++;
    return this.time;
  }

  /** Nhận thông điệp với timestamp remote. */
  receive(remoteTimestamp: number): void {
    this.time = Math.max(this.time, remoteTimestamp) + 1;
  }

  /** Giá trị clock hiện tại. */
  now(): number {
    return this.time;
  }
}
```

```rust [Rust]
use std::sync::atomic::{AtomicU64, Ordering};

pub struct LamportClock {
    time: AtomicU64,
}

impl LamportClock {
    pub fn new() -> Self {
        LamportClock { time: AtomicU64::new(0) }
    }

    pub fn tick(&self) -> u64 {
        self.time.fetch_add(1, Ordering::SeqCst) + 1
    }

    pub fn send(&self) -> u64 {
        self.tick()
    }

    pub fn receive(&self, remote: u64) -> u64 {
        loop {
            let current = self.time.load(Ordering::SeqCst);
            let new_time = std::cmp::max(current, remote) + 1;
            if self.time.compare_exchange(
                current, new_time, Ordering::SeqCst, Ordering::SeqCst
            ).is_ok() {
                return new_time;
            }
        }
    }

    pub fn now(&self) -> u64 {
        self.time.load(Ordering::SeqCst)
    }
}
```

```go [Go]
type LamportClock struct {
	mu   sync.Mutex
	time uint64
}

func (c *LamportClock) Tick() uint64 {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.time++
	return c.time
}

func (c *LamportClock) Send() uint64 {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.time++
	return c.time
}

func (c *LamportClock) Receive(remote uint64) uint64 {
	c.mu.Lock()
	defer c.mu.Unlock()
	if remote > c.time {
		c.time = remote
	}
	c.time++
	return c.time
}

func (c *LamportClock) Now() uint64 {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.time
}
```

```python [Python]
class LamportClock:
    def __init__(self) -> None:
        self._time = 0

    def tick(self) -> None:
        self._time += 1

    def send(self) -> int:
        self._time += 1
        return self._time

    def receive(self, remote_timestamp: int) -> None:
        self._time = max(self._time, remote_timestamp) + 1

    def now(self) -> int:
        return self._time
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai Lamport clock với tick/send/receive | `exercises/typescript/logical-clock/01-basic.test.ts` |
| Trung bình | Xây version vector cho theo dõi nhân quả đa node | `exercises/typescript/logical-clock/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/logical_clock/mod.rs` · Go `exercises/go/logical_clock/logical_clock_test.go` · Python `exercises/python/logical_clock/test_logical_clock.py`

## Khi nào nên dùng

- **Theo dõi revision database** — etcd, CockroachDB và Spanner dùng revision đơn điệu cho snapshot nhất quán và API watch
- **Vô hiệu cache** — vô hiệu dựa trên epoch: "nếu epoch cache của bạn < epoch hiện tại, dữ liệu của bạn cũ"
- **Sắp xếp event phân tán** — sắp xếp thông điệp qua node không cần đồng bộ clock (message queue, event sourcing)
- **MVCC (multi-version concurrency control)** — mỗi transaction nhận sequence number; reader thấy snapshot nhất quán tại một thời điểm
- **Concurrency lạc quan** — "cập nhật row này chỉ nếu version khớp" (compare-and-swap với timestamp logic)

## Khi nào KHÔNG nên dùng

- **Cần wall-clock** — nếu bạn cần "này xảy ra lúc 14:30" cho timestamp hướng user, logical clock cho thứ tự nhưng không phải thời gian thật. Dùng Hybrid Logical Clock (HLC) hoặc TrueTime.
- **Phát hiện event đồng thời** — Lamport clock không xác định được hai event đồng thời hay liên quan nhân quả khi `clock(A) < clock(B)`. Bạn cần vector clock cho điều đó.
- **Code tuần tự một process** — nếu mọi thứ chạy trong một thread không phân tán, bộ đếm đơn giản hoặc index mảng đủ. Bộ máy Lamport không thêm gì.

## Thêm các ứng dụng production

- [CockroachDB](https://github.com/cockroachdb/cockroach) — Hybrid Logical Clock (HLC) kết hợp wall clock + bộ đếm logic cho transaction serializable
- [Amazon DynamoDB](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) — vector clock cho phát hiện xung đột qua replica
- [Kafka](https://github.com/apache/kafka) — offset là vị trí logic đơn điệu trong log partition
- [Raft consensus](https://github.com/etcd-io/raft) — `term` là epoch logic; term cao hơn thắng bầu cử leader

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [MVCC (Multi-Version Concurrency Control)](/patterns/mvcc/) | MVCC dùng timestamp logic làm định danh phiên bản |
| [Write-Ahead Log (WAL)](/patterns/write-ahead-log/) | Entry WAL sắp xếp theo sequence number logical clock |
| [Checkpointing](/patterns/checkpointing/) | Checkpoint được lấy tại vị trí logical clock cụ thể |

## Câu hỏi thử thách

::: details Câu 1: Process A có Lamport clock 5, Process B có clock 3. Có thể xác định event nào xảy ra trước không?
**Trả lời:** Không. Lamport clock chỉ đảm bảo: nếu A có nhân quả trước B, thì `clock(A) < clock(B)`. Đảo lại KHÔNG đảm bảo.

`clock(A) = 5 > clock(B) = 3` KHÔNG nghĩa A xảy ra sau B. Chúng có thể là event đồng thời trên máy khác không giao tiếp. Để phát hiện đồng thời, bạn cần **vector clock** — một bộ đếm mỗi node, với so sánh theo thành phần.
:::

::: details Câu 2: Hybrid Logical Clock (HLC) cải tiến Lamport clock thuần thế nào?
**Trả lời:** HLC kết hợp timestamp vật lý (wall clock) với bộ đếm logic. Phần vật lý cho gần thời gian thật — "này xảy ra khoảng 14:30." Phần logic phá thế cờ và duy trì đảm bảo Lamport.

Quy tắc: `hlc = max(local_wall_clock, local_hlc, remote_hlc)`. Nếu wall clock tiến, phần logic reset. Nếu wall clock chậm (NTP chưa bắt kịp), phần logic tăng.

CockroachDB dùng HLC vì cần cả hai: thứ tự nhân quả cho consistency VÀ giới hạn thời gian thật cho deadline transaction. Lamport thuần cho thứ tự nhưng số vô nghĩa như thời gian. Wall clock thuần cho thời gian nhưng có thể đi ngược.
:::

::: details Câu 3: Cache của bạn dùng bộ đếm epoch để vô hiệu. Server restart và epoch reset về 0. Hỏng gì?
**Trả lời:** Entry cache cũ trông hợp lệ. Client có cache epoch 5 thấy server epoch 0 và có thể kết luận sai nó có dữ liệu mới hơn (hoặc tuỳ protocol, buộc re-fetch đầy đủ).

Giải pháp: (1) lưu epoch ra đĩa và khôi phục khi restart, (2) dùng kết hợp ID server + epoch để restart phân biệt được, (3) dùng epoch dựa trên timestamp chỉ tăng. etcd giải bằng revision bền vững + ID member đổi khi rejoin.
:::

::: details Câu 4: Bạn đang xây hệ event sourcing. Nên dùng Lamport clock hay sequence number làm event ID?
**Trả lời:** Sequence number tốt hơn cho event store single-writer. Lamport clock thêm phức tạp không cần khi chỉ một nguồn event — auto-incrementing integer đơn giản là logical clock hoàn toàn hợp lệ.

Lamport clock toả sáng khi nhiều writer độc lập tồn tại (hệ phân tán). Cho single-writer: dùng sequence number. Cho multi-writer với một node phối hợp: dùng sequence tập trung (như offset partition Kafka). Cho multi-writer thực sự phân tán: dùng Lamport hoặc vector clock. Match công cụ với mô hình phân tán.
:::
