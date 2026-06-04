package exercises

import (
	"hash/fnv"
	"sort"
	"testing"
)

type HashRing struct {
	ring     []uint32
	nodeMap  map[uint32]string
	replicas int
}

func NewHashRing(replicas int) *HashRing {
	return &HashRing{replicas: replicas, nodeMap: make(map[uint32]string)}
}

func hashKey(key string) uint32 {
	h := fnv.New32a()
	h.Write([]byte(key))
	return h.Sum32()
}

func (hr *HashRing) AddNode(node string) {
	for i := 0; i < hr.replicas; i++ {
		vkey := node + "#" + string(rune('0'+i))
		hash := hashKey(vkey)
		hr.ring = append(hr.ring, hash)
		hr.nodeMap[hash] = node
	}
	sort.Slice(hr.ring, func(i, j int) bool { return hr.ring[i] < hr.ring[j] })
}

func (hr *HashRing) RemoveNode(node string) {
	var newRing []uint32
	for _, hash := range hr.ring {
		if hr.nodeMap[hash] != node {
			newRing = append(newRing, hash)
		} else {
			delete(hr.nodeMap, hash)
		}
	}
	hr.ring = newRing
}

func (hr *HashRing) GetNode(key string) string {
	if len(hr.ring) == 0 {
		return ""
	}
	hash := hashKey(key)
	idx := sort.Search(len(hr.ring), func(i int) bool { return hr.ring[i] >= hash })
	if idx == len(hr.ring) {
		idx = 0
	}
	return hr.nodeMap[hr.ring[idx]]
}

func TestHashRingBasic(t *testing.T) {
	hr := NewHashRing(3)
	hr.AddNode("server-a")
	hr.AddNode("server-b")
	hr.AddNode("server-c")

	node := hr.GetNode("my-key")
	if node == "" {
		t.Error("should return a node")
	}
}

func TestHashRingConsistency(t *testing.T) {
	hr := NewHashRing(50)
	hr.AddNode("server-a")
	hr.AddNode("server-b")
	hr.AddNode("server-c")

	results := make(map[string]string)
	keys := []string{"user:1", "user:2", "user:3", "session:abc", "order:999"}
	for _, k := range keys {
		results[k] = hr.GetNode(k)
	}

	for _, k := range keys {
		if hr.GetNode(k) != results[k] {
			t.Errorf("same key %q mapped to different node", k)
		}
	}
}

func TestHashRingMinimalDisruption(t *testing.T) {
	hr := NewHashRing(50)
	hr.AddNode("server-a")
	hr.AddNode("server-b")

	before := make(map[string]string)
	keys := make([]string, 100)
	for i := range keys {
		keys[i] = string(rune('a' + i%26))
		before[keys[i]] = hr.GetNode(keys[i])
	}

	hr.AddNode("server-c")
	moved := 0
	for _, k := range keys {
		if hr.GetNode(k) != before[k] {
			moved++
		}
	}

	if moved == len(keys) {
		t.Error("adding a node should not remap all keys")
	}
}

func TestHashRingRemoveNode(t *testing.T) {
	hr := NewHashRing(10)
	hr.AddNode("server-a")
	hr.AddNode("server-b")
	hr.RemoveNode("server-a")

	for _, k := range []string{"k1", "k2", "k3"} {
		if hr.GetNode(k) != "server-b" {
			t.Errorf("after removing server-a, all keys should go to server-b")
		}
	}
}
