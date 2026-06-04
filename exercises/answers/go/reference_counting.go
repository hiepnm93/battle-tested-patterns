package answers

import "sync"

type RefCounted[T any] struct {
	mu      sync.Mutex
	value   T
	count   int
	cleanup func(T)
}

func NewRefCounted[T any](value T, cleanup func(T)) *RefCounted[T] {
	return &RefCounted[T]{value: value, count: 1, cleanup: cleanup}
}

func (rc *RefCounted[T]) Clone() *RefCounted[T] {
	rc.mu.Lock()
	defer rc.mu.Unlock()
	rc.count++
	return rc // same pointer, shared state
}

func (rc *RefCounted[T]) Drop() {
	rc.mu.Lock()
	defer rc.mu.Unlock()
	rc.count--
	if rc.count == 0 {
		rc.cleanup(rc.value)
	}
}

func (rc *RefCounted[T]) Count() int {
	rc.mu.Lock()
	defer rc.mu.Unlock()
	return rc.count
}
