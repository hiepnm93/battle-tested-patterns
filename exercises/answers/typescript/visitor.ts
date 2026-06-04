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
