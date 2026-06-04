package answers

import "sort"

type KVEntry struct {
	Key   string
	Value *string // nil = tombstone
	Seq   int
}

type Memtable struct {
	entries map[string]KVEntry
	size    int
}

func NewMemtable() *Memtable {
	return &Memtable{entries: make(map[string]KVEntry)}
}

func (m *Memtable) Put(key, value string, seq int) {
	m.entries[key] = KVEntry{Key: key, Value: &value, Seq: seq}
	m.size++
}

func (m *Memtable) Delete(key string, seq int) {
	m.entries[key] = KVEntry{Key: key, Value: nil, Seq: seq}
	m.size++
}

func (m *Memtable) Get(key string) (KVEntry, bool) {
	e, ok := m.entries[key]
	return e, ok
}

func (m *Memtable) Flush() []KVEntry {
	result := make([]KVEntry, 0, len(m.entries))
	for _, e := range m.entries {
		result = append(result, e)
	}
	sort.Slice(result, func(i, j int) bool {
		return result[i].Key < result[j].Key
	})
	m.entries = make(map[string]KVEntry)
	m.size = 0
	return result
}

type LSMTree struct {
	memtable       *Memtable
	runs           [][]KVEntry
	seq            int
	flushThreshold int
	maxRuns        int
}

func NewLSMTree(flushThreshold, maxRuns int) *LSMTree {
	return &LSMTree{
		memtable:       NewMemtable(),
		flushThreshold: flushThreshold,
		maxRuns:        maxRuns,
	}
}

func (t *LSMTree) Put(key, value string) {
	t.memtable.Put(key, value, t.seq)
	t.seq++
	if t.memtable.size >= t.flushThreshold {
		t.flushMemtable()
	}
}

func (t *LSMTree) Delete(key string) {
	t.memtable.Delete(key, t.seq)
	t.seq++
	if t.memtable.size >= t.flushThreshold {
		t.flushMemtable()
	}
}

func (t *LSMTree) Get(key string) (string, bool) {
	if e, ok := t.memtable.Get(key); ok {
		if e.Value == nil {
			return "", false
		}
		return *e.Value, true
	}
	for _, run := range t.runs {
		if e := binarySearch(run, key); e != nil {
			if e.Value == nil {
				return "", false
			}
			return *e.Value, true
		}
	}
	return "", false
}

func binarySearch(run []KVEntry, key string) *KVEntry {
	lo, hi := 0, len(run)-1
	for lo <= hi {
		mid := (lo + hi) / 2
		if run[mid].Key == key {
			return &run[mid]
		}
		if run[mid].Key < key {
			lo = mid + 1
		} else {
			hi = mid - 1
		}
	}
	return nil
}

func (t *LSMTree) flushMemtable() {
	run := t.memtable.Flush()
	t.runs = append([][]KVEntry{run}, t.runs...)
	if len(t.runs) > t.maxRuns {
		t.compact()
	}
}

func (t *LSMTree) compact() {
	merged := make(map[string]KVEntry)
	for i := len(t.runs) - 1; i >= 0; i-- {
		for _, e := range t.runs[i] {
			merged[e.Key] = e
		}
	}
	result := make([]KVEntry, 0)
	for _, e := range merged {
		if e.Value != nil {
			result = append(result, e)
		}
	}
	sort.Slice(result, func(i, j int) bool {
		return result[i].Key < result[j].Key
	})
	if len(result) > 0 {
		t.runs = [][]KVEntry{result}
	} else {
		t.runs = nil
	}
}

func (t *LSMTree) RunCount() int {
	return len(t.runs)
}
