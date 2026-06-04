interface ShapeVtable {
  area: (data: number[]) => number;
  perimeter: (data: number[]) => number;
}

interface Shape {
  vtable: ShapeVtable;
  data: number[];
}

const circleVtable: ShapeVtable = {
  area: (d) => Math.PI * d[0] * d[0],
  perimeter: (d) => 2 * Math.PI * d[0],
};

const rectVtable: ShapeVtable = {
  area: (d) => d[0] * d[1],
  perimeter: (d) => 2 * (d[0] + d[1]),
};

function createCircle(r: number): Shape {
  return { vtable: circleVtable, data: [r] };
}

function createRect(w: number, h: number): Shape {
  return { vtable: rectVtable, data: [w, h] };
}

// Polymorphic dispatch — works for any shape
function totalArea(shapes: Shape[]): number {
  return shapes.reduce((sum, s) => sum + s.vtable.area(s.data), 0);
}
