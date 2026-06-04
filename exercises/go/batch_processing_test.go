package exercises

import "testing"

type Batch[T any] struct {
	size    int
	buffer  []T
	batches [][]T
}

func NewBatch[T any](size int) *Batch[T] {
	return &Batch[T]{size: size}
}

func (b *Batch[T]) Add(item T) {
	b.buffer = append(b.buffer, item)
	if len(b.buffer) >= b.size {
		b.flush()
	}
}

func (b *Batch[T]) flush() {
	if len(b.buffer) == 0 {
		return
	}
	cp := make([]T, len(b.buffer))
	copy(cp, b.buffer)
	b.batches = append(b.batches, cp)
	b.buffer = b.buffer[:0]
}

func (b *Batch[T]) Flush() {
	b.flush()
}

func (b *Batch[T]) Batches() [][]T {
	return b.batches
}

func TestBatchAutoFlush(t *testing.T) {
	b := NewBatch[int](3)
	for i := 1; i <= 6; i++ {
		b.Add(i)
	}

	batches := b.Batches()
	if len(batches) != 2 {
		t.Fatalf("expected 2 batches, got %d", len(batches))
	}
	if len(batches[0]) != 3 || batches[0][0] != 1 {
		t.Errorf("batch 0: %v", batches[0])
	}
}

func TestBatchManualFlush(t *testing.T) {
	b := NewBatch[string](10)
	b.Add("a")
	b.Add("b")
	b.Flush()

	batches := b.Batches()
	if len(batches) != 1 || len(batches[0]) != 2 {
		t.Errorf("expected 1 batch of 2, got %v", batches)
	}
}

func TestBatchEmptyFlush(t *testing.T) {
	b := NewBatch[int](5)
	b.Flush()
	if len(b.Batches()) != 0 {
		t.Error("flushing empty buffer should produce no batch")
	}
}

func TestBatchPartialAndFull(t *testing.T) {
	b := NewBatch[int](3)
	for i := 1; i <= 7; i++ {
		b.Add(i)
	}
	b.Flush() // flush remaining [7]

	batches := b.Batches()
	if len(batches) != 3 {
		t.Fatalf("expected 3 batches, got %d", len(batches))
	}
	if len(batches[2]) != 1 {
		t.Errorf("last batch should have 1 item, got %d", len(batches[2]))
	}
}
