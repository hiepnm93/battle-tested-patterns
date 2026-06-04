package answers

type Interner struct {
	strToID map[string]int
	idToStr []string
}

func NewInterner() *Interner {
	return &Interner{strToID: make(map[string]int)}
}

func (it *Interner) Intern(s string) int {
	if id, ok := it.strToID[s]; ok {
		return id
	}
	id := len(it.idToStr)
	it.strToID[s] = id
	it.idToStr = append(it.idToStr, s)
	return id
}

func (it *Interner) Resolve(id int) (string, bool) {
	if id < 0 || id >= len(it.idToStr) {
		return "", false
	}
	return it.idToStr[id], true
}
