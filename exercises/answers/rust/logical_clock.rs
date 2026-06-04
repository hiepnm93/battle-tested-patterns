use std::sync::atomic::{AtomicU64, Ordering};

pub struct LamportClock {
    time: AtomicU64,
}

impl LamportClock {
    pub fn new() -> Self {
        LamportClock { time: AtomicU64::new(0) }
    }

    pub fn tick(&self) -> u64 {
        self.time.fetch_add(1, Ordering::SeqCst) + 1
    }

    pub fn send(&self) -> u64 {
        self.tick()
    }

    pub fn receive(&self, remote: u64) -> u64 {
        loop {
            let current = self.time.load(Ordering::SeqCst);
            let new_time = std::cmp::max(current, remote) + 1;
            if self.time.compare_exchange(
                current, new_time, Ordering::SeqCst, Ordering::SeqCst
            ).is_ok() {
                return new_time;
            }
        }
    }

    pub fn now(&self) -> u64 {
        self.time.load(Ordering::SeqCst)
    }
}
