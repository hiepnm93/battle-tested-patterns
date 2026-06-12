---
title: "Pattern: Write-Ahead Log (WAL)"
description: "Log mọi mutation vào lưu trữ bền vững trước khi áp dụng — replay log để khôi phục sau crash không mất dữ liệu."
difficulty: "intermediate"
---

# Pattern: Write-Ahead Log (WAL)

<DifficultyBadge />

## Mô tả một câu

Log mọi mutation vào lưu trữ bền vững trước khi áp dụng — replay log để khôi phục sau crash không mất dữ liệu.

<DemoBadge />

## Tương tự thực tế

Logbook thuyền trưởng. Trước khi đổi hướng, thuyền trưởng ghi thay đổi dự kiến vào log. Nếu tàu mất điện giữa lúc rẽ, thuỷ thủ đoàn có thể đọc log và hoàn thành hoặc huỷ bỏ thao tác. Log là nguồn sự thật.

## Ý tưởng cốt lõi

WAL ghi mọi thay đổi state thành append tuần tự trước khi state thực được sửa. Nếu hệ thống crash giữa thao tác, log sống sót và có thể replay để dựng lại state chính xác. Insight then chốt: **ghi tuần tự nhanh** (thân thiện đĩa), và **replay idempotent** (an toàn để làm lại).

```text
  Client                  WAL (trên đĩa)             State (trong bộ nhớ)
  ──────                  ────────────              ─────────────────
  SET x=1  ──────►  [1] SET x=1    ──────►  { x: 1 }
  SET y=2  ──────►  [2] SET y=2    ──────►  { x: 1, y: 2 }
  DEL x    ──────►  [3] DEL x      ──────►  { y: 2 }
                         ▲
              *** CRASH TẠI ĐÂY ***

  Khôi phục: replay entry log 1, 2, 3 → { y: 2 } ✓
```

| Thuộc tính | Giá trị |
|----------|-------|
| Mẫu ghi | Append tuần tự (tối ưu cho đĩa) |
| Bền vững | Sống sót crash — log trên lưu trữ bền vững |
| Khôi phục | Replay từ đầu hoặc từ checkpoint cuối |
| Overhead | Một ghi thêm mỗi mutation (log + state) |

**Thử ngay** — ghi thao tác vào WAL, flush tới bảng, rồi mô phỏng crash và khôi phục:

<WriteAheadLogViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| etcd | [wal.go#L72-L95](https://github.com/etcd-io/etcd/blob/e9b62f804766edf77cfa918d600cb6fb2c56b401/server/storage/wal/wal.go#L72-L95) | Struct `WAL` (L72) giữ dir, encoder, mutex và file pipeline. Method `Save` (L958-L1000) lưu hard state Raft và entry, sync ra đĩa, và xoay segment khi vượt `SegmentSizeBytes`. WAL là nguồn sự thật cho đồng thuận phân tán etcd. |
| PostgreSQL | [xlog.c#L783-L1128](https://github.com/postgres/postgres/blob/e18b0cb7344cb4bd28468f6c0aeeb9b9241d30aa/src/backend/access/transam/xlog.c#L783-L1128) | `XLogInsertRecord` — entry point chèn WAL cốt lõi. Đặt chỗ, copy dữ liệu record vào buffer WAL, kích hoạt flush nếu cần. `XLogWrite` (L2324-L2622) ghi page WAL từ buffer chia sẻ ra đĩa. Cho phép khôi phục crash, replication và PITR. |

## Triển khai

::: code-group

```typescript [TypeScript]
interface LogEntry {
  id: number;
  operation: string;
  data: Record<string, unknown>;
  applied: boolean;
}

class WriteAheadLog {
  private entries: LogEntry[] = [];
  private nextId = 1;

  append(operation: string, data: Record<string, unknown>): number {
    const id = this.nextId++;
    this.entries.push({ id, operation, data, applied: false });
    return id;
  }

  apply(applyFn: (entry: LogEntry) => void): number {
    let count = 0;
    for (const entry of this.entries) {
      if (!entry.applied) {
        applyFn(entry);
        entry.applied = true;
        count++;
      }
    }
    return count;
  }

  recover(applyFn: (entry: LogEntry) => void): number {
    let count = 0;
    for (const entry of this.entries) {
      applyFn(entry);
      entry.applied = true;
      count++;
    }
    return count;
  }
}
```

```rust [Rust]
use std::collections::HashMap;

pub struct LogEntry {
    pub id: usize,
    pub operation: String,
    pub data: HashMap<String, String>,
    pub applied: bool,
}

pub struct WriteAheadLog {
    entries: Vec<LogEntry>,
    next_id: usize,
}

impl WriteAheadLog {
    pub fn new() -> Self {
        WriteAheadLog { entries: Vec::new(), next_id: 1 }
    }

    pub fn append(&mut self, operation: &str, data: HashMap<String, String>) -> usize {
        let id = self.next_id;
        self.next_id += 1;
        self.entries.push(LogEntry {
            id, operation: operation.to_string(), data, applied: false,
        });
        id
    }

    pub fn apply(&mut self, apply_fn: &dyn Fn(&LogEntry)) -> usize {
        let mut count = 0;
        for entry in &mut self.entries {
            if !entry.applied {
                apply_fn(entry);
                entry.applied = true;
                count += 1;
            }
        }
        count
    }

    pub fn recover(&mut self, apply_fn: &dyn Fn(&LogEntry)) -> usize {
        let mut count = 0;
        for entry in &mut self.entries {
            apply_fn(entry);
            entry.applied = true;
            count += 1;
        }
        count
    }
}
```

```go [Go]
type LogEntry struct {
	ID        int
	Operation string
	Data      map[string]any
	Applied   bool
}

type WAL struct {
	entries []LogEntry
	nextID  int
}

func NewWAL() *WAL {
	return &WAL{nextID: 1}
}

func (w *WAL) Append(op string, data map[string]any) int {
	id := w.nextID
	w.nextID++
	w.entries = append(w.entries, LogEntry{ID: id, Operation: op, Data: data})
	return id
}

func (w *WAL) Apply(fn func(LogEntry)) int {
	count := 0
	for i := range w.entries {
		if !w.entries[i].Applied {
			fn(w.entries[i])
			w.entries[i].Applied = true
			count++
		}
	}
	return count
}

func (w *WAL) Recover(fn func(LogEntry)) int {
	count := 0
	for i := range w.entries {
		fn(w.entries[i])
		w.entries[i].Applied = true
		count++
	}
	return count
}
```

```python [Python]
from dataclasses import dataclass, field
from typing import Any

@dataclass
class LogEntry:
    id: int
    operation: str
    data: dict[str, Any]
    applied: bool = False

class WriteAheadLog:
    def __init__(self):
        self._entries: list[LogEntry] = []
        self._next_id = 1

    def append(self, operation: str, data: dict[str, Any]) -> int:
        entry = LogEntry(id=self._next_id, operation=operation, data=data)
        self._next_id += 1
        self._entries.append(entry)
        return entry.id

    def apply(self, apply_fn) -> int:
        count = 0
        for entry in self._entries:
            if not entry.applied:
                apply_fn(entry)
                entry.applied = True
                count += 1
        return count

    def recover(self, apply_fn) -> int:
        count = 0
        for entry in self._entries:
            apply_fn(entry)
            entry.applied = True
            count += 1
        return count
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai WAL trong bộ nhớ | `exercises/typescript/write-ahead-log/01-basic.test.ts` |
| Trung bình | Khôi phục checkpoint — chỉ replay sau checkpoint cuối | `exercises/typescript/write-ahead-log/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/write_ahead_log/mod.rs` · Go `exercises/go/write_ahead_log/write_ahead_log_test.go` · Python `exercises/python/write_ahead_log/test_write_ahead_log.py`

## Khi nào nên dùng

- **Database** — khôi phục crash cho transaction (PostgreSQL, SQLite, MySQL InnoDB)
- **Đồng thuận phân tán** — replication log Raft/Paxos (etcd, ZooKeeper)
- **Message queue** — lưu trữ message bền vững (Kafka, Pulsar)
- **Filesystem** — journaling cho toàn vẹn metadata (ext4, NTFS)
- **Event sourcing** — log event LÀ write-ahead log

## Khi nào KHÔNG nên dùng

- **Dữ liệu tạm** — entry cache hoặc dữ liệu session không cần khôi phục crash
- **Thao tác idempotent** — nếu có thể an toàn dẫn xuất lại state, WAL thêm overhead không cần
- **Update cùng key tần suất cao** — WAL tăng nhanh; cân nhắc LSM tree hoặc snapshot định kỳ
- **Tải nặng đọc** — WAL tối ưu ghi; đọc vẫn qua state trong bộ nhớ

## Thêm các ứng dụng production

- [SQLite](https://www.sqlite.org/wal.html) — mode WAL cho reader đồng thời với một writer
- [RocksDB](https://github.com/facebook/rocksdb) — WAL cho lưu trữ nền LSM-tree
- [CockroachDB](https://github.com/cockroachdb/cockroach) — Raft WAL cho SQL phân tán
- [Apache Kafka](https://github.com/apache/kafka) — commit log như trừu tượng lưu trữ cốt lõi

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Checkpointing](/patterns/checkpointing/) | Checkpoint cắt WAL — khôi phục từ checkpoint + replay log còn lại |
| [LSM Tree (Log-Structured Merge Tree)](/patterns/lsm-tree/) | LSM tree dùng WAL để đảm bảo ghi memtable sống sót crash trước khi flush |
| [Merkle Tree](/patterns/merkle-tree/) | Merkle tree xác minh state mà WAL giúp dựng lại sau khôi phục |
| [Logical Clock](/patterns/logical-clock/) | Entry WAL được sắp xếp bởi logical clock cho đảm bảo thứ tự |
| [MVCC](/patterns/mvcc/) | WAL ghi mọi mutation mà phiên bản MVCC dựa trên, cho phép khôi phục crash |

## Câu hỏi thử thách

::: details Câu 1: Triển khai WAL của bạn gọi write() nhưng không fsync(). OS crash (không chỉ process). Dữ liệu có an toàn không?
**Trả lời:** Không. Không có fsync, dữ liệu có thể trong page cache OS nhưng không trên đĩa. OS crash hoặc mất điện mất ghi chưa flush.

`write()` chuyển dữ liệu vào page cache kernel, là bộ nhớ tạm. Chỉ `fsync()` (hoặc `fdatasync()`) buộc nó vào lưu trữ bền vững. Đó là lý do database như PostgreSQL có `synchronous_commit` và etcd gọi `sync()` sau mỗi ghi WAL. Đánh đổi: fsync mỗi ghi chậm (đặc biệt trên đĩa quay), nên nhiều hệ thống batch ghi và fsync định kỳ, chấp nhận cửa sổ nhỏ tiềm năng mất dữ liệu.
:::

::: details Câu 2: WAL của bạn đã chạy 6 tháng và chứa 200 triệu entry log. Khôi phục sau crash mất 45 phút. Sửa thế nào?
**Trả lời:** Lấy snapshot định kỳ (checkpoint) state hiện tại và cắt WAL tới điểm đó. Khôi phục chỉ replay entry sau snapshot cuối.

Đây là compaction log hoặc checkpointing. Thay vì replay cả lịch sử, bạn serialize state hiện tại thành file snapshot, ghi vị trí WAL, và xoá entry log cũ. Khôi phục nạp snapshot và replay chỉ entry sau đó. etcd làm vậy với cơ chế snapshot; PostgreSQL dùng checkpoint. Không có nó, hệ thống nền WAL chậm khôi phục dần.
:::

::: details Câu 3: Đồng đội đề nghị dùng snapshot toàn-state định kỳ thay vì WAL. "Cứ snapshot mỗi 5 giây." WAL cho bạn gì mà snapshot riêng không cho?
**Trả lời:** WAL cho khôi phục thời điểm với không mất dữ liệu. Khoảng snapshot 5 giây nghĩa bạn có thể mất tới 5 giây ghi khi crash.

Snapshot bắt state ở khoảng rời rạc, nên mọi ghi giữa snapshot cuối và crash bị mất. WAL ghi mọi mutation riêng, nên khôi phục replay tới entry ghi thành công cuối — thường mất tối đa một thao tác. Hầu hết hệ thống production dùng cả hai: WAL cho bền vững giữa snapshot, và snapshot để giới hạn size WAL và tăng tốc khôi phục.
:::

::: details Câu 4: Hai thao tác trong WAL là: (1) SET balance=100, (2) SET balance=200. Khi khôi phục, hệ thống replay cả hai. Thứ tự replay có quan trọng không, và sao?
**Trả lời:** Có, thứ tự quan trọng. Replay (2) trước (1) sẽ set balance về 100, sai. Entry WAL phải replay đúng thứ tự được ghi.

Tính đúng WAL phụ thuộc vào replay tuần tự tái tạo chính xác cùng chuyển trạng thái như thực thi gốc. Đó là lý do WAL là log có thứ tự, append-only — không phải tập thao tác không thứ tự. Nếu thao tác giao hoán và idempotent (như "tăng thêm 5"), thứ tự có thể không quan trọng, nhưng hầu hết mutation thực (SET, DELETE) phụ thuộc thứ tự.
:::
