"""Cooperative Scheduling — round-robin task interleaving with voluntary yielding."""

from typing import Callable


class Scheduler:
    def __init__(self):
        self._tasks: list[tuple[str, list[Callable[[], str]]]] = []  # TODO: implement

    def add_task(self, name: str, steps: list[Callable[[], str]]) -> None:
        self._tasks.append((name, steps))  # TODO: implement

    def run(self) -> list[str]:
        results: list[str] = []  # TODO: implement
        cursors = [0] * len(self._tasks)

        while True:
            progress = False
            for i, (_, steps) in enumerate(self._tasks):
                if cursors[i] < len(steps):
                    result = steps[cursors[i]]()
                    results.append(result)
                    cursors[i] += 1
                    progress = True
            if not progress:
                break

        return results


# ─── Tests (do not modify below this line) ───


def test_coop_scheduler_interleaving():
    s = Scheduler()
    s.add_task("A", [lambda: "A1", lambda: "A2"])
    s.add_task("B", [lambda: "B1", lambda: "B2"])

    results = s.run()
    assert results == ["A1", "B1", "A2", "B2"]


def test_coop_scheduler_unequal_steps():
    s = Scheduler()
    s.add_task("A", [lambda: "A1", lambda: "A2", lambda: "A3"])
    s.add_task("B", [lambda: "B1"])

    results = s.run()
    assert len(results) == 4
    assert results[0] == "A1"
    assert results[1] == "B1"


def test_coop_scheduler_empty():
    s = Scheduler()
    results = s.run()
    assert results == []
