---
title: "Pattern: Merkle Tree"
description: "Hash lá, rồi hash các cặp lên trên tới root — xác minh toàn vẹn lá nào trong O(log n) không cần re-hash toàn bộ dataset."
difficulty: "advanced"
---

# Pattern: Merkle Tree

<DifficultyBadge />

## Mô tả một câu

Hash lá, rồi hash các cặp lên trên tới root — xác minh toàn vẹn lá nào trong O(log n) không cần re-hash toàn bộ dataset.

<DemoBadge />

## Tương tự thực tế

Hệ thống niêm phong vận chuyển bằng chứng giả mạo. Mỗi hộp nhận niêm phong sáp duy nhất. Hộp gom thành thùng, mỗi thùng niêm phong bằng dấu lấy từ tất cả niêm phong hộp. Thùng vào container với niêm phong tổng riêng. Nếu một item bị tráo, mọi niêm phong phía trên nó vỡ — và bạn có thể tìm hộp bị làm giả bằng cách check chỉ log(n) niêm phong thay vì mở mọi hộp.

## Ý tưởng cốt lõi

Merkle tree là cây nhị phân các hash. Mỗi node lá chứa hash của một block dữ liệu. Mỗi node nội bộ chứa hash của hai con nối lại. Root hash là dấu vân tay của toàn bộ dataset. Để xác minh một lá, bạn chỉ cần "đường bằng chứng" — các hash anh em dọc đường từ lá tới root — cho xác minh O(log n).

```text
                    Root Hash
                   H(H12 + H34)
                  /             \
              H12                H34
           H(H1+H2)          H(H3+H4)
            /    \             /    \
          H1      H2        H3      H4
          |       |         |       |
        Data A  Data B    Data C  Data D

  Xác minh Data C:
  ┌──────────────────────────────────────┐
  │ Cần: H4 (anh em), H12 (chú)         │
  │ Tính: H3 = hash(Data C)             │
  │       H34 = hash(H3 + H4)           │
  │       root = hash(H12 + H34)        │
  │ So: root == root đã biết? ✓         │
  └──────────────────────────────────────┘
```

| Thuộc tính | Giá trị |
|----------|-------|
| Chi phí xác minh | O(log n) hash mỗi lá |
| Xây cây | O(n) hash |
| Bộ nhớ cho bằng chứng | O(log n) hash anh em |
| Phát hiện giả mạo | Bất kỳ thay đổi nào lật root hash |

**Thử ngay** — xác minh toàn vẹn lá bằng cách lần theo đường bằng chứng, hoặc làm giả dữ liệu để xem root hash đổi:

<MerkleTreeViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| Git | [tree.c#L136-L171](https://github.com/git/git/blob/1ff279f3404a482a83fb04c7457e41ab26884aea/tree.c#L136-L171) | `parse_tree_gently` parse object tree, mỗi cái lưu hash của blob/tree con. Mô hình object Git là Merkle DAG — mọi commit, tree và blob được địa chỉ-theo-nội-dung bằng SHA-1. Đổi một byte trong file nào đổi mọi hash lên tới commit root. Điều này cho phép diff, fetch (chỉ chuyển object thiếu) và xác minh toàn vẹn hiệu quả với `git fsck`. |
| ZFS | [blkptr.c (OpenZFS)](https://github.com/openzfs/zfs/blob/7e054b2e7ea80c7c838f7fd44b7d517eea5c9d18/module/zfs/blkptr.c#L30-L77) | `blkptr_verify` xác minh checksum block pointer. Mọi block trong ZFS lưu checksum nội dung trong con trỏ của block cha — tạo Merkle tree từ block dữ liệu lên uberblock. Cấu trúc tự-xác-minh này phát hiện hư dữ liệu âm thầm (bit rot) không cần database toàn vẹn riêng. Command `zpool scrub` đi qua cây này để xác minh mọi block. |

## Triển khai

::: code-group

```typescript [TypeScript]
function hash(data: string): string {
  let h = 0x811c9dc5;
  for (let i = 0; i < data.length; i++) {
    h ^= data.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return (h >>> 0).toString(16).padStart(8, '0');
}

class MerkleTree {
  private leaves: string[];
  private layers: string[][];

  constructor(data: string[]) {
    this.leaves = data.map((d) => hash(d));
    this.layers = [this.leaves];
    this.buildTree();
  }

  private buildTree(): void {
    let current = this.leaves;
    while (current.length > 1) {
      const next: string[] = [];
      for (let i = 0; i < current.length; i += 2) {
        const left = current[i]!;
        const right = current[i + 1] ?? left; // nhân đôi cái cuối nếu lẻ
        next.push(hash(left + right));
      }
      this.layers.push(next);
      current = next;
    }
  }

  get root(): string {
    return this.layers[this.layers.length - 1]![0]!;
  }

  getProof(index: number): Array<{ hash: string; position: 'left' | 'right' }> {
    const proof: Array<{ hash: string; position: 'left' | 'right' }> = [];
    let idx = index;
    for (let i = 0; i < this.layers.length - 1; i++) {
      const layer = this.layers[i]!;
      const isRight = idx % 2 === 1;
      const siblingIdx = isRight ? idx - 1 : idx + 1;
      if (siblingIdx < layer.length) {
        proof.push({
          hash: layer[siblingIdx]!,
          position: isRight ? 'left' : 'right',
        });
      } else {
        proof.push({ hash: layer[idx]!, position: 'right' });
      }
      idx = Math.floor(idx / 2);
    }
    return proof;
  }

  static verify(
    leaf: string,
    proof: Array<{ hash: string; position: 'left' | 'right' }>,
    root: string,
  ): boolean {
    let current = hash(leaf);
    for (const step of proof) {
      if (step.position === 'left') {
        current = hash(step.hash + current);
      } else {
        current = hash(current + step.hash);
      }
    }
    return current === root;
  }
}
```

```rust [Rust]
fn hash_str(data: &str) -> String {
    let mut h: u64 = 0xcbf29ce484222325;
    for b in data.bytes() {
        h ^= b as u64;
        h = h.wrapping_mul(0x100000001b3);
    }
    format!("{:016x}", h)
}

pub struct ProofStep {
    pub hash: String,
    pub position: String, // "left" hoặc "right"
}

pub struct MerkleTree {
    layers: Vec<Vec<String>>,
}

impl MerkleTree {
    pub fn new(data: &[&str]) -> Self {
        let leaves: Vec<String> = data.iter().map(|d| hash_str(d)).collect();
        let mut tree = MerkleTree { layers: vec![leaves] };
        tree.build_tree();
        tree
    }

    fn build_tree(&mut self) {
        let mut current = self.layers[0].clone();
        while current.len() > 1 {
            let mut next = Vec::new();
            for i in (0..current.len()).step_by(2) {
                let left = &current[i];
                let right = if i + 1 < current.len() { &current[i + 1] } else { left };
                next.push(hash_str(&format!("{}{}", left, right)));
            }
            self.layers.push(next.clone());
            current = next;
        }
    }

    pub fn root(&self) -> &str {
        &self.layers.last().unwrap()[0]
    }

    pub fn get_proof(&self, index: usize) -> Vec<ProofStep> {
        let mut proof = Vec::new();
        let mut idx = index;
        for i in 0..self.layers.len() - 1 {
            let layer = &self.layers[i];
            let is_right = idx % 2 == 1;
            let sibling_idx = if is_right { idx - 1 } else { idx + 1 };
            if sibling_idx < layer.len() {
                let pos = if is_right { "left" } else { "right" };
                proof.push(ProofStep {
                    hash: layer[sibling_idx].clone(),
                    position: pos.to_string(),
                });
            } else {
                proof.push(ProofStep {
                    hash: layer[idx].clone(),
                    position: "right".to_string(),
                });
            }
            idx /= 2;
        }
        proof
    }

    pub fn verify(leaf: &str, proof: &[ProofStep], root: &str) -> bool {
        let mut current = hash_str(leaf);
        for step in proof {
            if step.position == "left" {
                current = hash_str(&format!("{}{}", step.hash, current));
            } else {
                current = hash_str(&format!("{}{}", current, step.hash));
            }
        }
        current == root
    }
}
```

```go [Go]
package merkle

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
	Position string // "left" hoặc "right"
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
```

```python [Python]
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
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Xây Merkle tree, lấy root hash, sinh và xác minh bằng chứng | `exercises/typescript/merkle-tree/01-basic.test.ts` |
| Trung bình | Phát hiện lá bị giả mạo và sinh đường bằng chứng tối thiểu | `exercises/typescript/merkle-tree/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/merkle_tree/mod.rs` · Go `exercises/go/merkle_tree/merkle_tree_test.go` · Python `exercises/python/merkle_tree/test_merkle_tree.py`

## Khi nào nên dùng

- **Version control** — lưu trữ địa chỉ-theo-nội-dung nơi mọi thay đổi đều phát hiện được (Git)
- **Blockchain** — xác minh giao dịch không cần tải toàn chuỗi (Bitcoin SPV)
- **Filesystem** — phát hiện hư dữ liệu âm thầm (ZFS, Btrfs)
- **Peer-to-peer** — xác minh chunk tải về từ peer không tin cậy (BitTorrent, IPFS)
- **Minh bạch chứng chỉ** — log Merkle append-only của chứng chỉ TLS

## Khi nào KHÔNG nên dùng

- **Dataset nhỏ** — nếu có thể hash mọi thứ một lần, Merkle tree thêm phức tạp không cần
- **Dữ liệu đổi thường xuyên** — mỗi mutation cần O(log n) re-hash lên root
- **Bối cảnh không-xác-minh-được** — nếu bạn tin nguồn dữ liệu hoàn toàn, bằng chứng toàn vẹn là việc phí
- **Mẫu truy cập có thứ tự** — Merkle tree không phải cây tìm kiếm; dùng B+ tree cho truy vấn khoảng

## Thêm các ứng dụng production

- [Bitcoin](https://github.com/bitcoin/bitcoin) — header block chứa Merkle root mọi transaction
- [Ethereum](https://github.com/ethereum/go-ethereum) — Patricia Merkle Trie cho state, transaction và receipt
- [IPFS](https://github.com/ipfs/kubo) — Merkle DAG địa chỉ-theo-nội-dung cho lưu trữ file phân tán
- [Certificate Transparency](https://certificate.transparency.dev/) — log Merkle tree cho audit chứng chỉ TLS

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Copy-on-Write (CoW)](/patterns/copy-on-write/) | Merkle tree cho copy-on-write hiệu quả — chỉ re-hash đường đã đổi |
| [Write-Ahead Log (WAL)](/patterns/write-ahead-log/) | WAL ghi thay đổi; Merkle tree xác minh state kết quả nhất quán |
| [Checkpointing](/patterns/checkpointing/) | Root Merkle phục vụ bằng chứng toàn vẹn cho snapshot checkpoint |
| [B+ Tree](/patterns/b-plus-tree/) | Cả hai là cấu trúc cây — Merkle cho xác minh, B+ cho truy cập có thứ tự |
| [Diff & Patch](/patterns/diff-patch/) | Merkle tree cho phát hiện diff hiệu quả — chỉ re-hash đường tới node đã đổi |

## Câu hỏi thử thách

::: details Câu 1: Merkle tree của bạn có 1 triệu lá. Client muốn xác minh rằng lá #500.000 là xác thực. Client cần nhận và tính bao nhiêu hash?
**Trả lời:** Khoảng 20 hash (log2(1.000.000) ~ 20). Client nhận ~20 hash anh em (đường bằng chứng) và tính ~20 thao tác hash để đi từ lá tới root.

Đây là giá trị cốt lõi của Merkle tree: chi phí xác minh logarit theo size dataset. Client cần dữ liệu lá, đường bằng chứng (một hash anh em mỗi tầng cây) và root hash đã biết. Cho 1 triệu lá, đó là khoảng 20 × 32 byte = 640 byte dữ liệu bằng chứng — không đáng kể so với tải lại và hash cả 1 triệu lá.
:::

::: details Câu 2: Git dùng SHA-1 cho Merkle DAG. Nếu bạn đổi một ký tự trong file sâu trong repo, chính xác gì đổi trong object database?
**Trả lời:** Blob hash đổi, đổi tree hash của thư mục cha, đổi mọi tree hash lên tree root, đổi commit hash. Mọi object tổ tiên nhận hash mới.

Đây là tính chất "chứng cứ giả mạo": thay đổi một bit ở lá nào cũng lan tới root. Trong Git, điều này nghĩa mọi commit hash là dấu vân tay của toàn bộ state repo tại điểm đó. Đó cũng là lý do Git có thể hiệu quả xác định cái gì đổi giữa hai commit — nếu hai tree hash khớp, toàn bộ subtree giống nhau, nên Git có thể bỏ qua hoàn toàn khi diff/fetch.
:::

::: details Câu 3: Bạn đang xây Merkle tree với số lá lẻ (ví dụ 5). Xử lý lá không cặp ở mỗi tầng thế nào?
**Trả lời:** Nhân đôi lá cuối (hash nó với chính nó) để tạo cặp. Đây là cách tiếp cận chuẩn dùng trong triển khai Merkle tree Bitcoin.

Có hai chiến lược phổ biến: (1) nhân đôi node không cặp và hash với chính nó (cách Bitcoin), hoặc (2) thăng node không cặp lên tầng tiếp không đổi (một số triển khai học thuật). Cách nhân đôi đơn giản hơn nhưng tạo vấn đề tinh tế: hai dataset khác nhau (ví dụ [A, B, C] và [A, B, C, C]) có thể sinh cùng root hash. Bitcoin giải bằng quy tắc xác minh thêm. Cách thăng tránh mơ hồ này nhưng làm sinh bằng chứng phức tạp hơn chút.
:::

::: details Câu 4: Merkle tree của bạn dùng trong hệ chia sẻ file peer-to-peer. Peer độc hại gửi bạn bằng chứng hợp lệ cho một lá, nhưng dữ liệu lá là rác. Bằng chứng có xác minh được không?
**Trả lời:** Không. Bằng chứng không xác minh được vì hash(dữ_liệu_rác) sẽ sinh lá hash khác bản gốc, và root tính được không khớp root đã biết.

Xác minh bằng chứng tính lại root bắt đầu từ hash(dữ_liệu_nhận). Nếu dữ liệu khác, hash(dữ_liệu_nhận) != hash(dữ_liệu_gốc), và lệch lan lên qua mọi tầng. Đây chính xác lý do Merkle proof hoạt động cho nguồn dữ liệu không tin cậy — bạn không cần tin peer, chỉ tin root hash (từ nguồn tin cậy như blockchain hoặc manifest đã ký).
:::
