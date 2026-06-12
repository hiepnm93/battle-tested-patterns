---
title: "Pattern: Dependency Graph"
description: "Mô hình dependency thành đồ thị có hướng không chu trình và sắp xếp topo để xác định thứ tự thực thi hợp lệ — phát hiện chu trình trước khi gây deadlock."
difficulty: "intermediate"
---

# Pattern: Dependency Graph

<DifficultyBadge />

## Mô tả một câu

Mô hình dependency thành đồ thị có hướng không chu trình và sắp xếp topo để xác định thứ tự thực thi hợp lệ — phát hiện chu trình trước khi gây deadlock.

<DemoBadge />

## Tương tự thực tế

Sơ đồ tiên quyết môn học trong catalog đại học. Bạn không thể học Vật lý nâng cao không qua Vật lý nhập môn trước. Bạn theo sơ đồ từ tiên quyết đến môn nâng cao, đảm bảo không bỏ qua bước cần.

## Ý tưởng cốt lõi

Dependency graph biểu diễn item là node và ràng buộc thứ tự là cạnh có hướng. `addEdge(A, B)` nghĩa "A phải đến trước B" — A là tiên quyết của B. Sắp xếp topo (thuật toán Kahn) lặp lại xoá node có in-degree 0, sinh thứ tự nơi mọi tiên quyết xuất hiện trước phụ thuộc.

```text
  addEdge(wash, dry)     wash ──► dry ──► fold
  addEdge(dry, fold)          0        1       2
  addEdge(wash, fold)         │                ▲
                              └────────────────┘

  In-degree:  wash=0   dry=1   fold=2
  Output:     wash  →  dry  →  fold
  (in-degree 0 trước, rồi phụ thuộc)

  Chu trình:  a → b → c → a  ← LỖI: không thứ tự hợp lệ
```

| Thuộc tính | Giá trị |
|----------|-------|
| Thêm node/cạnh | O(1) |
| Sắp xếp topo | O(V + E) — thăm mỗi node và cạnh một lần |
| Phát hiện chu trình | Tích hợp vào sắp xếp topo (node còn lại = chu trình) |
| Bộ nhớ | O(V + E) — danh sách kề |

**Thử ngay** — thêm node và cạnh, rồi chạy sắp xếp topo để xem thuật toán Kahn đi qua:

<DependencyGraphViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| Cargo (Rust) | [dep_cache.rs#L143-L175](https://github.com/rust-lang/cargo/blob/b50aa179d3d1099b53548bc8693dd17ddd019ab4/src/cargo/core/resolver/dep_cache.rs#L143-L175) | `RegistryQueryer` quản lý graph phân giải dependency cho package Rust. Dependency tạo DAG phân giải qua backtracking, với `build_deps` (L207) sinh tập dependency kích hoạt bởi mỗi candidate. |
| pnpm | [graph-sequencer#L22-L125](https://github.com/pnpm/pnpm/blob/46fd26afc9926b4391636a851ae32493f9b2c9ff/deps/graph-sequencer/src/index.ts#L22-L125) | `graphSequencer` — sắp xếp topo package workspace theo dependency liên gói với phát hiện chu trình. Dùng bởi command đệ quy `pnpm -r` để tôn trọng thứ tự dependency qua monorepo. |

## Triển khai

::: code-group

```typescript [TypeScript]
class DependencyGraph<T> {
  private adjacency = new Map<T, Set<T>>();

  addNode(node: T): void {
    if (!this.adjacency.has(node)) this.adjacency.set(node, new Set());
  }

  addEdge(from: T, to: T): void {
    this.addNode(from);
    this.addNode(to);
    this.adjacency.get(from)!.add(to);
  }

  topologicalSort(): T[] {
    const inDegree = new Map<T, number>();
    for (const node of this.adjacency.keys()) inDegree.set(node, 0);
    for (const [, deps] of this.adjacency) {
      for (const dep of deps) {
        inDegree.set(dep, (inDegree.get(dep) ?? 0) + 1);
      }
    }

    const queue: T[] = [];
    for (const [node, degree] of inDegree) {
      if (degree === 0) queue.push(node);
    }

    const result: T[] = [];
    while (queue.length > 0) {
      const node = queue.shift()!;
      result.push(node);
      for (const dep of this.adjacency.get(node) ?? []) {
        const newDegree = inDegree.get(dep)! - 1;
        inDegree.set(dep, newDegree);
        if (newDegree === 0) queue.push(dep);
      }
    }

    if (result.length !== this.adjacency.size) {
      throw new Error('Cycle detected');
    }
    return result;
  }
}
```

```rust [Rust]
use std::collections::HashMap;

pub struct DependencyGraph {
    adj: HashMap<String, Vec<String>>,
}

impl DependencyGraph {
    pub fn new() -> Self {
        DependencyGraph { adj: HashMap::new() }
    }

    pub fn add_node(&mut self, node: &str) {
        self.adj.entry(node.to_string()).or_default();
    }

    pub fn add_edge(&mut self, from: &str, to: &str) {
        self.add_node(from);
        self.add_node(to);
        self.adj.get_mut(from).unwrap().push(to.to_string());
    }

    pub fn topological_sort(&self) -> Result<Vec<String>, &'static str> {
        let mut in_degree: HashMap<&str, usize> = HashMap::new();
        for node in self.adj.keys() {
            in_degree.entry(node.as_str()).or_insert(0);
        }
        for deps in self.adj.values() {
            for dep in deps {
                *in_degree.entry(dep.as_str()).or_insert(0) += 1;
            }
        }

        let mut queue: Vec<&str> = in_degree.iter()
            .filter(|(_, &d)| d == 0)
            .map(|(&n, _)| n)
            .collect();
        queue.sort();

        let mut result = Vec::new();
        while let Some(node) = queue.first().copied() {
            queue.remove(0);
            result.push(node.to_string());
            if let Some(deps) = self.adj.get(node) {
                for dep in deps {
                    let d = in_degree.get_mut(dep.as_str()).unwrap();
                    *d -= 1;
                    if *d == 0 {
                        queue.push(dep.as_str());
                        queue.sort();
                    }
                }
            }
        }

        if result.len() != self.adj.len() {
            return Err("Cycle detected");
        }
        Ok(result)
    }
}
```

```go [Go]
type DependencyGraph struct {
	adj map[string][]string
}

func NewDependencyGraph() *DependencyGraph {
	return &DependencyGraph{adj: make(map[string][]string)}
}

func (g *DependencyGraph) AddNode(node string) {
	if _, ok := g.adj[node]; !ok {
		g.adj[node] = nil
	}
}

func (g *DependencyGraph) AddEdge(from, to string) {
	g.AddNode(from)
	g.AddNode(to)
	g.adj[from] = append(g.adj[from], to)
}

func (g *DependencyGraph) TopologicalSort() ([]string, error) {
	inDegree := make(map[string]int)
	for node := range g.adj {
		inDegree[node] = 0
	}
	for _, deps := range g.adj {
		for _, dep := range deps {
			inDegree[dep]++
		}
	}

	var queue []string
	for node, deg := range inDegree {
		if deg == 0 {
			queue = append(queue, node)
		}
	}
	sort.Strings(queue)

	var result []string
	for len(queue) > 0 {
		node := queue[0]
		queue = queue[1:]
		result = append(result, node)
		for _, dep := range g.adj[node] {
			inDegree[dep]--
			if inDegree[dep] == 0 {
				queue = append(queue, dep)
			}
		}
	}

	if len(result) != len(g.adj) {
		return nil, fmt.Errorf("cycle detected")
	}
	return result, nil
}
```

```python [Python]
from collections import deque

class DependencyGraph:
    def __init__(self):
        self.adj: dict[str, list[str]] = {}

    def add_node(self, node: str) -> None:
        if node not in self.adj:
            self.adj[node] = []

    def add_edge(self, from_node: str, to_node: str) -> None:
        self.add_node(from_node)
        self.add_node(to_node)
        self.adj[from_node].append(to_node)

    def topological_sort(self) -> list[str]:
        in_degree: dict[str, int] = {n: 0 for n in self.adj}
        for deps in self.adj.values():
            for dep in deps:
                in_degree[dep] = in_degree.get(dep, 0) + 1

        queue = deque(n for n, d in in_degree.items() if d == 0)
        result: list[str] = []

        while queue:
            node = queue.popleft()
            result.append(node)
            for dep in self.adj.get(node, []):
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)

        if len(result) != len(self.adj):
            raise ValueError("Cycle detected")
        return result
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai sắp xếp topo với phát hiện chu trình | `exercises/typescript/dependency-graph/01-basic.test.ts` |
| Trung bình | Planner thực thi song song — tính các đợt thực thi | `exercises/typescript/dependency-graph/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/dependency_graph/mod.rs` · Go `exercises/go/dependency_graph/dependency_graph_test.go` · Python `exercises/python/dependency_graph/test_dependency_graph.py`

## Khi nào nên dùng

- **Hệ build** — biên dịch dependency trước phụ thuộc (Make, Bazel, Cargo)
- **Trình quản lý package** — thứ tự cài/build cho package workspace (pnpm, npm, yarn)
- **Lập lịch task** — điều phối job với tiên quyết (Airflow, pipeline CI/CD)
- **Bundler module** — xác định tách chunk và thứ tự nạp (webpack, Rollup)
- **Migration database** — áp thay đổi schema theo thứ tự dependency

## Khi nào KHÔNG nên dùng

- **Dependency vòng tồn tại theo thiết kế** — dùng mô hình khác (ví dụ hướng sự kiện, đánh giá lười)
- **Không cần thứ tự** — nếu task độc lập, list đơn giản đủ
- **Dependency động** — nếu cạnh đổi lúc runtime, cách tiếp cận tăng dần tốt hơn
- **Đồ thị rất lớn** — cân nhắc thuật toán song song (Kahn vốn tuần tự không có sửa đổi)

## Thêm các ứng dụng production

- [Make (GNU)](https://github.com/mirror/make) — DAG tiên quyết xác định thứ tự rebuild target
- [Bazel](https://github.com/bazelbuild/bazel) — action graph với pha thực thi topo
- [webpack](https://github.com/webpack/webpack) — `ModuleGraph` cho tách chunk và tree shaking
- [Terraform](https://github.com/hashicorp/terraform) — graph dependency resource cho apply song song

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Visitor](/patterns/visitor/) | Duyệt cây trên dependency graph dispatch tới handler đặc thù kiểu |
| [Iterator](/patterns/iterator/) | Lặp topo sinh chuỗi lười các node theo thứ tự dependency |
| [Dirty Flag](/patterns/dirty-flag/) | Lan dirty đi theo cạnh dependency để đánh dấu node downstream cho tính lại |
| [Registry](/patterns/registry/) | Registry theo dõi metadata component; dependency graph theo dõi quan hệ chúng |

## Câu hỏi thử thách

::: details Câu 1: Cho dependency graph nơi A->C, B->C, và A và B không có dependency, bao nhiêu task có thể chạy song song? Sắp xếp topo tiết lộ điều này thế nào?
**Trả lời:** A và B có thể chạy song song (cả hai in-degree 0). C phải chờ cả hai. Song song tối đa là 2.

Sắp xếp topo dùng Kahn tự nhiên lộ song song: mọi node với in-degree 0 ở bước nào cũng có thể thực thi đồng thời. Ở ví dụ này, "đợt" đầu là {A, B} (cả hai in-degree 0), và đợt hai là {C} (in-degree giảm về 0 sau khi cả A và B xong). Hệ build như Bazel và Make khai thác bằng cách xử lý mỗi đợt song song.
:::

::: details Câu 2: Package D phụ thuộc cả B và C. B phụ thuộc A. C cũng phụ thuộc A. Đây là "diamond dependency." Sắp xếp topo có xử lý đúng không?
**Trả lời:** Có. Sắp xếp topo xử lý diamond đúng vì nó theo dõi in-degree, không phải đường đi. A chạy trước, rồi B và C (song song), rồi D.

Diamond không phải chu trình — chỉ là hai đường hội tụ tại cùng node. Thuật toán Kahn xử lý A (in-degree 0), giảm in-degree của B và C về 0, xử lý cả hai, rồi giảm in-degree D về 0 và xử lý. Vấn đề tiềm năng không phải ở thứ tự mà ở xung đột phiên bản: nếu B cần A v1 và C cần A v2, bạn có vấn đề tương thích mà cấu trúc graph riêng không giải.
:::

::: details Câu 3: Bạn đổi file `utils.ts` trong dự án lớn. Hệ build tăng dần chỉ biên dịch lại file phụ thuộc `utils.ts`. Dependency graph cho phép điều này thế nào?
**Trả lời:** Hệ build đi qua dependency graph tới từ `utils.ts`, thu thập mọi phụ thuộc bắc cầu. Chỉ những file đó (cộng `utils.ts` chính) cần biên dịch lại.

Đây là lợi thế then chốt duy trì dependency graph thay vì list file phẳng. Không có graph, bạn phải biên dịch lại tất cả hoặc duy trì list dependency thủ công. Với graph, bạn tính subgraph bị ảnh hưởng trong O(V+E). Công cụ như `ModuleGraph` của webpack và action graph của Bazel làm chính xác điều này — chúng theo dõi output nào phụ thuộc input nào và vô hiệu chỉ subtree bị ảnh hưởng.
:::

::: details Câu 4: Dev thêm dependency từ module A tới module B, nhưng B đã bắc cầu phụ thuộc A (B -> C -> A). Hệ build nên làm gì?
**Trả lời:** Từ chối thay đổi. Thêm A -> B tạo chu trình (A -> B -> C -> A), nghĩa không có thứ tự build hợp lệ.

Thuật toán Kahn phát hiện điều này: sau khi xử lý mọi node in-degree 0, một số node còn in-degree khác 0 — các node đó tạo chu trình. Hệ build nên báo cáo đường chu trình chính xác để dev có thể thiết kế lại dependency (ví dụ tách code dùng chung vào module mới, dùng đảo ngược dependency, hoặc dùng import lười/động để phá chu trình lúc compile).
:::
