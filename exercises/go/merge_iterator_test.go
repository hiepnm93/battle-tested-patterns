package exercises

import (
	"container/heap"
	"testing"
)

type mergeItem struct {
	value    int
	listIdx  int
	elemIdx  int
}

type mergeHeap []mergeItem

func (h mergeHeap) Len() int            { return len(h) }
func (h mergeHeap) Less(i, j int) bool   { return h[i].value < h[j].value }
func (h mergeHeap) Swap(i, j int)        { h[i], h[j] = h[j], h[i] }
func (h *mergeHeap) Push(x any)          { *h = append(*h, x.(mergeItem)) }
func (h *mergeHeap) Pop() any {
	old := *h
	n := len(old)
	item := old[n-1]
	*h = old[:n-1]
	return item
}

func MergeKSorted(lists [][]int) []int {
	h := &mergeHeap{}
	heap.Init(h)

	for i, list := range lists {
		if len(list) > 0 {
			heap.Push(h, mergeItem{value: list[0], listIdx: i, elemIdx: 0})
		}
	}

	var result []int
	for h.Len() > 0 {
		item := heap.Pop(h).(mergeItem)
		result = append(result, item.value)
		next := item.elemIdx + 1
		if next < len(lists[item.listIdx]) {
			heap.Push(h, mergeItem{value: lists[item.listIdx][next], listIdx: item.listIdx, elemIdx: next})
		}
	}
	return result
}

func TestMergeKSorted(t *testing.T) {
	lists := [][]int{
		{1, 4, 7},
		{2, 5, 8},
		{3, 6, 9},
	}
	result := MergeKSorted(lists)
	want := []int{1, 2, 3, 4, 5, 6, 7, 8, 9}
	if len(result) != len(want) {
		t.Fatalf("got %v, want %v", result, want)
	}
	for i, v := range result {
		if v != want[i] {
			t.Errorf("result[%d] = %d, want %d", i, v, want[i])
		}
	}
}

func TestMergeKSortedUnequal(t *testing.T) {
	lists := [][]int{
		{1, 10},
		{2, 3, 4, 5},
		{6},
	}
	result := MergeKSorted(lists)
	for i := 1; i < len(result); i++ {
		if result[i] < result[i-1] {
			t.Errorf("not sorted at index %d: %v", i, result)
			break
		}
	}
}

func TestMergeKSortedEmpty(t *testing.T) {
	result := MergeKSorted([][]int{{}, {}, {}})
	if len(result) != 0 {
		t.Error("merging empty lists should produce empty result")
	}
}

func TestMergeKSortedSingleList(t *testing.T) {
	result := MergeKSorted([][]int{{5, 10, 15}})
	want := []int{5, 10, 15}
	for i, v := range result {
		if v != want[i] {
			t.Errorf("result[%d] = %d, want %d", i, v, want[i])
		}
	}
}
