package exercises

import "testing"

type Task struct {
	name string
	fn   func()
}

type EventLoop struct {
	queue []Task
}

func NewEventLoop() *EventLoop {
	return &EventLoop{}
}

func (el *EventLoop) Enqueue(name string, fn func()) {
	el.queue = append(el.queue, Task{name: name, fn: fn})
}

func (el *EventLoop) Run() []string {
	var executed []string
	for len(el.queue) > 0 {
		task := el.queue[0]
		el.queue = el.queue[1:]
		task.fn()
		executed = append(executed, task.name)
	}
	return executed
}

func (el *EventLoop) Pending() int { return len(el.queue) }

func TestEventLoopOrder(t *testing.T) {
	el := NewEventLoop()
	var log []int
	el.Enqueue("a", func() { log = append(log, 1) })
	el.Enqueue("b", func() { log = append(log, 2) })
	el.Enqueue("c", func() { log = append(log, 3) })

	names := el.Run()
	if len(names) != 3 || names[0] != "a" || names[1] != "b" || names[2] != "c" {
		t.Errorf("expected [a,b,c], got %v", names)
	}
	want := []int{1, 2, 3}
	for i, v := range log {
		if v != want[i] {
			t.Errorf("log[%d] = %d, want %d", i, v, want[i])
		}
	}
}

func TestEventLoopEnqueueDuringRun(t *testing.T) {
	el := NewEventLoop()
	var log []string
	el.Enqueue("first", func() {
		log = append(log, "first")
		el.Enqueue("nested", func() { log = append(log, "nested") })
	})

	el.Run()
	if len(log) != 2 || log[0] != "first" || log[1] != "nested" {
		t.Errorf("expected [first, nested], got %v", log)
	}
}

func TestEventLoopEmpty(t *testing.T) {
	el := NewEventLoop()
	names := el.Run()
	if len(names) != 0 {
		t.Error("empty loop should produce no results")
	}
}
