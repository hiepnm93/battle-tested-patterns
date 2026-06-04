use std::collections::BTreeMap;

#[derive(Clone, Debug)]
pub struct KVEntry {
    pub key: String,
    pub value: Option<String>, // None = tombstone
    pub seq: usize,
}

pub struct Memtable {
    entries: BTreeMap<String, KVEntry>,
    size: usize,
}

impl Memtable {
    pub fn new() -> Self {
        Memtable { entries: BTreeMap::new(), size: 0 }
    }

    pub fn put(&mut self, key: &str, value: &str, seq: usize) {
        self.entries.insert(key.to_string(), KVEntry {
            key: key.to_string(), value: Some(value.to_string()), seq,
        });
        self.size += 1;
    }

    pub fn delete(&mut self, key: &str, seq: usize) {
        self.entries.insert(key.to_string(), KVEntry {
            key: key.to_string(), value: None, seq,
        });
        self.size += 1;
    }

    pub fn get(&self, key: &str) -> Option<&KVEntry> {
        self.entries.get(key)
    }

    pub fn size(&self) -> usize { self.size }

    pub fn flush(&mut self) -> Vec<KVEntry> {
        let result: Vec<KVEntry> = self.entries.values().cloned().collect();
        self.entries.clear();
        self.size = 0;
        result
    }
}

pub struct LSMTree {
    memtable: Memtable,
    runs: Vec<Vec<KVEntry>>,
    seq: usize,
    flush_threshold: usize,
    max_runs: usize,
}

impl LSMTree {
    pub fn new(flush_threshold: usize, max_runs: usize) -> Self {
        LSMTree {
            memtable: Memtable::new(),
            runs: Vec::new(),
            seq: 0,
            flush_threshold,
            max_runs,
        }
    }

    pub fn put(&mut self, key: &str, value: &str) {
        self.memtable.put(key, value, self.seq);
        self.seq += 1;
        if self.memtable.size() >= self.flush_threshold {
            self.flush_memtable();
        }
    }

    pub fn delete(&mut self, key: &str) {
        self.memtable.delete(key, self.seq);
        self.seq += 1;
        if self.memtable.size() >= self.flush_threshold {
            self.flush_memtable();
        }
    }

    pub fn get(&self, key: &str) -> Option<&str> {
        if let Some(entry) = self.memtable.get(key) {
            return entry.value.as_deref();
        }
        for run in &self.runs {
            if let Ok(idx) = run.binary_search_by(|e| e.key.as_str().cmp(key)) {
                return run[idx].value.as_deref();
            }
        }
        None
    }

    fn flush_memtable(&mut self) {
        let run = self.memtable.flush();
        self.runs.insert(0, run);
        if self.runs.len() > self.max_runs {
            self.compact();
        }
    }

    fn compact(&mut self) {
        let mut merged = BTreeMap::new();
        for run in self.runs.iter().rev() {
            for entry in run {
                merged.insert(entry.key.clone(), entry.clone());
            }
        }
        let result: Vec<KVEntry> = merged.into_values()
            .filter(|e| e.value.is_some())
            .collect();
        self.runs = if result.is_empty() { vec![] } else { vec![result] };
    }

    pub fn run_count(&self) -> usize { self.runs.len() }
}
