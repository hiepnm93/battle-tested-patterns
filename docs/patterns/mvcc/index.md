---
title: "Pattern: MVCC (Multi-Version Concurrency Control)"
description: "Giữ nhiều phiên bản có timestamp của mỗi giá trị để reader không bao giờ chặn writer — mỗi transaction thấy snapshot nhất quán không cần lock."
difficulty: "advanced"
---

# Pattern: MVCC (Multi-Version Concurrency Control)

<DifficultyBadge />

## Mô tả một câu

Giữ nhiều phiên bản có timestamp của mỗi giá trị để reader không bao giờ chặn writer — mỗi transaction thấy snapshot nhất quán không cần lock.

<DemoBadge />

## Tương tự thực tế

Thư viện giữ ấn bản cũ của sách cùng với ấn bản mới. Người đọc đã mượn ấn bản 3 có thể đọc xong dù ấn bản 4 đã ra. Mỗi người đọc thấy snapshot nhất quán — không ai thấy update viết dở.

## Ý tưởng cốt lõi

MVCC lưu mỗi ghi như phiên bản mới gắn timestamp hoặc transaction ID. Reader thấy phiên bản mới nhất visible với snapshot của họ, bỏ qua ghi đồng thời. Điều này loại bỏ tranh chấp đọc-ghi: reader không bao giờ chặn writer, writer không bao giờ chặn reader.

```text
  Key "balance"
  ┌──────────┬──────────┬──────────┬──────────┐
  │ t=100    │ t=200    │ t=300    │ t=400    │
  │ val=500  │ val=450  │ val=600  │ val=580  │
  └──────────┴──────────┴──────────┴──────────┘

  Transaction tại t=250:  thấy val=450  (phiên bản mới nhất ≤ 250)
  Transaction tại t=350:  thấy val=600  (phiên bản mới nhất ≤ 350)
  Cả hai đọc không chặn writer tại t=400.
```

| Thuộc tính | Giá trị |
|----------|-------|
| Xung đột đọc-ghi | **Không** — reader thấy snapshot của họ, writer append phiên bản mới |
| Xung đột ghi-ghi | Phát hiện lúc commit (first-writer-wins hoặc abort) |
| Overhead bộ nhớ | Nhiều phiên bản mỗi key (GC qua compaction) |
| Mức cô lập | Snapshot isolation (mạnh hơn read-committed, yếu hơn serializable) |

**Thử ngay** — bắt đầu transaction, đọc và ghi key, và quan sát cô lập snapshot:

<MVCCViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| PostgreSQL | [heapam_visibility.c#L917-L1096](https://github.com/postgres/postgres/blob/e18b0cb7344cb4bd28468f6c0aeeb9b9241d30aa/src/backend/access/heap/heapam_visibility.c#L917-L1096) | `HeapTupleSatisfiesMVCC` — check hiển thị cốt lõi. Cho tuple heap và snapshot MVCC, xác định tuple visible với transaction hiện tại. Dùng `XidInMVCCSnapshot` để check hiển thị transaction không tranh chấp trên `ProcArrayLock`. |
| etcd | [kvstore.go#L53-L135](https://github.com/etcd-io/etcd/blob/e9b62f804766edf77cfa918d600cb6fb2c56b401/server/storage/mvcc/kvstore.go#L53-L135) | Struct `store` (L53-L82) theo dõi `currentRev` và `compactMainRev` với B-tree `kvindex` cho tra cứu đa phiên bản. `NewStore` (L87-L135) khởi tạo store MVCC và dựng lại index trong bộ nhớ từ revision đã lưu. Chạy xương sống cấu hình Kubernetes. |

## Triển khai

::: code-group

```typescript [TypeScript]
interface Version<T> {
  timestamp: number;
  value: T;
  deleted: boolean;
}

class MVCCStore<T> {
  private store = new Map<string, Version<T>[]>();

  put(key: string, value: T, timestamp: number): void {
    if (!this.store.has(key)) this.store.set(key, []);
    this.store.get(key)!.push({ timestamp, value, deleted: false });
  }

  get(key: string, timestamp: number): T | undefined {
    const versions = this.store.get(key);
    if (!versions) return undefined;
    let best: Version<T> | undefined;
    for (const v of versions) {
      if (v.timestamp <= timestamp && (!best || v.timestamp > best.timestamp)) {
        best = v;
      }
    }
    return best && !best.deleted ? best.value : undefined;
  }

  delete(key: string, timestamp: number): void {
    if (!this.store.has(key)) this.store.set(key, []);
    this.store.get(key)!.push({ timestamp, value: undefined as T, deleted: true });
  }
}
```

```rust [Rust]
pub struct Version {
    pub timestamp: u64,
    pub value: Option<String>,
}

pub struct MVCCStore {
    data: std::collections::HashMap<String, Vec<Version>>,
}

impl MVCCStore {
    pub fn new() -> Self {
        MVCCStore { data: std::collections::HashMap::new() }
    }

    pub fn put(&mut self, key: &str, value: &str, ts: u64) {
        self.data.entry(key.to_string()).or_default()
            .push(Version { timestamp: ts, value: Some(value.to_string()) });
    }

    pub fn get(&self, key: &str, ts: u64) -> Option<&str> {
        let versions = self.data.get(key)?;
        let mut best: Option<&Version> = None;
        for v in versions {
            if v.timestamp <= ts && best.map_or(true, |b| v.timestamp > b.timestamp) {
                best = Some(v);
            }
        }
        best.and_then(|v| v.value.as_deref())
    }

    pub fn delete(&mut self, key: &str, ts: u64) {
        self.data.entry(key.to_string()).or_default()
            .push(Version { timestamp: ts, value: None });
    }
}
```

```go [Go]
type Version struct {
	Timestamp int
	Value     string
	Deleted   bool
}

type MVCCStore struct {
	data map[string][]Version
}

func NewMVCCStore() *MVCCStore {
	return &MVCCStore{data: make(map[string][]Version)}
}

func (s *MVCCStore) Put(key, value string, ts int) {
	s.data[key] = append(s.data[key], Version{Timestamp: ts, Value: value})
}

func (s *MVCCStore) Get(key string, ts int) (string, bool) {
	versions := s.data[key]
	var best *Version
	for i := range versions {
		v := &versions[i]
		if v.Timestamp <= ts && (best == nil || v.Timestamp > best.Timestamp) {
			best = v
		}
	}
	if best == nil || best.Deleted {
		return "", false
	}
	return best.Value, true
}

func (s *MVCCStore) Delete(key string, ts int) {
	s.data[key] = append(s.data[key], Version{Timestamp: ts, Deleted: true})
}
```

```python [Python]
from dataclasses import dataclass
from typing import Any

@dataclass
class Version:
    timestamp: int
    value: Any
    deleted: bool = False

class MVCCStore:
    def __init__(self):
        self._data: dict[str, list[Version]] = {}

    def put(self, key: str, value: Any, timestamp: int) -> None:
        self._data.setdefault(key, []).append(Version(timestamp, value))

    def get(self, key: str, timestamp: int) -> Any:
        versions = self._data.get(key, [])
        best = None
        for v in versions:
            if v.timestamp <= timestamp and (best is None or v.timestamp > best.timestamp):
                best = v
        if best is None or best.deleted:
            return None
        return best.value

    def delete(self, key: str, timestamp: int) -> None:
        self._data.setdefault(key, []).append(Version(timestamp, None, deleted=True))
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai kho key-value đa phiên bản | `exercises/typescript/mvcc/01-basic.test.ts` |
| Trung bình | Transaction snapshot với đọc nhất quán | `exercises/typescript/mvcc/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/mvcc/mod.rs` · Go `exercises/go/mvcc/mvcc_test.go` · Python `exercises/python/mvcc/test_mvcc.py`

## Khi nào nên dùng

- **Database** — snapshot isolation cho transaction đồng thời (PostgreSQL, MySQL InnoDB)
- **KV store phân tán** — đọc nhất quán không cần lock phân tán (etcd, CockroachDB, TiKV)
- **Truy vấn time-travel** — đọc dữ liệu tại timestamp quá khứ
- **Concurrency lạc quan** — phát hiện xung đột lúc commit thay vì lock từ đầu

## Khi nào KHÔNG nên dùng

- **Hệ single-writer** — overhead MVCC không cần nếu chỉ một writer
- **Eo hẹp bộ nhớ** — nhiều phiên bản mỗi key tiêu thụ storage đáng kể
- **Nặng ghi, không đọc** — overhead quản lý phiên bản không lợi cho reader
- **Cần serializability nghiêm ngặt** — MVCC cung cấp snapshot isolation; serializability đầy đủ cần cơ chế thêm (SSI)

## Thêm các ứng dụng production

- [CockroachDB](https://github.com/cockroachdb/cockroach/blob/5f5932a2bf50713ff76a0f859a41fd7985dec307/pkg/storage/mvcc.go#L1923-L1962) — `MVCCPut` / `MVCCGet` cho SQL phân tán
- [MySQL InnoDB](https://github.com/mysql/mysql-server) — undo log cho versioning row MVCC
- [TiKV](https://github.com/tikv/tikv) — transaction MVCC phân tán nền Percolator
- [FoundationDB](https://github.com/apple/foundationdb) — lớp lưu trữ đa phiên bản

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Copy-on-Write (CoW)](/patterns/copy-on-write/) | MVCC tạo phiên bản mới khi ghi, tương tự ngữ nghĩa copy-on-write |
| [Logical Clock](/patterns/logical-clock/) | Logical clock cung cấp timestamp phiên bản mà MVCC phụ thuộc |
| [Tombstone](/patterns/tombstone/) | MVCC đánh dấu phiên bản đã xoá bằng tombstone cho GC sau |
| [Write-Ahead Log (WAL)](/patterns/write-ahead-log/) | WAL đảm bảo thay đổi phiên bản MVCC sống sót crash |

## Câu hỏi thử thách

::: details Câu 1: MVCC store của bạn giữ mọi phiên bản của mọi key mãi. Sau một năm hoạt động, dùng storage 50x kích thước dataset live thực. Database production như PostgreSQL xử lý thế nào?
**Trả lời:** Họ chạy garbage collection (gọi "vacuum" trong PostgreSQL) để xoá phiên bản không còn visible với transaction active nào.

Process `VACUUM` của PostgreSQL xác định tuple "chết" — phiên bản cũ hơn snapshot transaction active cũ nhất. Vì không transaction nào có thể thấy phiên bản này, chúng an toàn để thu hồi. etcd dùng `compaction` để bỏ revision cũ hơn ngưỡng. Thách thức là xác định "low-water mark": snapshot cũ nhất vẫn dùng. Nếu transaction chạy lâu giữ snapshot cũ, nó chặn GC cho mọi phiên bản mới hơn snapshot đó — nguồn phổ biến của bloat PostgreSQL.
:::

::: details Câu 2: Hai transaction đều đọc key "balance" (value=100) ở cùng snapshot timestamp, rồi cả hai cố ghi "balance=90" (trừ 10). Dưới MVCC snapshot isolation, cả hai đọc thành công không chặn. Chuyện gì lúc commit?
**Trả lời:** Một transaction commit thành công; cái khác phát hiện xung đột ghi-ghi và abort. Balance kết thúc ở 90, không phải 80.

Đây là dị thường "lost update" dưới snapshot isolation. Cả hai transaction đọc cùng snapshot (balance=100) và tính độc lập balance=90. MVCC phát hiện xung đột lúc commit dùng quy tắc "first-writer-wins": cái đầu commit ghi phiên bản t=200 với giá trị=90. Cái thứ hai cố commit nhưng thấy "balance" đã sửa sau snapshot của nó — phải abort và retry. Khi retry, đọc giá trị mới (90) và ghi 80. Đó là lý do MVCC cung cấp snapshot isolation, không phải serializable: nó chặn lost update nhưng cần xử lý cấp ứng dụng cho xung đột ghi.
:::

::: details Câu 3: Team bạn dùng MVCC với snapshot isolation cho hệ ngân hàng. Audit compliance hỏi: "Hai chuyển tiền đồng thời giữa cùng tài khoản có thể sinh tổng không nhất quán không?" Team bạn nói snapshot isolation chặn điều này. Có đúng không?
**Trả lời:** Không. Snapshot isolation chặn lost update nhưng dễ bị dị thường write skew, nơi hai transaction đọc dữ liệu chồng và làm ghi không xung đột mà cùng vi phạm ràng buộc.

Ví dụ: account A=50 và B=50 với ràng buộc "A+B >= 0." Transaction 1 đọc cả hai, thấy total=100, ghi A=-10. Transaction 2 đọc cả hai (cùng snapshot, A=50, B=50), ghi B=-60. Cả hai pass check ràng buộc độc lập, cả hai commit (ghi key khác, nên không xung đột ghi-ghi), và kết quả A=-10, B=-60, total=-70 — vi phạm ràng buộc. Serializability đầy đủ (SSI của PostgreSQL, mode serializable CockroachDB) cần để chặn write skew.
:::

::: details Câu 4: etcd dùng MVCC để chạy kho cấu hình Kubernetes. Sao kho key-value phân tán hưởng lợi từ giữ phiên bản cũ, thay vì chỉ lưu giá trị mới nhất?
**Trả lời:** Phiên bản cũ cho phép ngữ nghĩa watch/subscribe — client có thể hỏi "cái gì đổi từ revision X?" không cần polling, và client bị ngắt kết nối có thể catch up từ revision thấy cuối.

Controller Kubernetes (như replication controller) dùng watch etcd để phản ứng thay đổi state. Nếu etcd chỉ lưu giá trị mới nhất, controller ngắt 5 giây sẽ lỡ thay đổi trung gian và cần resync đầy đủ. Với MVCC, controller kết nối lại và nói "cho tôi mọi thay đổi từ revision 12345," nhận luồng chính xác cái gì đổi. Đây cũng thiết yếu cho đảm bảo consistency etcd: đọc linearizable có thể phục vụ từ revision cụ thể, và truy vấn time-travel cho debug ("state cluster 10 phút trước là gì?").
:::
