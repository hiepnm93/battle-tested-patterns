class LamportClock:
    def __init__(self) -> None:
        self._time = 0

    def tick(self) -> None:
        self._time += 1

    def send(self) -> int:
        self._time += 1
        return self._time

    def receive(self, remote_timestamp: int) -> None:
        self._time = max(self._time, remote_timestamp) + 1

    def now(self) -> int:
        return self._time
