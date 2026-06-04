package exercises

import (
	"iter"
	"slices"
	"testing"
)

func FilterSeq[T any](seq iter.Seq[T], pred func(T) bool) iter.Seq[T] {
	return func(yield func(T) bool) {
		for v := range seq {
			if pred(v) && !yield(v) {
				return
			}
		}
	}
}

func MapSeq[T, U any](seq iter.Seq[T], fn func(T) U) iter.Seq[U] {
	return func(yield func(U) bool) {
		for v := range seq {
			if !yield(fn(v)) {
				return
			}
		}
	}
}

func TakeSeq[T any](seq iter.Seq[T], n int) iter.Seq[T] {
	return func(yield func(T) bool) {
		i := 0
		for v := range seq {
			if i >= n || !yield(v) {
				return
			}
			i++
		}
	}
}

func CollectSeq[T any](seq iter.Seq[T]) []T {
	var out []T
	for v := range seq {
		out = append(out, v)
	}
	return out
}

func TestIteratorFilter(t *testing.T) {
	source := slices.Values([]int{1, 2, 3, 4, 5, 6})
	odds := CollectSeq(FilterSeq(source, func(x int) bool { return x%2 != 0 }))
	want := []int{1, 3, 5}
	if len(odds) != len(want) {
		t.Fatalf("got %v, want %v", odds, want)
	}
	for i, v := range odds {
		if v != want[i] {
			t.Errorf("odds[%d] = %d, want %d", i, v, want[i])
		}
	}
}

func TestIteratorMapAndTake(t *testing.T) {
	source := slices.Values([]int{1, 2, 3, 4, 5})
	doubled := CollectSeq(TakeSeq(MapSeq(source, func(x int) int { return x * 2 }), 3))
	want := []int{2, 4, 6}
	if len(doubled) != len(want) {
		t.Fatalf("got %v, want %v", doubled, want)
	}
	for i, v := range doubled {
		if v != want[i] {
			t.Errorf("doubled[%d] = %d, want %d", i, v, want[i])
		}
	}
}

func TestIteratorPipeline(t *testing.T) {
	source := slices.Values([]int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10})
	isOdd := func(x int) bool { return x%2 != 0 }
	times10 := func(x int) int { return x * 10 }
	result := CollectSeq(TakeSeq(MapSeq(FilterSeq(source, isOdd), times10), 3))
	want := []int{10, 30, 50}
	if len(result) != len(want) {
		t.Fatalf("got %v, want %v", result, want)
	}
	for i, v := range result {
		if v != want[i] {
			t.Errorf("result[%d] = %d, want %d", i, v, want[i])
		}
	}
}

func TestIteratorEmpty(t *testing.T) {
	source := slices.Values([]int{})
	result := CollectSeq(FilterSeq(source, func(x int) bool { return true }))
	if len(result) != 0 {
		t.Errorf("expected empty, got %v", result)
	}
}
