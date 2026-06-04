package exercises

import (
	"sync"
	"testing"
)

type Message struct {
	Type    string
	Payload int
}

type Actor struct {
	mailbox chan Message
	state   int
	mu      sync.Mutex
	done    chan struct{}
}

func NewActor() *Actor {
	a := &Actor{
		mailbox: make(chan Message, 100),
		done:    make(chan struct{}),
	}
	go a.run()
	return a
}

func (a *Actor) run() {
	for msg := range a.mailbox {
		a.mu.Lock()
		switch msg.Type {
		case "add":
			a.state += msg.Payload
		case "reset":
			a.state = 0
		}
		a.mu.Unlock()
	}
	close(a.done)
}

func (a *Actor) Send(msg Message) {
	a.mailbox <- msg
}

func (a *Actor) Stop() {
	close(a.mailbox)
	<-a.done
}

func (a *Actor) State() int {
	a.mu.Lock()
	defer a.mu.Unlock()
	return a.state
}

func TestActorProcessesMessages(t *testing.T) {
	a := NewActor()
	a.Send(Message{"add", 10})
	a.Send(Message{"add", 20})
	a.Stop()

	if a.State() != 30 {
		t.Errorf("expected 30, got %d", a.State())
	}
}

func TestActorReset(t *testing.T) {
	a := NewActor()
	a.Send(Message{"add", 100})
	a.Send(Message{"reset", 0})
	a.Send(Message{"add", 5})
	a.Stop()

	if a.State() != 5 {
		t.Errorf("expected 5, got %d", a.State())
	}
}

func TestActorConcurrentSenders(t *testing.T) {
	a := NewActor()
	var wg sync.WaitGroup
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			a.Send(Message{"add", 1})
		}()
	}
	wg.Wait()
	a.Stop()

	if a.State() != 100 {
		t.Errorf("expected 100, got %d", a.State())
	}
}
