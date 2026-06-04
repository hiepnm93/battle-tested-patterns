package answers

type heapEntry struct {
	val    int
	stream int
	index  int
}

type minHeap struct {
	data []heapEntry
}

func (h *minHeap) Len() int            { return len(h.data) }
func (h *minHeap) Less(i, j int) bool  { return h.data[i].val < h.data[j].val }
func (h *minHeap) Swap(i, j int)       { h.data[i], h.data[j] = h.data[j], h.data[i] }
func (h *minHeap) Push(x heapEntry)    { h.data = append(h.data, x); h.bubbleUp(len(h.data) - 1) }

func (h *minHeap) Pop() heapEntry {
	top := h.data[0]
	last := h.data[len(h.data)-1]
	h.data = h.data[:len(h.data)-1]
	if len(h.data) > 0 {
		h.data[0] = last
		h.sinkDown(0)
	}
	return top
}

func (h *minHeap) bubbleUp(i int) {
	for i > 0 {
		parent := (i - 1) / 2
		if h.data[i].val >= h.data[parent].val {
			break
		}
		h.data[i], h.data[parent] = h.data[parent], h.data[i]
		i = parent
	}
}

func (h *minHeap) sinkDown(i int) {
	n := len(h.data)
	for {
		smallest := i
		left, right := 2*i+1, 2*i+2
		if left < n && h.data[left].val < h.data[smallest].val {
			smallest = left
		}
		if right < n && h.data[right].val < h.data[smallest].val {
			smallest = right
		}
		if smallest == i {
			break
		}
		h.data[i], h.data[smallest] = h.data[smallest], h.data[i]
		i = smallest
	}
}

func MergeKSorted(streams [][]int) []int {
	h := &minHeap{}
	for s, stream := range streams {
		if len(stream) > 0 {
			h.Push(heapEntry{val: stream[0], stream: s, index: 0})
		}
	}

	var result []int
	for h.Len() > 0 {
		entry := h.Pop()
		result = append(result, entry.val)
		nextIdx := entry.index + 1
		if nextIdx < len(streams[entry.stream]) {
			h.Push(heapEntry{val: streams[entry.stream][nextIdx], stream: entry.stream, index: nextIdx})
		}
	}
	return result
}
