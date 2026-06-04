package exercises

import "testing"

type RingBuffer[T any] struct {
	buf  []T
	head int
	tail int
	cnt  int
	cap  int
}

func NewRingBuffer[T any](capacity int) *RingBuffer[T] {
	return &RingBuffer[T]{buf: make([]T, capacity), cap: capacity}
}

func (r *RingBuffer[T]) Enqueue(item T) bool {
	if r.cnt == r.cap {
		return false
	}
	r.buf[r.tail] = item
	r.tail = (r.tail + 1) % r.cap
	r.cnt++
	return true
}

func (r *RingBuffer[T]) Dequeue() (T, bool) {
	var zero T
	if r.cnt == 0 {
		return zero, false
	}
	item := r.buf[r.head]
	r.head = (r.head + 1) % r.cap
	r.cnt--
	return item, true
}

func (r *RingBuffer[T]) Len() int  { return r.cnt }
func (r *RingBuffer[T]) IsFull() bool { return r.cnt == r.cap }

func TestRingBufferEnqueueDequeue(t *testing.T) {
	rb := NewRingBuffer[int](3)
	if !rb.Enqueue(1) || !rb.Enqueue(2) || !rb.Enqueue(3) {
		t.Fatal("enqueue should succeed")
	}
	if rb.Enqueue(4) {
		t.Error("enqueue on full buffer should fail")
	}
	for _, want := range []int{1, 2, 3} {
		got, ok := rb.Dequeue()
		if !ok || got != want {
			t.Errorf("Dequeue() = %d, want %d", got, want)
		}
	}
}

func TestRingBufferWrapAround(t *testing.T) {
	rb := NewRingBuffer[string](2)
	rb.Enqueue("a")
	rb.Enqueue("b")
	rb.Dequeue()
	rb.Enqueue("c")

	got, _ := rb.Dequeue()
	if got != "b" {
		t.Errorf("got %q, want %q", got, "b")
	}
	got, _ = rb.Dequeue()
	if got != "c" {
		t.Errorf("got %q, want %q", got, "c")
	}
}

func TestRingBufferEmpty(t *testing.T) {
	rb := NewRingBuffer[int](4)
	if rb.Len() != 0 {
		t.Error("new buffer should be empty")
	}
	if _, ok := rb.Dequeue(); ok {
		t.Error("dequeue on empty should fail")
	}
}
