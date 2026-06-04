"""State Machine pattern — explicit states and transitions."""


class StateMachine:  # TODO: implement
    def __init__(self, config: dict, initial: str):
        self._config = config
        self._current = initial

    @property
    def state(self) -> str:  # TODO: implement
        return self._current

    def send(self, event: str) -> str:  # TODO: implement
        transitions = self._config.get(self._current, {}).get("on", {})
        if event in transitions:
            self._current = transitions[event]
        return self._current

    def can(self, event: str) -> bool:  # TODO: implement
        return event in self._config.get(self._current, {}).get("on", {})


# ─── Tests (do not modify below this line) ───


def _approval_machine() -> StateMachine:
    return StateMachine(
        {
            "idle": {"on": {"submit": "pending"}},
            "pending": {"on": {"approve": "approved", "reject": "rejected"}},
            "rejected": {"on": {"resubmit": "pending"}},
            "approved": {"on": {}},
        },
        initial="idle",
    )


def test_happy_path():
    sm = _approval_machine()
    sm.send("submit")
    assert sm.state == "pending"
    sm.send("approve")
    assert sm.state == "approved"


def test_invalid_transition():
    sm = _approval_machine()
    sm.send("approve")  # invalid from idle
    assert sm.state == "idle", "Invalid transition should keep current state"


def test_resubmit():
    sm = _approval_machine()
    sm.send("submit")
    sm.send("reject")
    assert sm.state == "rejected"
    sm.send("resubmit")
    assert sm.state == "pending"


def test_can():
    sm = _approval_machine()
    assert sm.can("submit")
    assert not sm.can("approve")

    sm.send("submit")
    assert sm.can("approve")
    assert sm.can("reject")
    assert not sm.can("submit")


def test_traffic_light():
    sm = StateMachine(
        {
            "green": {"on": {"TIMER": "yellow"}},
            "yellow": {"on": {"TIMER": "red"}},
            "red": {"on": {"TIMER": "green"}},
        },
        initial="green",
    )
    sm.send("TIMER")
    assert sm.state == "yellow"
    sm.send("TIMER")
    assert sm.state == "red"
    sm.send("TIMER")
    assert sm.state == "green"


def test_no_transition_defined():
    sm = StateMachine(
        {"only": {"on": {}}},
        initial="only",
    )
    sm.send("anything")
    assert sm.state == "only", "Unknown events should be silently ignored"
