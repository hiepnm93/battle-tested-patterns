from typing import Callable

class EventLoop:
    def __init__(self) -> None:
        self._handlers: dict[int, Callable[[], None]] = {}

    def add_handler(self, fd: int, callback: Callable[[], None]) -> None:
        self._handlers[fd] = callback

    def remove_handler(self, fd: int) -> None:
        self._handlers.pop(fd, None)

    def tick(self) -> int:
        count = len(self._handlers)
        for handler in list(self._handlers.values()):
            handler()
        return count

    def run(self, max_ticks: int) -> int:
        ticks_run = 0
        for _ in range(max_ticks):
            if not self._handlers:
                break
            self.tick()
            ticks_run += 1
        return ticks_run
