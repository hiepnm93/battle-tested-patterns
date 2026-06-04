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
