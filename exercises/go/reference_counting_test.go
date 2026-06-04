package exercises

import (
	"sync/atomic"
	"testing"
)

type RcInner[T any] struct {
	value    T
	refCount int64
	dropped  *bool
}

type Rc[T any] struct {
	inner *RcInner[T]
}

func NewRc[T any](value T, dropped *bool) Rc[T] {
	return Rc[T]{inner: &RcInner[T]{value: value, refCount: 1, dropped: dropped}}
}

func (r Rc[T]) Clone() Rc[T] {
	atomic.AddInt64(&r.inner.refCount, 1)
	return Rc[T]{inner: r.inner}
}

func (r Rc[T]) Drop() {
	if atomic.AddInt64(&r.inner.refCount, -1) == 0 {
		*r.inner.dropped = true
	}
}

func (r Rc[T]) RefCount() int64 {
	return atomic.LoadInt64(&r.inner.refCount)
}

func (r Rc[T]) Value() T {
	return r.inner.value
}

func TestRcBasic(t *testing.T) {
	dropped := false
	r := NewRc(42, &dropped)
	if r.Value() != 42 {
		t.Errorf("expected 42, got %d", r.Value())
	}
	if r.RefCount() != 1 {
		t.Errorf("expected refcount 1, got %d", r.RefCount())
	}
	r.Drop()
	if !dropped {
		t.Error("should be dropped when refcount reaches 0")
	}
}

func TestRcClone(t *testing.T) {
	dropped := false
	r1 := NewRc("hello", &dropped)
	r2 := r1.Clone()

	if r1.RefCount() != 2 {
		t.Errorf("expected refcount 2, got %d", r1.RefCount())
	}

	r1.Drop()
	if dropped {
		t.Error("should not be dropped while r2 still holds a ref")
	}
	if r2.RefCount() != 1 {
		t.Errorf("expected refcount 1, got %d", r2.RefCount())
	}

	r2.Drop()
	if !dropped {
		t.Error("should be dropped when last ref is gone")
	}
}

func TestRcMultipleClones(t *testing.T) {
	dropped := false
	r := NewRc(99, &dropped)
	clones := make([]Rc[int], 5)
	for i := range clones {
		clones[i] = r.Clone()
	}
	if r.RefCount() != 6 {
		t.Errorf("expected refcount 6, got %d", r.RefCount())
	}
	for _, c := range clones {
		c.Drop()
	}
	if dropped {
		t.Error("should not be dropped, original still alive")
	}
	r.Drop()
	if !dropped {
		t.Error("should be dropped after all refs gone")
	}
}
