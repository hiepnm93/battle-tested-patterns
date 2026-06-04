struct ShapeVtable {
    area: fn(&[f64]) -> f64,
    perimeter: fn(&[f64]) -> f64,
}

struct Shape {
    vtable: &'static ShapeVtable,
    data: Vec<f64>,
}

static CIRCLE_VTABLE: ShapeVtable = ShapeVtable {
    area: |d| std::f64::consts::PI * d[0] * d[0],
    perimeter: |d| 2.0 * std::f64::consts::PI * d[0],
};

static RECT_VTABLE: ShapeVtable = ShapeVtable {
    area: |d| d[0] * d[1],
    perimeter: |d| 2.0 * (d[0] + d[1]),
};

fn create_circle(r: f64) -> Shape {
    Shape { vtable: &CIRCLE_VTABLE, data: vec![r] }
}

fn create_rect(w: f64, h: f64) -> Shape {
    Shape { vtable: &RECT_VTABLE, data: vec![w, h] }
}
