# Pattern: Merkle Tree
# Difficulty: Intermediate

import hashlib


def sha256_hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


class MerkleTree:
    def __init__(self, data: list[str]):  # TODO: implement
        self._leaves = [sha256_hash(d) for d in data]
        self._layers: list[list[str]] = [self._leaves[:]]
        self._build_tree()

    def _build_tree(self) -> None:  # TODO: implement
        current = self._leaves
        while len(current) > 1:
            next_layer: list[str] = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if i + 1 < len(current) else left
                next_layer.append(sha256_hash(left + right))
            self._layers.append(next_layer)
            current = next_layer

    @property
    def root(self) -> str:  # TODO: implement
        return self._layers[-1][0]

    @property
    def leaf_count(self) -> int:
        return len(self._leaves)

    def get_proof(self, index: int) -> list[dict[str, str]]:  # TODO: implement
        proof: list[dict[str, str]] = []
        idx = index
        for i in range(len(self._layers) - 1):
            layer = self._layers[i]
            is_right = idx % 2 == 1
            sibling_idx = idx - 1 if is_right else idx + 1
            if sibling_idx < len(layer):
                pos = "left" if is_right else "right"
                proof.append({"hash": layer[sibling_idx], "position": pos})
            else:
                proof.append({"hash": layer[idx], "position": "right"})
            idx = idx // 2
        return proof

    @staticmethod
    def verify(leaf: str, proof: list[dict[str, str]], root: str) -> bool:  # TODO: implement
        current = sha256_hash(leaf)
        for step in proof:
            if step["position"] == "left":
                current = sha256_hash(step["hash"] + current)
            else:
                current = sha256_hash(current + step["hash"])
        return current == root


# ─── Tests (do not modify below this line) ───

def test_root_hash():
    tree = MerkleTree(["a", "b", "c", "d"])
    assert tree.root != ""
    assert tree.leaf_count == 4

def test_deterministic():
    t1 = MerkleTree(["x", "y", "z"])
    t2 = MerkleTree(["x", "y", "z"])
    assert t1.root == t2.root

def test_change_sensitivity():
    t1 = MerkleTree(["a", "b", "c"])
    t2 = MerkleTree(["a", "b", "d"])
    assert t1.root != t2.root

def test_single_element():
    tree = MerkleTree(["only"])
    expected = sha256_hash("only")
    assert tree.root == expected

def test_verify_proof():
    tree = MerkleTree(["a", "b", "c", "d"])
    proof = tree.get_proof(0)
    assert MerkleTree.verify("a", proof, tree.root)

def test_verify_detects_tampering():
    tree = MerkleTree(["a", "b", "c", "d"])
    proof = tree.get_proof(0)
    assert not MerkleTree.verify("z", proof, tree.root)
