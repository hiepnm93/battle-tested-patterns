package answers

// Op represents a diff operation.
type OpType int

const (
	OpKeep OpType = iota
	OpInsert
	OpDelete
)

type DiffOp[T comparable] struct {
	Type  OpType
	Value T
}

// Diff computes the operations needed to transform old into new.
func Diff[T comparable](old, new []T) []DiffOp[T] {
	var ops []DiffOp[T]
	oi, ni := 0, 0

	for oi < len(old) && ni < len(new) {
		if old[oi] == new[ni] {
			ops = append(ops, DiffOp[T]{Type: OpKeep, Value: old[oi]})
			oi++
			ni++
		} else if !contains(new[ni:], old[oi]) {
			ops = append(ops, DiffOp[T]{Type: OpDelete, Value: old[oi]})
			oi++
		} else {
			ops = append(ops, DiffOp[T]{Type: OpInsert, Value: new[ni]})
			ni++
		}
	}

	for oi < len(old) {
		ops = append(ops, DiffOp[T]{Type: OpDelete, Value: old[oi]})
		oi++
	}
	for ni < len(new) {
		ops = append(ops, DiffOp[T]{Type: OpInsert, Value: new[ni]})
		ni++
	}

	return ops
}

// Patch applies diff operations to produce the new list.
func Patch[T comparable](ops []DiffOp[T]) []T {
	var result []T
	for _, op := range ops {
		if op.Type == OpKeep || op.Type == OpInsert {
			result = append(result, op.Value)
		}
	}
	return result
}

func contains[T comparable](slice []T, item T) bool {
	for _, v := range slice {
		if v == item {
			return true
		}
	}
	return false
}
