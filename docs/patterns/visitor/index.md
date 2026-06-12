---
title: "Pattern: Visitor / Tree Walker"
description: "Tách duyệt cây khỏi thao tác bằng cách dispatch tới callback đặc thù kiểu — cho phép thêm thao tác mới không sửa cây."
difficulty: "advanced"
---

# Pattern: Visitor / Tree Walker

<DifficultyBadge />

## Mô tả một câu

Tách duyệt cây khỏi thao tác bằng cách dispatch tới callback đặc thù kiểu — cho phép thêm thao tác mới không sửa cây.

<DemoBadge />

## Tương tự thực tế

Thanh tra xây dựng thăm các loại phòng khác nhau. Thanh tra có checklist cụ thể cho mỗi loại phòng — kiểm tra bếp khác kiểm tra phòng tắm. Các phòng không cần biết tự kiểm tra; chỉ cần mở cửa và để thanh tra làm việc đúng theo loại phòng.

## Ý tưởng cốt lõi

Pattern visitor tách "đi qua cây thế nào" khỏi "làm gì ở mỗi node." Cây định nghĩa method `accept(visitor)` dispatch tới callback đặc thù kiểu của visitor (ví dụ `visitAdd`, `visitMultiply`). Để thêm thao tác mới (đánh giá, in, tối ưu), bạn tạo visitor mới — không class node cây nào cần đổi.

```text
  AST:         +               Eval Visitor:
              / \                visitNumber(n) → n
             *   4              visitAdd(l, r)  → visit(l) + visit(r)
            / \                 visitMul(l, r)  → visit(l) * visit(r)
           2   3

  visit(tree, evalVisitor):
    visitAdd(
      visitMul(visitNumber(2), visitNumber(3)),   → 6
      visitNumber(4)                               → 4
    ) → 10

  Print Visitor (thao tác mới, không đổi cây):
    visitAdd(l, r) → "(" + visit(l) + " + " + visit(r) + ")"
    → "((2 * 3) + 4)"
```

| Thuộc tính | Giá trị |
|----------|-------|
| Thêm thao tác | Dễ — viết visitor mới |
| Thêm kiểu node | Khó — phải update mọi visitor (expression problem) |
| Duyệt | Kiểm soát bởi visitor hoặc bởi method accept() |
| Họ pattern | Hành vi — liên quan đến Strategy và Iterator |

**Thử ngay** — chọn loại visitor và duyệt AST, xem mỗi node được visit:

<VisitorViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| LLVM | [InstVisitor.h#L45-L107](https://github.com/llvm/llvm-project/blob/1dc53bacd24fb555dfd2ec030a5ee33f5db3fadf/llvm/include/llvm/IR/InstVisitor.h#L45-L107) | `InstVisitor<SubClass, RetTy>` (L45) là visitor CRTP qua mọi kiểu lệnh LLVM IR. Nó dispatch qua `visit(Instruction &I)` switch theo opcode để gọi `visitAdd`, `visitBr`, `visitCall` v.v. Dùng cho đếm lệnh, gấp hằng và pass tối ưu. Hành vi mặc định uỷ thác visitor class cha. |
| Vue.js | [transforms/vIf.ts#L35-L60](https://github.com/vuejs/core/blob/48ad452dd61926a59e358da3c74c5ef750ae21c4/packages/compiler-core/src/transforms/vIf.ts#L35-L60) | `transformIf` là visitor `NodeTransform` đi qua AST template. `traverseNode` của compiler (trong transform.ts) dispatch mỗi node AST tới visitor transform đã đăng ký. Mỗi transform (v-if, v-for, v-bind) là visitor viết lại node mà không sửa code cấu trúc AST. |

## Triển khai

::: code-group

```typescript [TypeScript]
type Expr =
  | { type: 'number'; value: number }
  | { type: 'add'; left: Expr; right: Expr }
  | { type: 'multiply'; left: Expr; right: Expr };

interface ExprVisitor<T> {
  visitNumber: (value: number) => T;
  visitAdd: (left: Expr, right: Expr) => T;
  visitMultiply: (left: Expr, right: Expr) => T;
}

function visit<T>(expr: Expr, v: ExprVisitor<T>): T {
  switch (expr.type) {
    case 'number': return v.visitNumber(expr.value);
    case 'add': return v.visitAdd(expr.left, expr.right);
    case 'multiply': return v.visitMultiply(expr.left, expr.right);
  }
}

// Eval visitor
const evalVisitor: ExprVisitor<number> = {
  visitNumber: (n) => n,
  visitAdd: (l, r) => visit(l, evalVisitor) + visit(r, evalVisitor),
  visitMultiply: (l, r) => visit(l, evalVisitor) * visit(r, evalVisitor),
};
```

```rust [Rust]
enum Expr {
    Number(f64),
    Add(Box<Expr>, Box<Expr>),
    Multiply(Box<Expr>, Box<Expr>),
}

trait ExprVisitor {
    type Output;
    fn visit_number(&mut self, value: f64) -> Self::Output;
    fn visit_add(&mut self, left: &Expr, right: &Expr) -> Self::Output;
    fn visit_multiply(&mut self, left: &Expr, right: &Expr) -> Self::Output;
}

fn visit<V: ExprVisitor>(expr: &Expr, v: &mut V) -> V::Output {
    match expr {
        Expr::Number(n) => v.visit_number(*n),
        Expr::Add(l, r) => v.visit_add(l, r),
        Expr::Multiply(l, r) => v.visit_multiply(l, r),
    }
}

struct Evaluator;
impl ExprVisitor for Evaluator {
    type Output = f64;
    fn visit_number(&mut self, value: f64) -> f64 { value }
    fn visit_add(&mut self, left: &Expr, right: &Expr) -> f64 {
        visit(left, self) + visit(right, self)
    }
    fn visit_multiply(&mut self, left: &Expr, right: &Expr) -> f64 {
        visit(left, self) * visit(right, self)
    }
}
```

```go [Go]
type Expr interface{ exprNode() }

type NumberExpr struct{ Value float64 }
type AddExpr struct{ Left, Right Expr }
type MulExpr struct{ Left, Right Expr }

func (NumberExpr) exprNode() {}
func (AddExpr) exprNode()    {}
func (MulExpr) exprNode()    {}

func Eval(e Expr) float64 {
	switch n := e.(type) {
	case NumberExpr:
		return n.Value
	case AddExpr:
		return Eval(n.Left) + Eval(n.Right)
	case MulExpr:
		return Eval(n.Left) * Eval(n.Right)
	default:
		panic("unknown node")
	}
}
```

```python [Python]
from dataclasses import dataclass
from typing import Protocol, TypeVar

T = TypeVar("T")

@dataclass
class Number:
    value: float

@dataclass
class Add:
    left: "Expr"
    right: "Expr"

@dataclass
class Multiply:
    left: "Expr"
    right: "Expr"

Expr = Number | Add | Multiply

def visit(expr: Expr, visitor: dict) -> float:
    if isinstance(expr, Number):
        return visitor["number"](expr.value)
    elif isinstance(expr, Add):
        return visitor["add"](expr.left, expr.right)
    elif isinstance(expr, Multiply):
        return visitor["multiply"](expr.left, expr.right)
    raise TypeError(f"Unknown expr: {expr}")

eval_visitor = {
    "number": lambda v: v,
    "add": lambda l, r: visit(l, eval_visitor) + visit(r, eval_visitor),
    "multiply": lambda l, r: visit(l, eval_visitor) * visit(r, eval_visitor),
}
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Visitor AST cho biểu thức toán (eval + print) | `exercises/typescript/visitor/01-basic.test.ts` |
| Trung bình | Visitor transform viết lại cây (gấp hằng) | `exercises/typescript/visitor/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/visitor/mod.rs` · Go `exercises/go/visitor/visitor_test.go` · Python `exercises/python/visitor/test_visitor.py`

## Khi nào nên dùng

- **Compiler và interpreter** — đánh giá, type checking, pass tối ưu qua AST
- **Linter và formatter** — đi qua AST code để phát hiện pattern hoặc format lại
- **Serialize** — duyệt đồ thị object để phát JSON, XML hoặc binary
- **Framework UI** — đi qua cây component để render, diff hoặc check accessibility
- **Query planner** — đi qua và tối ưu kế hoạch truy vấn SQL

## Khi nào KHÔNG nên dùng

- **Kiểu node thay đổi thường xuyên** — nếu bạn thêm kiểu node thường xuyên, mọi visitor phải update (expression problem)
- **Logic đơn giản một pass** — nếu chỉ cần một thao tác, hàm đệ quy đơn giản rõ hơn visitor đầy đủ
- **Dữ liệu phẳng** — visitor toả sáng trên cấu trúc cây/đồ thị; cho list phẳng, vòng lặp đơn giản đủ

## Thêm các ứng dụng production

- [Babel](https://github.com/babel/babel) — transform AST JavaScript dùng kiến trúc plugin nền visitor
- [ESLint](https://github.com/eslint/eslint) — rule lint là visitor đi qua AST và báo cáo vi phạm
- [Roslyn](https://github.com/dotnet/roslyn) — visitor syntax tree của compiler C# cho phân tích và sinh code
- [rustc](https://github.com/rust-lang/rust) — trait visitor HIR và MIR cho borrow checking, tối ưu và codegen

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Iterator](/patterns/iterator/) | Cả hai duyệt cấu trúc — visitor dispatch callback, iterator yield phần tử |
| [Vtable](/patterns/vtable/) | Bảng dispatch visitor về mặt khái niệm là vtable index theo kiểu node |
| [Dependency Graph](/patterns/dependency-graph/) | Visitor đi qua dependency graph để xử lý node theo thứ tự đúng |
| [Tagged Union](/patterns/tagged-union/) | Dispatch visitor match tag kiểu của tagged union |
| [State Machine](/patterns/state-machine/) | Visitor có thể duyệt node state machine; state machine có thể thúc dispatch visitor |

## Câu hỏi thử thách

::: details Câu 1: Bạn đang xây compiler với 20 kiểu node AST và 15 pass tối ưu. Nên dùng visitor hay switch statement?
**Trả lời:** Visitor. Với 15 pass (thao tác) và 20 kiểu node, bạn sẽ cần 15 switch riêng mỗi cái xử lý 20 case. Với visitor, mỗi pass là class visitor tự chứa.

Nếu thêm pass mới, bạn viết một visitor. Nếu dùng switch, bạn thêm một hàm với 20 case. Visitor giữ logic mỗi pass gắn kết. Tuy nhiên, nếu thêm kiểu node mới, bạn phải update cả 15 visitor — đây là đánh đổi kinh điển.
:::

::: details Câu 2: Plugin Babel là visitor. Chuyện gì nếu hai plugin visit cùng kiểu node và xung đột?
**Trả lời:** Thứ tự plugin quan trọng. Babel chạy visitor theo thứ tự plugin liệt kê trong config. Nếu plugin A biến đổi node mà plugin B cũng mong, output plugin đầu trở thành input plugin sau.

Điều này có thể gây bug tinh tế: plugin A viết lại `import` thành `require`, rồi plugin B (mong `import`) không match. Giải pháp: (1) Tài liệu yêu cầu thứ tự plugin, (2) Dùng ưu tiên visitor, (3) Chạy plugin xung đột ở pass riêng. Hook `pre`/`post` của Babel giúp phối hợp.
:::

::: details Câu 3: Visitor transform trong bài tập tạo node mới thay vì sửa. Sao bất biến quan trọng ở đây?
**Trả lời:** Transform bất biến an toàn hơn vì cây gốc được bảo toàn. Điều này cho phép: (1) chạy nhiều transform trên cùng input, (2) so trước/sau để debug, (3) rollback nếu transform fail, (4) transform song song trên cùng cây.

Visitor mutable nhanh hơn (không cấp phát) nhưng nguy hiểm — mutation của một visitor có thể phá visitor khác đang đọc cùng cây. LLVM dùng visitor mutable cho hiệu năng, nhưng compiler Vue dùng transform bất biến cho an toàn.
:::

::: details Câu 4: InstVisitor của LLVM có case mặc định gọi visitor class lệnh cha. Sao điều này hữu ích?
**Trả lời:** Nó triển khai hành vi fallback qua phân cấp class. Nếu bạn không override `visitAdd`, nó fallback về `visitBinaryOperator`, rồi `visitInstruction`, rồi no-op.

Điều này nghĩa bạn chỉ cần override các case quan tâm. Bộ đếm lệnh có thể override chỉ `visitInstruction` để đếm mọi lệnh. Tối ưu thao tác nhị phân có thể override chỉ `visitBinaryOperator` để xử lý add, sub, mul, div cùng lúc, không cần liệt kê mỗi cái. Đây là pattern "template method" áp dụng cho visitor.
:::
