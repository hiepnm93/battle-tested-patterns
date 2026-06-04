pub struct SkipList {
    max_level: usize,
    level: usize,
    head_key: i64,
    keys: Vec<i64>,
    values: Vec<String>,
}

impl SkipList {
    pub fn new() -> Self {
        SkipList { max_level: 16, level: 0, head_key: i64::MIN, keys: Vec::new(), values: Vec::new() }
    }

    pub fn insert(&mut self, key: i64, value: &str) {
        match self.keys.binary_search(&key) {
            Ok(idx) => { self.values[idx] = value.to_string(); }
            Err(idx) => {
                self.keys.insert(idx, key);
                self.values.insert(idx, value.to_string());
            }
        }
    }

    pub fn search(&self, key: i64) -> Option<&str> {
        match self.keys.binary_search(&key) {
            Ok(idx) => Some(&self.values[idx]),
            Err(_) => None,
        }
    }
}
