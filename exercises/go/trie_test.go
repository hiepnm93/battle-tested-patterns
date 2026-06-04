package exercises

import (
	"sort"
	"testing"
)

type TrieNode struct {
	children map[byte]*TrieNode
	isEnd    bool
}

type Trie struct {
	root *TrieNode
}

func NewTrie() *Trie {
	return &Trie{root: &TrieNode{children: make(map[byte]*TrieNode)}}
}

func (t *Trie) Insert(word string) {
	node := t.root
	for i := 0; i < len(word); i++ {
		ch := word[i]
		if node.children[ch] == nil {
			node.children[ch] = &TrieNode{children: make(map[byte]*TrieNode)}
		}
		node = node.children[ch]
	}
	node.isEnd = true
}

func (t *Trie) Search(word string) bool {
	node := t.root
	for i := 0; i < len(word); i++ {
		child, ok := node.children[word[i]]
		if !ok {
			return false
		}
		node = child
	}
	return node.isEnd
}

func (t *Trie) StartsWith(prefix string) bool {
	node := t.root
	for i := 0; i < len(prefix); i++ {
		child, ok := node.children[prefix[i]]
		if !ok {
			return false
		}
		node = child
	}
	return true
}

func (t *Trie) collectWords(node *TrieNode, prefix string, results *[]string) {
	if node.isEnd {
		*results = append(*results, prefix)
	}
	for ch, child := range node.children {
		t.collectWords(child, prefix+string(ch), results)
	}
}

func (t *Trie) AutoComplete(prefix string) []string {
	node := t.root
	for i := 0; i < len(prefix); i++ {
		child, ok := node.children[prefix[i]]
		if !ok {
			return nil
		}
		node = child
	}
	var results []string
	t.collectWords(node, prefix, &results)
	sort.Strings(results)
	return results
}

func TestTrieInsertAndSearch(t *testing.T) {
	trie := NewTrie()
	trie.Insert("apple")
	trie.Insert("app")

	if !trie.Search("apple") {
		t.Error("should find apple")
	}
	if !trie.Search("app") {
		t.Error("should find app")
	}
	if trie.Search("ap") {
		t.Error("should not find ap (not inserted as complete word)")
	}
}

func TestTrieStartsWith(t *testing.T) {
	trie := NewTrie()
	trie.Insert("hello")

	if !trie.StartsWith("hel") {
		t.Error("should find prefix hel")
	}
	if trie.StartsWith("world") {
		t.Error("should not find prefix world")
	}
}

func TestTrieAutoComplete(t *testing.T) {
	trie := NewTrie()
	trie.Insert("car")
	trie.Insert("card")
	trie.Insert("care")
	trie.Insert("careful")
	trie.Insert("dog")

	results := trie.AutoComplete("car")
	want := []string{"car", "card", "care", "careful"}
	if len(results) != len(want) {
		t.Fatalf("AutoComplete(car) = %v, want %v", results, want)
	}
	for i, v := range results {
		if v != want[i] {
			t.Errorf("results[%d] = %q, want %q", i, v, want[i])
		}
	}
}

func TestTrieEmpty(t *testing.T) {
	trie := NewTrie()
	if trie.Search("anything") {
		t.Error("empty trie should find nothing")
	}
}
