package exercises

import (
	"errors"
	"testing"
)

type DepGraph struct {
	edges map[string][]string
}

func NewDepGraph() *DepGraph {
	return &DepGraph{edges: make(map[string][]string)}
}

func (g *DepGraph) AddDep(node, dep string) {
	g.edges[node] = append(g.edges[node], dep)
	if _, ok := g.edges[dep]; !ok {
		g.edges[dep] = nil
	}
}

func (g *DepGraph) TopoSort() ([]string, error) {
	visited := make(map[string]int) // 0=unvisited, 1=visiting, 2=done
	var result []string

	var visit func(string) error
	visit = func(node string) error {
		if visited[node] == 1 {
			return errors.New("cycle detected")
		}
		if visited[node] == 2 {
			return nil
		}
		visited[node] = 1
		for _, dep := range g.edges[node] {
			if err := visit(dep); err != nil {
				return err
			}
		}
		visited[node] = 2
		result = append(result, node)
		return nil
	}

	for node := range g.edges {
		if err := visit(node); err != nil {
			return nil, err
		}
	}
	return result, nil
}

func TestDepGraphTopoSort(t *testing.T) {
	g := NewDepGraph()
	g.AddDep("app", "router")
	g.AddDep("app", "db")
	g.AddDep("router", "logger")
	g.AddDep("db", "logger")

	order, err := g.TopoSort()
	if err != nil {
		t.Fatal(err)
	}

	pos := make(map[string]int)
	for i, n := range order {
		pos[n] = i
	}
	if pos["logger"] > pos["router"] || pos["logger"] > pos["db"] {
		t.Error("logger should come before router and db")
	}
	if pos["router"] > pos["app"] || pos["db"] > pos["app"] {
		t.Error("router and db should come before app")
	}
}

func TestDepGraphCycleDetection(t *testing.T) {
	g := NewDepGraph()
	g.AddDep("a", "b")
	g.AddDep("b", "c")
	g.AddDep("c", "a")

	_, err := g.TopoSort()
	if err == nil {
		t.Error("should detect cycle")
	}
}

func TestDepGraphSingleNode(t *testing.T) {
	g := NewDepGraph()
	g.AddDep("solo", "solo") // self-cycle

	_, err := g.TopoSort()
	if err == nil {
		t.Error("self-cycle should be detected")
	}
}
