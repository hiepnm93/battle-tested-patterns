use std::time::{Duration, Instant};

#[derive(Debug, PartialEq)]
pub enum State {
    Closed,
    Open,
    HalfOpen,
}

pub struct CircuitBreaker {
    state: State,
    failures: u32,
    threshold: u32,
    timeout: Duration,
    opened_at: Option<Instant>,
}

impl CircuitBreaker {
    pub fn new(threshold: u32, timeout: Duration) -> Self {
        CircuitBreaker {
            state: State::Closed,
            failures: 0,
            threshold,
            timeout,
            opened_at: None,
        }
    }

    pub fn call<F, E>(&mut self, f: F) -> Result<(), E>
    where
        F: FnOnce() -> Result<(), E>,
        E: std::fmt::Display,
    {
        if self.state == State::Open {
            if let Some(opened) = self.opened_at {
                if opened.elapsed() > self.timeout {
                    self.state = State::HalfOpen;
                } else {
                    return Err(self.circuit_open_error());
                }
            }
        }

        match f() {
            Ok(()) => {
                self.failures = 0;
                self.state = State::Closed;
                Ok(())
            }
            Err(e) => {
                self.failures += 1;
                if self.failures >= self.threshold {
                    self.state = State::Open;
                    self.opened_at = Some(Instant::now());
                }
                Err(e)
            }
        }
    }

    fn circuit_open_error<E>(&self) -> E
    where
        E: std::fmt::Display,
    {
        panic!("circuit open");
    }

    pub fn state(&self) -> &State {
        &self.state
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_closed_on_success() {
        let mut cb = CircuitBreaker::new(3, Duration::from_secs(1));
        let result: Result<(), String> = cb.call(|| Ok(()));
        assert!(result.is_ok());
        assert_eq!(cb.state(), &State::Closed);
    }

    #[test]
    fn test_opens_on_failures() {
        let mut cb = CircuitBreaker::new(3, Duration::from_secs(1));
        let fail = || -> Result<(), String> { Err("fail".into()) };
        let _ = cb.call(fail);
        let _ = cb.call(fail);
        assert_eq!(cb.state(), &State::Closed);
        let _ = cb.call(fail);
        assert_eq!(cb.state(), &State::Open);
    }

    #[test]
    fn test_recovery() {
        let mut cb = CircuitBreaker::new(1, Duration::from_millis(1));
        let _ = cb.call(|| -> Result<(), String> { Err("fail".into()) });
        assert_eq!(cb.state(), &State::Open);

        std::thread::sleep(Duration::from_millis(5));

        let result: Result<(), String> = cb.call(|| Ok(()));
        assert!(result.is_ok());
        assert_eq!(cb.state(), &State::Closed);
    }
}
