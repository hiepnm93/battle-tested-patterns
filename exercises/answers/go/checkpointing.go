package answers

type LogEntry struct {
	ID        int
	Operation string
	Key       string
	Value     any
}

type stateSnapshot struct {
	state       map[string]any
	walPosition int
}

type CheckpointableStore struct {
	state      map[string]any
	wal        []LogEntry
	nextID     int
	checkpoint *stateSnapshot
}

func NewStore() *CheckpointableStore {
	return &CheckpointableStore{
		state:  make(map[string]any),
		nextID: 1,
	}
}

func (s *CheckpointableStore) Apply(operation, key string, value any) {
	entry := LogEntry{ID: s.nextID, Operation: operation, Key: key, Value: value}
	s.nextID++
	s.wal = append(s.wal, entry)
	s.executeOp(entry)
}

func (s *CheckpointableStore) Get(key string) (any, bool) {
	v, ok := s.state[key]
	return v, ok
}

func (s *CheckpointableStore) TakeCheckpoint() {
	snap := make(map[string]any, len(s.state))
	for k, v := range s.state {
		snap[k] = v
	}
	s.checkpoint = &stateSnapshot{state: snap, walPosition: len(s.wal)}
}

func (s *CheckpointableStore) SimulateCrash() {
	s.state = make(map[string]any)
}

func (s *CheckpointableStore) Recover() int {
	if s.checkpoint != nil {
		s.state = make(map[string]any, len(s.checkpoint.state))
		for k, v := range s.checkpoint.state {
			s.state[k] = v
		}
		replayed := 0
		for i := s.checkpoint.walPosition; i < len(s.wal); i++ {
			s.executeOp(s.wal[i])
			replayed++
		}
		return replayed
	}
	s.state = make(map[string]any)
	for _, entry := range s.wal {
		s.executeOp(entry)
	}
	return len(s.wal)
}

func (s *CheckpointableStore) executeOp(entry LogEntry) {
	if entry.Operation == "SET" {
		s.state[entry.Key] = entry.Value
	} else if entry.Operation == "DELETE" {
		delete(s.state, entry.Key)
	}
}

func (s *CheckpointableStore) WALLength() int   { return len(s.wal) }
func (s *CheckpointableStore) StateSize() int    { return len(s.state) }
