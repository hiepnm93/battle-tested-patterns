package answers

type StateMachine struct {
	current     string
	transitions map[string]map[string]string // state -> event -> next
}

func NewStateMachine(initial string) *StateMachine {
	return &StateMachine{
		current:     initial,
		transitions: make(map[string]map[string]string),
	}
}

func (sm *StateMachine) AddTransition(from, event, to string) {
	if sm.transitions[from] == nil {
		sm.transitions[from] = make(map[string]string)
	}
	sm.transitions[from][event] = to
}

func (sm *StateMachine) Send(event string) string {
	if next, ok := sm.transitions[sm.current][event]; ok {
		sm.current = next
	}
	return sm.current
}

func (sm *StateMachine) Can(event string) bool {
	_, ok := sm.transitions[sm.current][event]
	return ok
}

func (sm *StateMachine) State() string { return sm.current }
