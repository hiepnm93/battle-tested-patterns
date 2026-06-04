import hashlib

def sha256_hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

class MerkleTree:
    def __init__(self, data: list[str]):
        self._leaves = [sha256_hash(d) for d in data]
        self._layers: list[list[str]] = [self._leaves[:]]
        self._build_tree()

    def _build_tree(self) -> None:
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
    def root(self) -> str:
        return self._layers[-1][0]

    def get_proof(self, index: int) -> list[dict[str, str]]:
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
    def verify(leaf: str, proof: list[dict[str, str]], root: str) -> bool:
        current = sha256_hash(leaf)
        for step in proof:
            if step["position"] == "left":
                current = sha256_hash(step["hash"] + current)
            else:
                current = sha256_hash(current + step["hash"])
        return current == root
