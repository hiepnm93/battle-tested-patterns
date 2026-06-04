package answers

type EventLoop struct {
	handlers map[int]func()
}

func NewEventLoop() *EventLoop {
	return &EventLoop{handlers: make(map[int]func())}
}

func (el *EventLoop) AddHandler(fd int, handler func()) {
	el.handlers[fd] = handler
}

func (el *EventLoop) RemoveHandler(fd int) {
	delete(el.handlers, fd)
}

func (el *EventLoop) Tick() int {
	count := len(el.handlers)
	for _, handler := range el.handlers {
		handler()
	}
	return count
}

func (el *EventLoop) Run(maxTicks int) int {
	ticksRun := 0
	for i := 0; i < maxTicks; i++ {
		if len(el.handlers) == 0 {
			break
		}
		el.Tick()
		ticksRun++
	}
	return ticksRun
}
