---
title: "Pattern: Work Stealing"
description: "Thread rảnh lấy trộm task từ queue của thread bận — cân bằng tải động không cần phối hợp tập trung."
difficulty: "advanced"
---

# Pattern: Work Stealing

<DifficultyBadge />

## Mô tả một câu

Thread rảnh lấy trộm task từ queue của thread bận — cân bằng tải động không cần phối hợp tập trung.

<DemoBadge />

## Tương tự thực tế

Đội thu ngân ở siêu thị. Khi một thu ngân xong hàng của họ, họ đi tới thu ngân bận nhất và lấy khách từ cuối hàng đó. Công việc tự nhiên chảy từ lane quá tải sang lane rảnh.

## Ý tưởng cốt lõi

Mỗi worker sở hữu deque cục bộ (double-ended queue). Worker push/pop task từ đỉnh deque của riêng (LIFO cho cache locality). Khi deque worker rỗng, nó lấy trộm từ đáy deque worker khác (FIFO cho công bằng). Điều này đạt cân bằng tải tự động không có nút thắt scheduler tập trung.

```text
  Worker 0 (bận)          Worker 1 (rảnh)        Worker 2 (bận)
  ┌──────────────┐        ┌──────────────┐       ┌──────────────┐
  │ Task D ← pop │        │   (rỗng)     │       │ Task G ← pop │
  │ Task C       │        │              │       │ Task F       │
  │ Task B       │◄───────│  STEAL ────► │       │              │
  │ Task A       │  steal │              │       │              │
  └──────────────┘  from  └──────────────┘       └──────────────┘
        ↑ đáy                                          ↑ đáy
```

| Thuộc tính | Giá trị |
|----------|-------|
| Push/pop riêng | O(1) — không cần đồng bộ |
| Steal | O(1) — CAS trên đáy deque nạn nhân |
| Cân bằng tải | Tự động, phi tập trung |
| Cache locality | Cao — LIFO cho việc riêng, FIFO cho việc lấy trộm |

**Thử ngay** — thêm task vào một worker và bắt đầu xử lý để xem worker rảnh lấy trộm task:

<WorkStealingViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| Go runtime | [proc.go#L3836-L3903](https://github.com/golang/go/blob/f5cdf4745455415c7a43cfc7d925214d4511489b/src/runtime/proc.go#L3836-L3903) | `stealWork` — vòng steal của scheduler goroutine. Lặp 4× qua mọi P theo thứ tự ngẫu nhiên, gọi `runqsteal` (L7774-L7791) để CAS-grab nửa số goroutine có thể chạy từ queue chạy local của P nạn nhân. `runqgrab` cấp thấp (L7706-L7769) dùng CAS atomic trên `runqhead`. |
| Tokio (Rust) | [worker.rs#L1136-L1175](https://github.com/tokio-rs/tokio/blob/bde89678532a8091d958268c0d36eac9362317d8/tokio/src/runtime/scheduler/multi_thread/worker.rs#L1136-L1175) | `Core::steal_work` — lặp qua worker remote từ index ngẫu nhiên, gọi `steal_into` trên queue steal của mỗi worker. Chỉ cố steal nếu ít hơn nửa worker đang search. Fallback về queue inject toàn cục. |

## Triển khai

::: code-group

```typescript [TypeScript]
class WorkStealingScheduler {
  private queues: number[][];

  constructor(workerCount: number) {
    this.queues = Array.from({ length: workerCount }, () => []);
  }

  submit(task: number, workerIdx: number): void {
    this.queues[workerIdx]!.push(task);
  }

  run(process: (task: number) => number): number[] {
    const results: number[] = [];
    let anyWork = true;
    while (anyWork) {
      anyWork = false;
      for (let w = 0; w < this.queues.length; w++) {
        if (this.queues[w]!.length > 0) {
          anyWork = true;
          const task = this.queues[w]!.pop()!;
          results.push(process(task));
        } else {
          for (let other = 0; other < this.queues.length; other++) {
            if (other !== w && this.queues[other]!.length > 1) {
              anyWork = true;
              const stolen = this.queues[other]!.shift()!;
              results.push(process(stolen));
              break;
            }
          }
        }
      }
    }
    return results;
  }
}
```

```rust [Rust]
use std::collections::VecDeque;

pub struct WorkStealingScheduler {
    queues: Vec<VecDeque<i32>>,
}

impl WorkStealingScheduler {
    pub fn new(worker_count: usize) -> Self {
        WorkStealingScheduler {
            queues: (0..worker_count).map(|_| VecDeque::new()).collect(),
        }
    }

    pub fn submit(&mut self, task: i32, worker_idx: usize) {
        self.queues[worker_idx].push_back(task);
    }

    pub fn run(&mut self, process: fn(i32) -> i32) -> Vec<i32> {
        let mut results = Vec::new();
        loop {
            let mut any_work = false;
            for w in 0..self.queues.len() {
                if !self.queues[w].is_empty() {
                    any_work = true;
                    let task = self.queues[w].pop_back().unwrap();
                    results.push(process(task));
                } else {
                    let len = self.queues.len();
                    for other in 0..len {
                        if other != w && self.queues[other].len() > 1 {
                            any_work = true;
                            let stolen = self.queues[other].pop_front().unwrap();
                            results.push(process(stolen));
                            break;
                        }
                    }
                }
            }
            if !any_work { break; }
        }
        results
    }
}
```

```go [Go]
type WorkStealingScheduler struct {
	queues [][]int
}

func NewScheduler(workerCount int) *WorkStealingScheduler {
	queues := make([][]int, workerCount)
	for i := range queues {
		queues[i] = []int{}
	}
	return &WorkStealingScheduler{queues: queues}
}

func (s *WorkStealingScheduler) Submit(task, workerIdx int) {
	s.queues[workerIdx] = append(s.queues[workerIdx], task)
}

func (s *WorkStealingScheduler) Run(process func(int) int) []int {
	var results []int
	for {
		anyWork := false
		for w := 0; w < len(s.queues); w++ {
			if len(s.queues[w]) > 0 {
				anyWork = true
				last := len(s.queues[w]) - 1
				task := s.queues[w][last]
				s.queues[w] = s.queues[w][:last]
				results = append(results, process(task))
			} else {
				for other := 0; other < len(s.queues); other++ {
					if other != w && len(s.queues[other]) > 1 {
						anyWork = true
						stolen := s.queues[other][0]
						s.queues[other] = s.queues[other][1:]
						results = append(results, process(stolen))
						break
					}
				}
			}
		}
		if !anyWork {
			break
		}
	}
	return results
}
```

```python [Python]
from collections import deque

class WorkStealingScheduler:
    def __init__(self, worker_count: int):
        self.queues: list[deque[int]] = [deque() for _ in range(worker_count)]

    def submit(self, task: int, worker_idx: int) -> None:
        self.queues[worker_idx].append(task)

    def run(self, process) -> list[int]:
        results: list[int] = []
        while True:
            any_work = False
            for w in range(len(self.queues)):
                if self.queues[w]:
                    any_work = True
                    task = self.queues[w].pop()
                    results.append(process(task))
                else:
                    for other in range(len(self.queues)):
                        if other != w and len(self.queues[other]) > 1:
                            any_work = True
                            stolen = self.queues[other].popleft()
                            results.append(process(stolen))
                            break
            if not any_work:
                break
        return results
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai scheduler work-stealing với deque local | `exercises/typescript/work-stealing/01-basic.test.ts` |
| Trung bình | Work stealing có ưu tiên — task ưu tiên cao trước | `exercises/typescript/work-stealing/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/work_stealing/mod.rs` · Go `exercises/go/work_stealing/work_stealing_test.go` · Python `exercises/python/work_stealing/test_work_stealing.py`

## Khi nào nên dùng

- **Runtime song song** — scheduler goroutine (Go), scheduler task (Tokio, Java ForkJoinPool)
- **Chia-để-trị** — phân rã task đệ quy nơi subtask thay đổi kích thước
- **Tải không đều** — khi thời lượng task khó đoán
- **Lập lịch nhận biết NUMA** — chỉ steal từ xa khi việc local cạn

## Khi nào KHÔNG nên dùng

- **Đơn luồng** — không có worker khác để steal
- **Task đồng nhất** — phân vùng tĩnh đơn giản hơn và hiệu quả tương đương
- **Task rất ngắn** — overhead steal lấn át thời gian thực thi task
- **Thứ tự nghiêm ngặt** — work stealing phá vỡ thứ tự FIFO theo thiết kế

## Thêm các ứng dụng production

- [Java ForkJoinPool](https://github.com/openjdk/jdk/blob/4b3ec455c85314d051800a8f46dd8f5c93881e3a/src/java.base/share/classes/java/util/concurrent/ForkJoinPool.java) — method `scan` với work stealing ngẫu nhiên
- [Rayon (Rust)](https://github.com/rayon-rs/rayon) — thư viện song song dữ liệu với thread pool work-stealing
- [Intel TBB](https://github.com/oneapi-src/oneTBB) — `task_arena` với scheduler work-stealing
- [Cilk](https://github.com/OpenCilk/opencilk-project) — tiên phong work stealing cho song song fork-join

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Cooperative Scheduling](/patterns/cooperative-scheduling/) | Work stealing phân tán task qua thread; cooperative scheduling yield trong một thread |
| [Object Pool](/patterns/object-pool/) | Thread worker dùng object pool mỗi thread để tránh tranh chấp |
| [Free List](/patterns/free-list/) | Free list mỗi thread bổ sung work stealing bằng cách cung cấp cấp phát lock-free |

## Câu hỏi thử thách

::: details Câu 1: Worker pop từ deque riêng dùng LIFO (đỉnh), nhưng steal từ cái khác dùng FIFO (đáy). Sao không dùng FIFO cho cả hai?
**Trả lời:** LIFO trên deque riêng cho cache locality — task push gần nhất có khả năng vẫn trong cache CPU. Steal FIFO lấy task cũ nhất (lớn nhất) từ nạn nhân, cho thief nhiều việc trước khi cần steal lại.

Trong tải chia-để-trị, đáy deque giữ task spawn sớm nhất (mức to nhất). Steal một task lớn tốt hơn steal nhiều task nhỏ vì phân bổ overhead steal và cho thief một khối việc nó có thể chia nhỏ cục bộ. LIFO cho pop local cũng tự nhiên triển khai thực thi theo chiều sâu, dùng ít space stack hơn.
:::

::: details Câu 2: Runtime Go steal nửa run queue của nạn nhân thay vì chỉ một task. Sao "steal nửa" tốt hơn "steal một"?
**Trả lời:** Steal một task nghĩa thief có thể xong nhanh và lập tức cần steal lại, gây tranh chấp lặp lại trên deque nạn nhân. Steal nửa phân bổ chi phí đồng bộ.

Mỗi thao tác steal cần CAS atomic trên deque nạn nhân, đắt. Nếu steal chỉ một task, worker với queue rỗng có thể steal hàng chục lần mỗi millisecond. Steal nửa queue trong một thao tác nghĩa thief có đủ việc local để giữ bận, giảm tổng số lần thử steal và tranh chấp. `runqgrab` của runtime Go làm chính xác điều này với một thao tác atomic.
:::

::: details Câu 3: Vấn đề ABA là gì trong bối cảnh deque work-stealing lock-free, và sao quan trọng?
**Trả lời:** Vấn đề ABA xảy ra khi CAS thành công vì giá trị khớp, nhưng state bên dưới đã đổi giữa lúc đọc và CAS — thread khác đã sửa và khôi phục giá trị gốc.

Trong deque lock-free, thief đọc index đáy là giá trị A, bị preempt, owner pop và push (đáy đi A -> B -> A), và CAS của thief trên index đáy thành công dù nội dung deque khác. Điều này có thể làm task được thực thi hai lần hoặc bị bỏ qua. Sửa là dùng con trỏ có tag hoặc bộ đếm generation để CAS phát hiện thay đổi trung gian. Đó là lý do Tokio và Go dùng bộ đếm epoch/version song song với index deque.
:::

::: details Câu 4: Bạn có 8 worker và 8 task chạy lâu giống nhau, một mỗi worker. Work stealing có giúp ở đây không?
**Trả lời:** Không. Nếu mỗi worker có chính xác một task thời lượng bằng, không worker nào xong sớm, nên không steal nào xảy ra. Work stealing thêm 0 lợi ích và overhead nhỏ từ logic check idle.

Work stealing toả sáng khi tải không đều — vài task xong nhanh và worker có thể giúp cái khác. Với task cân bằng hoàn hảo, đồng nhất, phân vùng tĩnh (gán một task mỗi worker) đơn giản hơn và hiệu quả tương đương. Overhead work stealing (quản lý deque, chọn nạn nhân ngẫu nhiên, thao tác CAS) lãng phí khi không có gì để steal.
:::
