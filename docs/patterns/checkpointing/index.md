---
title: "Pattern: Checkpointing"
description: "Định kỳ snapshot state nhất quán để khôi phục chỉ replay từ checkpoint — không phải từ đầu."
difficulty: "intermediate"
---

# Pattern: Checkpointing

<DifficultyBadge />

## Mô tả một câu

Định kỳ snapshot state nhất quán để khôi phục chỉ replay từ checkpoint — không phải từ đầu.

<DemoBadge />

## Tương tự thực tế

Save game. Bạn chơi một lúc, nhấn 'save', và nếu chết, khởi động lại từ điểm save cuối thay vì đầu. Save càng thường, mất tiến độ càng ít — nhưng mỗi save mất thời gian.

## Ý tưởng cốt lõi

Checkpointing bắt snapshot nhất quán của state hệ thống hiện tại ở điểm đã biết. Khi crash, khôi phục nạp checkpoint cuối và chỉ replay các thao tác log sau đó. Không có checkpoint, hệ thống nền WAL phải replay toàn lịch sử mỗi lần khởi động — tăng không giới hạn. Checkpoint giới hạn thời gian khôi phục ở khoảng từ checkpoint cuối.

```text
  Thời gian ────────────────────────────────────────────►

  WAL:  [op1] [op2] [op3] [op4] [op5] [op6] [op7] [op8]
                          ▲                    ▲
                     Checkpoint 1         Checkpoint 2
                     (snapshot state)     (snapshot state)

  Không checkpoint:
    Khôi phục replay: op1, op2, op3, op4, op5, op6, op7, op8

  Có checkpoint:
    Khôi phục nạp Checkpoint 2, replay: chỉ op7, op8
```

| Thuộc tính | Giá trị |
|----------|-------|
| Thời gian khôi phục | Tỉ lệ với số op từ checkpoint cuối |
| Chi phí checkpoint | O(kích thước state) để serialize state hiện tại |
| Cắt WAL | An toàn bỏ entry log trước checkpoint |
| Consistency | Checkpoint phải bắt snapshot nhất quán |

**Thử ngay** — tăng state, lấy checkpoint, crash, và khôi phục từ checkpoint:

<CheckpointingViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| PostgreSQL | [checkpointer.c#L218-L360](https://github.com/postgres/postgres/blob/e18b0cb7344cb4bd28468f6c0aeeb9b9241d30aa/src/backend/postmaster/checkpointer.c#L218-L360) | `CheckpointerMain` — process nền checkpoint. Chạy trong vòng lặp chờ yêu cầu checkpoint hoặc `checkpoint_timeout` (mặc định 5 phút). Gọi `CreateCheckPoint` flush mọi buffer dirty ra đĩa, ghi record checkpoint WAL, và cập nhật `pg_control` với vị trí checkpoint. Khi khôi phục crash, PostgreSQL đọc `pg_control` để tìm checkpoint cuối và replay WAL chỉ từ điểm đó. |
| Redis | [rdb.c#L1414-L1529](https://github.com/redis/redis/blob/df63a65d4d4ee33ae67e9f101885074febe0bccb/src/rdb.c#L1414-L1529) | `rdbSaveRio` serialize cả dataset Redis vào file RDB — snapshot tại thời điểm. Redis fork process con (`rdbSaveBackground`) để ghi snapshot không chặn main thread. File RDB là checkpoint đầy đủ: khi restart, Redis nạp nó khôi phục state tức thì. Kết hợp với AOF (append-only file), Redis có thể replay chỉ entry AOF ghi sau snapshot RDB cuối. |

## Triển khai

::: code-group

```typescript [TypeScript]
interface LogEntry {
  id: number;
  operation: string;
  data: Record<string, unknown>;
}

class CheckpointableStore {
  private state: Map<string, unknown> = new Map();
  private wal: LogEntry[] = [];
  private nextId = 1;
  private checkpoint: { state: Map<string, unknown>; walPosition: number } | null = null;

  /** Áp dụng thao tác, log vào WAL trước. */
  apply(operation: string, key: string, value: unknown): void {
    const entry: LogEntry = {
      id: this.nextId++,
      operation,
      data: { key, value },
    };
    this.wal.push(entry);
    this.executeOp(entry);
  }

  get(key: string): unknown {
    return this.state.get(key);
  }

  /** Lấy checkpoint: snapshot state hiện tại và ghi vị trí WAL. */
  takeCheckpoint(): void {
    this.checkpoint = {
      state: new Map(this.state),
      walPosition: this.wal.length,
    };
  }

  /** Mô phỏng crash: xoá state trong bộ nhớ nhưng giữ WAL và checkpoint. */
  simulateCrash(): void {
    this.state = new Map();
  }

  /** Khôi phục từ crash dùng checkpoint + replay WAL. */
  recover(): number {
    if (this.checkpoint) {
      this.state = new Map(this.checkpoint.state);
      let replayed = 0;
      for (let i = this.checkpoint.walPosition; i < this.wal.length; i++) {
        this.executeOp(this.wal[i]!);
        replayed++;
      }
      return replayed;
    }
    // Không checkpoint: replay cả WAL
    this.state = new Map();
    for (const entry of this.wal) {
      this.executeOp(entry);
    }
    return this.wal.length;
  }

  private executeOp(entry: LogEntry): void {
    const { key, value } = entry.data as { key: string; value: unknown };
    if (entry.operation === 'SET') {
      this.state.set(key, value);
    } else if (entry.operation === 'DELETE') {
      this.state.delete(key);
    }
  }

  get walLength(): number { return this.wal.length; }
  get stateSize(): number { return this.state.size; }
}
```

```rust [Rust]
use std::collections::HashMap;

pub struct LogEntry {
    pub id: usize,
    pub operation: String,
    pub key: String,
    pub value: Option<String>,
}

struct Snapshot {
    state: HashMap<String, String>,
    wal_position: usize,
}

pub struct CheckpointableStore {
    state: HashMap<String, String>,
    wal: Vec<LogEntry>,
    next_id: usize,
    checkpoint: Option<Snapshot>,
}

impl CheckpointableStore {
    pub fn new() -> Self {
        CheckpointableStore {
            state: HashMap::new(),
            wal: Vec::new(),
            next_id: 1,
            checkpoint: None,
        }
    }

    pub fn apply(&mut self, operation: &str, key: &str, value: Option<&str>) {
        let entry = LogEntry {
            id: self.next_id,
            operation: operation.to_string(),
            key: key.to_string(),
            value: value.map(|v| v.to_string()),
        };
        self.next_id += 1;
        self.execute_op(&entry);
        self.wal.push(entry);
    }

    pub fn get(&self, key: &str) -> Option<&str> {
        self.state.get(key).map(|s| s.as_str())
    }

    pub fn take_checkpoint(&mut self) {
        self.checkpoint = Some(Snapshot {
            state: self.state.clone(),
            wal_position: self.wal.len(),
        });
    }

    pub fn simulate_crash(&mut self) {
        self.state.clear();
    }

    pub fn recover(&mut self) -> usize {
        if let Some(ref snap) = self.checkpoint {
            self.state = snap.state.clone();
            let start = snap.wal_position;
            let mut replayed = 0;
            for i in start..self.wal.len() {
                self.execute_op_by_index(i);
                replayed += 1;
            }
            return replayed;
        }
        self.state.clear();
        for i in 0..self.wal.len() {
            self.execute_op_by_index(i);
        }
        self.wal.len()
    }

    fn execute_op(&mut self, entry: &LogEntry) {
        if entry.operation == "SET" {
            if let Some(ref v) = entry.value {
                self.state.insert(entry.key.clone(), v.clone());
            }
        } else if entry.operation == "DELETE" {
            self.state.remove(&entry.key);
        }
    }

    fn execute_op_by_index(&mut self, idx: usize) {
        let op = self.wal[idx].operation.clone();
        let key = self.wal[idx].key.clone();
        let value = self.wal[idx].value.clone();
        if op == "SET" {
            if let Some(v) = value {
                self.state.insert(key, v);
            }
        } else if op == "DELETE" {
            self.state.remove(&key);
        }
    }

    pub fn wal_length(&self) -> usize { self.wal.len() }
    pub fn state_size(&self) -> usize { self.state.len() }
}
```

```go [Go]
package checkpoint

type LogEntry struct {
	ID        int
	Operation string
	Key       string
	Value     any
}

type stateSnapshot struct {
	state       map[string]any
	walPosition int
}

type CheckpointableStore struct {
	state      map[string]any
	wal        []LogEntry
	nextID     int
	checkpoint *stateSnapshot
}

func NewStore() *CheckpointableStore {
	return &CheckpointableStore{
		state:  make(map[string]any),
		nextID: 1,
	}
}

func (s *CheckpointableStore) Apply(operation, key string, value any) {
	entry := LogEntry{ID: s.nextID, Operation: operation, Key: key, Value: value}
	s.nextID++
	s.wal = append(s.wal, entry)
	s.executeOp(entry)
}

func (s *CheckpointableStore) Get(key string) (any, bool) {
	v, ok := s.state[key]
	return v, ok
}

func (s *CheckpointableStore) TakeCheckpoint() {
	snap := make(map[string]any, len(s.state))
	for k, v := range s.state {
		snap[k] = v
	}
	s.checkpoint = &stateSnapshot{state: snap, walPosition: len(s.wal)}
}

func (s *CheckpointableStore) SimulateCrash() {
	s.state = make(map[string]any)
}

func (s *CheckpointableStore) Recover() int {
	if s.checkpoint != nil {
		s.state = make(map[string]any, len(s.checkpoint.state))
		for k, v := range s.checkpoint.state {
			s.state[k] = v
		}
		replayed := 0
		for i := s.checkpoint.walPosition; i < len(s.wal); i++ {
			s.executeOp(s.wal[i])
			replayed++
		}
		return replayed
	}
	s.state = make(map[string]any)
	for _, entry := range s.wal {
		s.executeOp(entry)
	}
	return len(s.wal)
}

func (s *CheckpointableStore) executeOp(entry LogEntry) {
	if entry.Operation == "SET" {
		s.state[entry.Key] = entry.Value
	} else if entry.Operation == "DELETE" {
		delete(s.state, entry.Key)
	}
}

func (s *CheckpointableStore) WALLength() int   { return len(s.wal) }
func (s *CheckpointableStore) StateSize() int    { return len(s.state) }
```

```python [Python]
from dataclasses import dataclass, field
from typing import Any

@dataclass
class LogEntry:
    id: int
    operation: str
    key: str
    value: Any = None

class CheckpointableStore:
    def __init__(self):
        self._state: dict[str, Any] = {}
        self._wal: list[LogEntry] = []
        self._next_id = 1
        self._checkpoint: dict | None = None  # {state, wal_position}

    def apply(self, operation: str, key: str, value: Any = None) -> None:
        entry = LogEntry(id=self._next_id, operation=operation, key=key, value=value)
        self._next_id += 1
        self._wal.append(entry)
        self._execute_op(entry)

    def get(self, key: str) -> Any:
        return self._state.get(key)

    def take_checkpoint(self) -> None:
        self._checkpoint = {
            "state": dict(self._state),
            "wal_position": len(self._wal),
        }

    def simulate_crash(self) -> None:
        self._state = {}

    def recover(self) -> int:
        if self._checkpoint is not None:
            self._state = dict(self._checkpoint["state"])
            replayed = 0
            for i in range(self._checkpoint["wal_position"], len(self._wal)):
                self._execute_op(self._wal[i])
                replayed += 1
            return replayed
        self._state = {}
        for entry in self._wal:
            self._execute_op(entry)
        return len(self._wal)

    def _execute_op(self, entry: LogEntry) -> None:
        if entry.operation == "SET":
            self._state[entry.key] = entry.value
        elif entry.operation == "DELETE":
            self._state.pop(entry.key, None)

    @property
    def wal_length(self) -> int:
        return len(self._wal)

    @property
    def state_size(self) -> int:
        return len(self._state)
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | WAL với checkpoint và khôi phục | `exercises/typescript/checkpointing/01-basic.test.ts` |
| Trung bình | Checkpoint tăng dần (chỉ page dirty) | `exercises/typescript/checkpointing/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/checkpointing/mod.rs` · Go `exercises/go/checkpointing/checkpointing_test.go` · Python `exercises/python/checkpointing/test_checkpointing.py`

## Khi nào nên dùng

- **Khôi phục crash database** — giới hạn thời gian replay WAL (PostgreSQL, MySQL)
- **Cache trong bộ nhớ** — lưu state để sống sót restart (Redis RDB)
- **Xử lý stream** — lưu vị trí xử lý cho đảm bảo exactly-once (Flink, Kafka)
- **Tính toán chạy lâu** — lưu tiến độ để tiếp tục sau lỗi (huấn luyện ML)
- **Save game** — snapshot state game ở điểm an toàn

## Khi nào KHÔNG nên dùng

- **Service không có state** — không state để checkpoint
- **State rất nhỏ** — nếu replay WAL mất < 1 giây, checkpoint thêm phức tạp ít lợi
- **State đổi nhanh** — nếu cả state đổi giữa các checkpoint, snapshot đắt như replay WAL
- **State phân tán** — phối hợp checkpoint nhất quán qua node cần protocol snapshot phân tán (Chandy-Lamport)

## Thêm các ứng dụng production

- [Apache Flink](https://github.com/apache/flink) — snapshot phân tán cho xử lý stream exactly-once
- [etcd](https://github.com/etcd-io/etcd) — snapshot định kỳ để compact log Raft
- [SQLite WAL mode](https://www.sqlite.org/wal.html) — checkpoint WAL chuyển page về file database
- [PyTorch](https://github.com/pytorch/pytorch) — checkpoint model để tiếp tục training sau gián đoạn

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Write-Ahead Log (WAL)](/patterns/write-ahead-log/) | Checkpoint cắt WAL — khôi phục chỉ replay từ checkpoint mới nhất |
| [Copy-on-Write (CoW)](/patterns/copy-on-write/) | Copy-on-write cho phép snapshot nhất quán không dừng ghi |
| [Logical Clock](/patterns/logical-clock/) | Checkpoint liên kết với vị trí logical clock cho consistency |
| [Merkle Tree](/patterns/merkle-tree/) | Merkle tree xác minh toàn vẹn checkpoint bằng cách phát hiện subtree nào đổi |

## Câu hỏi thử thách

::: details Câu 1: Database PostgreSQL của bạn cấu hình checkpoint_timeout = 30 phút. Server crash. Thời gian khôi phục tệ nhất là gì, và bạn giảm thế nào?
**Trả lời:** Tệ nhất: replay tới 30 phút entry WAL. Giảm bằng cách hạ checkpoint_timeout (ví dụ 5 phút) hoặc checkpoint_completion_target.

Đánh đổi rõ: checkpoint thường hơn nghĩa khôi phục nhanh hơn nhưng overhead I/O cao hơn khi hoạt động bình thường. Mỗi checkpoint flush mọi page dirty ra đĩa, có thể gây burst ghi. `checkpoint_completion_target` của PostgreSQL (mặc định 0,9) trải I/O qua 90% khoảng checkpoint để tránh đỉnh. Trong hệ throughput cao, bạn có thể checkpoint mỗi 1-5 phút; cho hệ traffic thấp, 30 phút hoặc hơn ok.
:::

::: details Câu 2: Redis dùng fork() để tạo process con cho snapshot RDB. Database 10GB. Redis có cần 20GB RAM khi snapshot không?
**Trả lời:** Không, nhờ copy-on-write (COW). Child fork chia sẻ page bộ nhớ của parent. Chỉ page parent sửa sau fork mới được nhân đôi. Thực tế, overhead bộ nhớ khi snapshot thường 10-30% dataset, không phải 100%.

Kernel OS dùng COW cho page process fork. Child đọc state đóng băng trong khi parent tiếp tục phục vụ ghi. Chỉ page parent sửa được copy (bởi cơ chế COW kernel). Nếu khối lượng ghi thấp khi snapshot, overhead bộ nhớ tối thiểu. Tuy nhiên, dưới tải ghi nặng, nhân đôi page COW có thể đạt 100% tệ nhất. Đó là lý do Redis khuyến nghị giám sát `rss` khi save nền.
:::

::: details Câu 3: Bạn đang triển khai checkpoint cho hệ xử lý stream. Mỗi checkpoint mất 5 giây ghi, nhưng hệ thống xử lý 100K event/giây. Chuyện gì với 500K event đến khi tạo checkpoint?
**Trả lời:** Hệ thống phải tiếp tục xử lý event khi tạo checkpoint. Checkpoint bắt snapshot nhất quán của state tại thời điểm bắt đầu, không phải khi xong. Event đến được xử lý bình thường và log vào WAL.

Đây là vấn đề "snapshot nhất quán". Giải pháp: (1) dùng snapshot copy-on-write (như Redis fork) — checkpoint bắt state lúc fork trong khi ghi mới đi vào page COW; (2) dùng checkpoint mờ với "redo log" — bắt đầu snapshot, theo dõi page nào đổi khi snapshot, và bao gồm thay đổi đó trong metadata checkpoint; (3) dùng barrier — tạm dừng xử lý ngắn để lấy cut nhất quán, rồi tiếp. Apache Flink dùng snapshot barrier bất đồng bộ lấy cảm hứng từ thuật toán Chandy-Lamport.
:::

::: details Câu 4: Hệ thống của bạn lấy checkpoint mỗi giờ, nhưng file checkpoint 50GB. Tốc độ ghi đĩa 200MB/s, nên ghi mất ~4 phút. Trong 4 phút đó, có thể an toàn cắt WAL không?
**Trả lời:** Không. Bạn chỉ có thể cắt entry WAL trước checkpoint SAU KHI checkpoint được ghi đầy đủ và xác nhận bền vững (đã fsync). Nếu hệ thống crash khi ghi checkpoint, bạn cần WAL để khôi phục.

Đây là lỗi phổ biến: cắt WAL trước khi checkpoint xong. Nếu ghi checkpoint fail giữa chừng (đĩa đầy, crash, mất điện), bạn mất cả checkpoint chưa xong VÀ entry WAL cần để khôi phục. Trình tự an toàn: (1) ghi checkpoint vào file tạm, (2) fsync file tạm, (3) đổi tên nguyên tử thành file checkpoint, (4) RỒI cắt WAL. PostgreSQL theo chính xác protocol này, và cơ chế snapshot etcd cũng vậy.
:::
