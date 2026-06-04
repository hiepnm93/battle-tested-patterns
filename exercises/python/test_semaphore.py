"""Semaphore — limit concurrent access with acquire/release."""

import threading
import time


class Semaphore:
    def __init__(self, permits: int):
        self._permits = permits  # TODO: implement
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)

    def acquire(self) -> None:
        with self._condition:  # TODO: implement
            while self._permits <= 0:
                self._condition.wait()
            self._permits -= 1

    def release(self) -> None:
        with self._condition:  # TODO: implement
            self._permits += 1
            self._condition.notify()

    @property
    def available(self) -> int:
        with self._lock:
            return self._permits


# ─── Tests (do not modify below this line) ───


def test_semaphore_acquire_release():
    sem = Semaphore(2)
    sem.acquire()
    sem.acquire()
    sem.release()
    sem.acquire()  # should not block


def test_semaphore_limits_concurrency():
    sem = Semaphore(2)
    max_concurrent = 0
    current = 0
    lock = threading.Lock()

    def worker():
        nonlocal max_concurrent, current
        sem.acquire()
        with lock:
            current += 1
            if current > max_concurrent:
                max_concurrent = current
        time.sleep(0.001)
        with lock:
            current -= 1
        sem.release()

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert max_concurrent <= 2, \
        f"max concurrent {max_concurrent} exceeded semaphore limit 2"


def test_semaphore_available():
    sem = Semaphore(3)
    assert sem.available == 3
    sem.acquire()
    assert sem.available == 2
    sem.release()
    assert sem.available == 3
