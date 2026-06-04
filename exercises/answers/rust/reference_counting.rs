use std::cell::Cell;

struct RcInner<T> {
    value: T,
    count: Cell<usize>,
}

pub struct Rc<T> {
    inner: *const RcInner<T>,
}

impl<T> Rc<T> {
    pub fn new(value: T) -> Self {
        let inner = Box::into_raw(Box::new(RcInner {
            value,
            count: Cell::new(1),
        }));
        Rc { inner }
    }

    pub fn strong_count(&self) -> usize {
        unsafe { (*self.inner).count.get() }
    }

    pub fn value(&self) -> &T {
        unsafe { &(*self.inner).value }
    }
}

impl<T> Clone for Rc<T> {
    fn clone(&self) -> Self {
        unsafe {
            let c = (*self.inner).count.get();
            (*self.inner).count.set(c + 1);
        }
        Rc { inner: self.inner }
    }
}

impl<T> Drop for Rc<T> {
    fn drop(&mut self) {
        unsafe {
            let c = (*self.inner).count.get();
            (*self.inner).count.set(c - 1);
            if c == 1 {
                drop(Box::from_raw(self.inner as *mut RcInner<T>));
            }
        }
    }
}
