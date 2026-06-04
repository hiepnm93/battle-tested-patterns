package answers

import "math"

type ShapeOps struct {
	Area      func(data []float64) float64
	Perimeter func(data []float64) float64
}

type Shape struct {
	Ops  *ShapeOps
	Data []float64
}

var CircleOps = &ShapeOps{
	Area:      func(d []float64) float64 { return math.Pi * d[0] * d[0] },
	Perimeter: func(d []float64) float64 { return 2 * math.Pi * d[0] },
}

var RectOps = &ShapeOps{
	Area:      func(d []float64) float64 { return d[0] * d[1] },
	Perimeter: func(d []float64) float64 { return 2 * (d[0] + d[1]) },
}

func NewCircle(r float64) Shape { return Shape{Ops: CircleOps, Data: []float64{r}} }
func NewRect(w, h float64) Shape { return Shape{Ops: RectOps, Data: []float64{w, h}} }
