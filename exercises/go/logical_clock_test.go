package exercises

import "testing"

type LamportClock struct {
	time uint64
}

func NewLamportClock() *LamportClock {
	return &LamportClock{}
}

func (c *LamportClock) Tick() uint64 {
	c.time++
	return c.time
}

func (c *LamportClock) Send() uint64 {
	c.time++
	return c.time
}

func (c *LamportClock) Receive(remote uint64) uint64 {
	if remote > c.time {
		c.time = remote
	}
	c.time++
	return c.time
}

func (c *LamportClock) Time() uint64 { return c.time }

func TestLamportClockTick(t *testing.T) {
	c := NewLamportClock()
	t1 := c.Tick()
	t2 := c.Tick()
	if t2 <= t1 {
		t.Error("each tick should increase the clock")
	}
}

func TestLamportClockSendReceive(t *testing.T) {
	a := NewLamportClock()
	b := NewLamportClock()

	a.Tick()
	a.Tick()
	msgTime := a.Send()

	recvTime := b.Receive(msgTime)
	if recvTime <= msgTime {
		t.Error("receive should produce time > message time")
	}
}

func TestLamportClockCausality(t *testing.T) {
	a := NewLamportClock()
	b := NewLamportClock()

	a.Tick() // a=1
	a.Tick() // a=2
	a.Tick() // a=3

	b.Tick() // b=1

	msg := a.Send() // a=4, msg=4
	recv := b.Receive(msg) // b=max(1,4)+1=5

	if recv <= msg {
		t.Errorf("recv(%d) should be > msg(%d)", recv, msg)
	}
}

func TestLamportClockMonotonic(t *testing.T) {
	c := NewLamportClock()
	prev := c.Time()
	for i := 0; i < 100; i++ {
		curr := c.Tick()
		if curr <= prev {
			t.Errorf("clock not monotonic at step %d", i)
		}
		prev = curr
	}
}
