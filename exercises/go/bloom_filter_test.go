package exercises

import (
	"hash/fnv"
	"testing"
)

type BloomFilter struct {
	bits []bool
	size uint32
	k    int
}

func NewBloomFilter(size uint32, numHashes int) *BloomFilter {
	return &BloomFilter{bits: make([]bool, size), size: size, k: numHashes}
}

func (bf *BloomFilter) hashes(item string) []uint32 {
	h := fnv.New32a()
	h.Write([]byte(item))
	h1 := h.Sum32()
	h.Reset()
	h.Write([]byte(item + "#"))
	h2 := h.Sum32()

	indices := make([]uint32, bf.k)
	for i := 0; i < bf.k; i++ {
		indices[i] = (h1 + uint32(i)*h2) % bf.size
	}
	return indices
}

func (bf *BloomFilter) Add(item string) {
	for _, idx := range bf.hashes(item) {
		bf.bits[idx] = true
	}
}

func (bf *BloomFilter) MayContain(item string) bool {
	for _, idx := range bf.hashes(item) {
		if !bf.bits[idx] {
			return false
		}
	}
	return true
}

func TestBloomFilterAddAndCheck(t *testing.T) {
	bf := NewBloomFilter(1024, 3)
	bf.Add("hello")
	bf.Add("world")

	if !bf.MayContain("hello") {
		t.Error("should contain hello")
	}
	if !bf.MayContain("world") {
		t.Error("should contain world")
	}
}

func TestBloomFilterNoFalseNegative(t *testing.T) {
	bf := NewBloomFilter(4096, 5)
	items := []string{"alpha", "beta", "gamma", "delta", "epsilon"}
	for _, item := range items {
		bf.Add(item)
	}
	for _, item := range items {
		if !bf.MayContain(item) {
			t.Errorf("false negative for %q", item)
		}
	}
}

func TestBloomFilterProbablyAbsent(t *testing.T) {
	bf := NewBloomFilter(4096, 5)
	bf.Add("present")

	absent := []string{"absent1", "absent2", "absent3", "missing", "nope"}
	falsePositives := 0
	for _, item := range absent {
		if bf.MayContain(item) {
			falsePositives++
		}
	}
	if falsePositives == len(absent) {
		t.Error("all absent items reported as present — filter is broken")
	}
}
