package exercises

import (
	"errors"
	"testing"
	"time"
)

type CBState int

const (
	CBClosed CBState = iota
	CBOpen
	CBHalfOpen
)

type CircuitBreaker struct {
	state     CBState
	failures  int
	threshold int
	timeout   time.Duration
	openedAt  time.Time
}

func NewCircuitBreaker(threshold int, timeout time.Duration) *CircuitBreaker {
	return &CircuitBreaker{state: CBClosed, threshold: threshold, timeout: timeout}
}

func (cb *CircuitBreaker) Call(fn func() error) error {
	switch cb.state {
	case CBOpen:
		if time.Since(cb.openedAt) > cb.timeout {
			cb.state = CBHalfOpen
		} else {
			return errors.New("circuit open")
		}
	}

	err := fn()
	if err != nil {
		cb.failures++
		if cb.failures >= cb.threshold {
			cb.state = CBOpen
			cb.openedAt = time.Now()
		}
		return err
	}

	cb.failures = 0
	cb.state = CBClosed
	return nil
}

func (cb *CircuitBreaker) State() CBState { return cb.state }

func TestCircuitBreakerClosedOnSuccess(t *testing.T) {
	cb := NewCircuitBreaker(3, time.Second)
	err := cb.Call(func() error { return nil })
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if cb.State() != CBClosed {
		t.Error("should remain closed on success")
	}
}

func TestCircuitBreakerOpensOnFailures(t *testing.T) {
	cb := NewCircuitBreaker(3, time.Second)
	fail := func() error { return errors.New("fail") }

	cb.Call(fail)
	cb.Call(fail)
	if cb.State() != CBClosed {
		t.Error("should still be closed before threshold")
	}

	cb.Call(fail)
	if cb.State() != CBOpen {
		t.Error("should be open after threshold failures")
	}
}

func TestCircuitBreakerRejectsWhenOpen(t *testing.T) {
	cb := NewCircuitBreaker(1, time.Hour)
	cb.Call(func() error { return errors.New("fail") })

	err := cb.Call(func() error { return nil })
	if err == nil || err.Error() != "circuit open" {
		t.Error("should reject calls when open")
	}
}

func TestCircuitBreakerRecovery(t *testing.T) {
	cb := NewCircuitBreaker(1, time.Millisecond)
	cb.Call(func() error { return errors.New("fail") })

	time.Sleep(5 * time.Millisecond)

	err := cb.Call(func() error { return nil })
	if err != nil {
		t.Errorf("should allow call after timeout: %v", err)
	}
	if cb.State() != CBClosed {
		t.Error("should be closed after successful half-open call")
	}
}
