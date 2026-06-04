use std::sync::mpsc;
use std::sync::{Arc, Mutex};
use std::thread;

enum Message {
    Add(i64),
    Reset,
}

struct Actor {
    sender: mpsc::Sender<Message>,
    state: Arc<Mutex<i64>>,
    handle: Option<thread::JoinHandle<()>>,
}

impl Actor {
    fn new() -> Self {
        let (sender, receiver) = mpsc::channel();
        let state = Arc::new(Mutex::new(0i64));
        let s = Arc::clone(&state);

        let handle = thread::spawn(move || {
            for msg in receiver {
                let mut val = s.lock().unwrap();
                match msg {
                    Message::Add(n) => *val += n,
                    Message::Reset => *val = 0,
                }
            }
        });

        Self {
            sender,
            state,
            handle: Some(handle),
        }
    }

    fn send(&self, msg: Message) {
        self.sender.send(msg).unwrap();
    }

    fn stop(&mut self) {
        drop(self.sender.clone());
        // Drop the original sender by replacing it
        let (dummy, _) = mpsc::channel();
        let _ = std::mem::replace(&mut self.sender, dummy);
        if let Some(h) = self.handle.take() {
            h.join().unwrap();
        }
    }

    fn state(&self) -> i64 {
        *self.state.lock().unwrap()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_actor_processes_messages() {
        let mut a = Actor::new();
        a.send(Message::Add(10));
        a.send(Message::Add(20));
        a.stop();

        assert_eq!(a.state(), 30);
    }

    #[test]
    fn test_actor_reset() {
        let mut a = Actor::new();
        a.send(Message::Add(100));
        a.send(Message::Reset);
        a.send(Message::Add(5));
        a.stop();

        assert_eq!(a.state(), 5);
    }

    #[test]
    fn test_actor_concurrent_senders() {
        let mut a = Actor::new();
        let sender = a.sender.clone();

        let handles: Vec<_> = (0..100)
            .map(|_| {
                let s = sender.clone();
                thread::spawn(move || {
                    s.send(Message::Add(1)).unwrap();
                })
            })
            .collect();

        for h in handles {
            h.join().unwrap();
        }
        drop(sender);
        a.stop();

        assert_eq!(a.state(), 100);
    }
}
