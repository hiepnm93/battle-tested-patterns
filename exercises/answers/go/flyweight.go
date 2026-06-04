package answers

type FlyweightInterner struct {
	pool map[string]int
	data []string
}

func NewFlyweight() *FlyweightInterner {
	return &FlyweightInterner{pool: make(map[string]int)}
}

func (in *FlyweightInterner) Intern(s string) int {
	if id, ok := in.pool[s]; ok {
		return id
	}
	id := len(in.data)
	in.data = append(in.data, s)
	in.pool[s] = id
	return id
}

func (in *FlyweightInterner) Resolve(id int) string {
	return in.data[id]
}
