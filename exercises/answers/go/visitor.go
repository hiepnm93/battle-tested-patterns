package answers

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
