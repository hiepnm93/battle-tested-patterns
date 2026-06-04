"""Dependency Graph pattern — topological sort with cycle detection."""
from collections import deque


class DependencyGraph:  # TODO: implement
    def __init__(self):
        self.adj: dict[str, list[str]] = {}

    def add_node(self, node: str) -> None:  # TODO: implement
        if node not in self.adj:
            self.adj[node] = []

    def add_edge(self, from_node: str, to_node: str) -> None:  # TODO: implement
        self.add_node(from_node)
        self.add_node(to_node)
        self.adj[from_node].append(to_node)

    def topological_sort(self) -> list[str]:  # TODO: implement
        in_degree: dict[str, int] = {n: 0 for n in self.adj}
        for deps in self.adj.values():
            for dep in deps:
                in_degree[dep] = in_degree.get(dep, 0) + 1

        queue = deque(n for n, d in in_degree.items() if d == 0)
        result: list[str] = []

        while queue:
            node = queue.popleft()
            result.append(node)
            for dep in self.adj.get(node, []):
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)

        if len(result) != len(self.adj):
            raise ValueError("Cycle detected")
        return result


# ─── Tests (do not modify below this line) ───


def test_topological_sort():
    g = DependencyGraph()
    # add_edge(from, to) means "from must come before to"
    g.add_edge("logger", "router")
    g.add_edge("logger", "db")
    g.add_edge("router", "app")
    g.add_edge("db", "app")

    order = g.topological_sort()
    pos = {n: i for i, n in enumerate(order)}
    assert pos["logger"] < pos["router"]
    assert pos["logger"] < pos["db"]
    assert pos["router"] < pos["app"]
    assert pos["db"] < pos["app"]


def test_cycle_detection():
    g = DependencyGraph()
    g.add_edge("a", "b")
    g.add_edge("b", "c")
    g.add_edge("c", "a")

    try:
        g.topological_sort()
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_single_node_self_cycle():
    g = DependencyGraph()
    g.add_edge("solo", "solo")

    try:
        g.topological_sort()
        assert False, "Should detect self-cycle"
    except ValueError:
        pass


def test_linear_chain():
    g = DependencyGraph()
    g.add_edge("a", "b")
    g.add_edge("b", "c")
    g.add_edge("c", "d")

    order = g.topological_sort()
    assert order.index("a") < order.index("b")
    assert order.index("b") < order.index("c")
    assert order.index("c") < order.index("d")


def test_diamond_dependency():
    g = DependencyGraph()
    g.add_edge("a", "b")
    g.add_edge("a", "c")
    g.add_edge("b", "d")
    g.add_edge("c", "d")

    order = g.topological_sort()
    pos = {n: i for i, n in enumerate(order)}
    assert pos["a"] < pos["b"]
    assert pos["a"] < pos["c"]
    assert pos["b"] < pos["d"]
    assert pos["c"] < pos["d"]
