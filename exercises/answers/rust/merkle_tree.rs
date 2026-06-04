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
    pub position: String, // "left" or "right"
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
