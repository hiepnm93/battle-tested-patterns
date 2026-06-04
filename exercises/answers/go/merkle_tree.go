package answers

import (
	"crypto/sha256"
	"encoding/hex"
)

func hashStr(data string) string {
	h := sha256.Sum256([]byte(data))
	return hex.EncodeToString(h[:])
}

type ProofStep struct {
	Hash     string
	Position string // "left" or "right"
}

type MerkleTree struct {
	layers [][]string
}

func NewMerkleTree(data []string) *MerkleTree {
	leaves := make([]string, len(data))
	for i, d := range data {
		leaves[i] = hashStr(d)
	}
	t := &MerkleTree{layers: [][]string{leaves}}
	t.buildTree()
	return t
}

func (t *MerkleTree) buildTree() {
	current := t.layers[0]
	for len(current) > 1 {
		next := make([]string, 0, (len(current)+1)/2)
		for i := 0; i < len(current); i += 2 {
			left := current[i]
			right := left
			if i+1 < len(current) {
				right = current[i+1]
			}
			next = append(next, hashStr(left+right))
		}
		t.layers = append(t.layers, next)
		current = next
	}
}

func (t *MerkleTree) Root() string {
	top := t.layers[len(t.layers)-1]
	return top[0]
}

func (t *MerkleTree) GetProof(index int) []ProofStep {
	var proof []ProofStep
	idx := index
	for i := 0; i < len(t.layers)-1; i++ {
		layer := t.layers[i]
		isRight := idx%2 == 1
		siblingIdx := idx + 1
		if isRight {
			siblingIdx = idx - 1
		}
		if siblingIdx < len(layer) {
			pos := "right"
			if isRight {
				pos = "left"
			}
			proof = append(proof, ProofStep{Hash: layer[siblingIdx], Position: pos})
		} else {
			proof = append(proof, ProofStep{Hash: layer[idx], Position: "right"})
		}
		idx = idx / 2
	}
	return proof
}

func Verify(leaf string, proof []ProofStep, root string) bool {
	current := hashStr(leaf)
	for _, step := range proof {
		if step.Position == "left" {
			current = hashStr(step.Hash + current)
		} else {
			current = hashStr(current + step.Hash)
		}
	}
	return current == root
}
