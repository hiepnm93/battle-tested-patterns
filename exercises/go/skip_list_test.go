package exercises

import (
	"math/rand"
	"testing"
)

const skipMaxLevel = 4

type skipNode struct {
	key   int
	value string
	next  []*skipNode
}

type SkipList struct {
	head  *skipNode
	level int
	rng   *rand.Rand
}

func NewSkipList() *SkipList {
	head := &skipNode{next: make([]*skipNode, skipMaxLevel)}
	return &SkipList{head: head, level: 0, rng: rand.New(rand.NewSource(42))}
}

func (sl *SkipList) randomLevel() int {
	lvl := 0
	for lvl < skipMaxLevel-1 && sl.rng.Float64() < 0.5 {
		lvl++
	}
	return lvl
}

func (sl *SkipList) Insert(key int, value string) {
	update := make([]*skipNode, skipMaxLevel)
	cur := sl.head
	for i := sl.level; i >= 0; i-- {
		for cur.next[i] != nil && cur.next[i].key < key {
			cur = cur.next[i]
		}
		update[i] = cur
	}

	if cur.next[0] != nil && cur.next[0].key == key {
		cur.next[0].value = value
		return
	}

	lvl := sl.randomLevel()
	if lvl > sl.level {
		for i := sl.level + 1; i <= lvl; i++ {
			update[i] = sl.head
		}
		sl.level = lvl
	}

	node := &skipNode{key: key, value: value, next: make([]*skipNode, lvl+1)}
	for i := 0; i <= lvl; i++ {
		node.next[i] = update[i].next[i]
		update[i].next[i] = node
	}
}

func (sl *SkipList) Search(key int) (string, bool) {
	cur := sl.head
	for i := sl.level; i >= 0; i-- {
		for cur.next[i] != nil && cur.next[i].key < key {
			cur = cur.next[i]
		}
	}
	cur = cur.next[0]
	if cur != nil && cur.key == key {
		return cur.value, true
	}
	return "", false
}

func (sl *SkipList) Delete(key int) bool {
	update := make([]*skipNode, skipMaxLevel)
	cur := sl.head
	for i := sl.level; i >= 0; i-- {
		for cur.next[i] != nil && cur.next[i].key < key {
			cur = cur.next[i]
		}
		update[i] = cur
	}

	target := cur.next[0]
	if target == nil || target.key != key {
		return false
	}
	for i := 0; i <= sl.level; i++ {
		if update[i].next[i] != target {
			break
		}
		update[i].next[i] = target.next[i]
	}
	for sl.level > 0 && sl.head.next[sl.level] == nil {
		sl.level--
	}
	return true
}

func TestSkipListInsertAndSearch(t *testing.T) {
	sl := NewSkipList()
	sl.Insert(3, "three")
	sl.Insert(1, "one")
	sl.Insert(2, "two")

	if v, ok := sl.Search(2); !ok || v != "two" {
		t.Errorf("Search(2) = %q, want %q", v, "two")
	}
	if _, ok := sl.Search(99); ok {
		t.Error("Search(99) should return false")
	}
}

func TestSkipListDelete(t *testing.T) {
	sl := NewSkipList()
	sl.Insert(1, "one")
	sl.Insert(2, "two")
	sl.Insert(3, "three")

	if !sl.Delete(2) {
		t.Error("Delete(2) should succeed")
	}
	if _, ok := sl.Search(2); ok {
		t.Error("Search(2) should fail after delete")
	}
	if v, ok := sl.Search(1); !ok || v != "one" {
		t.Error("other keys should be unaffected")
	}
}

func TestSkipListUpdate(t *testing.T) {
	sl := NewSkipList()
	sl.Insert(1, "old")
	sl.Insert(1, "new")

	if v, ok := sl.Search(1); !ok || v != "new" {
		t.Errorf("Search(1) = %q, want %q", v, "new")
	}
}

func TestSkipListOrdering(t *testing.T) {
	sl := NewSkipList()
	for _, k := range []int{50, 10, 30, 20, 40} {
		sl.Insert(k, "")
	}
	var keys []int
	cur := sl.head.next[0]
	for cur != nil {
		keys = append(keys, cur.key)
		cur = cur.next[0]
	}
	for i := 1; i < len(keys); i++ {
		if keys[i] <= keys[i-1] {
			t.Errorf("keys not sorted: %v", keys)
			break
		}
	}
}
