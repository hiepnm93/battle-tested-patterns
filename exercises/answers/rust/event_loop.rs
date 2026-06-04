use std::collections::HashMap;

pub struct EventLoop {
    handlers: HashMap<i32, Box<dyn FnMut()>>,
}

impl EventLoop {
    pub fn new() -> Self {
        EventLoop { handlers: HashMap::new() }
    }

    pub fn add_handler(&mut self, fd: i32, handler: impl FnMut() + 'static) {
        self.handlers.insert(fd, Box::new(handler));
    }

    pub fn remove_handler(&mut self, fd: i32) {
        self.handlers.remove(&fd);
    }

    pub fn tick(&mut self) -> usize {
        let count = self.handlers.len();
        for handler in self.handlers.values_mut() {
            handler();
        }
        count
    }

    pub fn run(&mut self, max_ticks: usize) -> usize {
        let mut ticks_run = 0;
        for _ in 0..max_ticks {
            if self.handlers.is_empty() {
                break;
            }
            self.tick();
            ticks_run += 1;
        }
        ticks_run
    }
}
