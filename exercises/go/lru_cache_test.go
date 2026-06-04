package exercises

import "testing"

type lruEntry struct {
	key        string
	value      int
	prev, next *lruEntry
}

type LRUCache struct {
	cap   int
	items map[string]*lruEntry
	head  *lruEntry
	tail  *lruEntry
}

func NewLRUCache(capacity int) *LRUCache {
	head := &lruEntry{}
	tail := &lruEntry{}
	head.next = tail
	tail.prev = head
	return &LRUCache{cap: capacity, items: make(map[string]*lruEntry), head: head, tail: tail}
}

func (c *LRUCache) remove(e *lruEntry) {
	e.prev.next = e.next
	e.next.prev = e.prev
}

func (c *LRUCache) pushFront(e *lruEntry) {
	e.next = c.head.next
	e.prev = c.head
	c.head.next.prev = e
	c.head.next = e
}

func (c *LRUCache) Get(key string) (int, bool) {
	e, ok := c.items[key]
	if !ok {
		return 0, false
	}
	c.remove(e)
	c.pushFront(e)
	return e.value, true
}

func (c *LRUCache) Put(key string, value int) {
	if e, ok := c.items[key]; ok {
		e.value = value
		c.remove(e)
		c.pushFront(e)
		return
	}
	if len(c.items) == c.cap {
		evict := c.tail.prev
		c.remove(evict)
		delete(c.items, evict.key)
	}
	e := &lruEntry{key: key, value: value}
	c.pushFront(e)
	c.items[key] = e
}

func TestLRUCacheBasic(t *testing.T) {
	c := NewLRUCache(2)
	c.Put("a", 1)
	c.Put("b", 2)

	if v, ok := c.Get("a"); !ok || v != 1 {
		t.Errorf("Get(a) = %d, want 1", v)
	}

	c.Put("c", 3) // evicts "b"
	if _, ok := c.Get("b"); ok {
		t.Error("b should have been evicted")
	}
}

func TestLRUCacheUpdate(t *testing.T) {
	c := NewLRUCache(2)
	c.Put("a", 1)
	c.Put("b", 2)
	c.Put("a", 10) // update, promotes "a"
	c.Put("c", 3)  // evicts "b" (LRU)

	if v, ok := c.Get("a"); !ok || v != 10 {
		t.Errorf("Get(a) = %d, want 10", v)
	}
	if _, ok := c.Get("b"); ok {
		t.Error("b should have been evicted")
	}
}

func TestLRUCacheAccessOrder(t *testing.T) {
	c := NewLRUCache(3)
	c.Put("a", 1)
	c.Put("b", 2)
	c.Put("c", 3)
	c.Get("a")     // promotes "a"
	c.Put("d", 4)  // evicts "b" (LRU)

	if _, ok := c.Get("b"); ok {
		t.Error("b should have been evicted")
	}
	if _, ok := c.Get("a"); !ok {
		t.Error("a should still be present")
	}
}
