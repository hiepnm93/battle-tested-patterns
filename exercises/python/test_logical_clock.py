"""Logical Clock / Lamport Clock pattern — causal event ordering without wall-clock time."""


class LamportClock:  # TODO: implement
    def __init__(self) -> None:
        self._time = 0

    def tick(self) -> None:  # TODO: implement
        self._time += 1

    def send(self) -> int:  # TODO: implement
        self._time += 1
        return self._time

    def receive(self, remote_timestamp: int) -> None:  # TODO: implement
        self._time = max(self._time, remote_timestamp) + 1

    def now(self) -> int:  # TODO: implement
        return self._time


# ─── Tests (do not modify below this line) ───


def test_tick():
    c = LamportClock()
    c.tick()
    t1 = c.now()
    c.tick()
    t2 = c.now()
    assert t2 > t1, "Each tick should increase the clock"


def test_send_receive():
    a = LamportClock()
    b = LamportClock()

    a.tick()
    a.tick()
    msg_time = a.send()

    b.receive(msg_time)
    assert b.now() > msg_time, "Receive should produce time > message time"


def test_causality():
    a = LamportClock()
    b = LamportClock()

    a.tick()  # a=1
    a.tick()  # a=2
    a.tick()  # a=3

    b.tick()  # b=1

    msg = a.send()       # a=4, msg=4
    b.receive(msg)       # b=max(1,4)+1=5

    assert b.now() > msg, f"recv({b.now()}) should be > msg({msg})"


def test_monotonic():
    c = LamportClock()
    prev = c.now()
    for _ in range(100):
        c.tick()
        curr = c.now()
        assert curr > prev, "Clock should be monotonically increasing"
        prev = curr


def test_receive_from_behind():
    """When receiving from a clock behind us, our clock still advances."""
    a = LamportClock()
    a.tick()
    a.tick()
    a.tick()  # a=3

    before = a.now()
    a.receive(1)  # remote is behind
    assert a.now() > before, "Should still advance even when remote is behind"
    assert a.now() == 4  # max(3, 1) + 1 = 4
