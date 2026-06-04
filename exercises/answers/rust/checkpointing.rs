use std::collections::HashMap;

pub struct LogEntry {
    pub id: usize,
    pub operation: String,
    pub key: String,
    pub value: Option<String>,
}

struct Snapshot {
    state: HashMap<String, String>,
    wal_position: usize,
}

pub struct CheckpointableStore {
    state: HashMap<String, String>,
    wal: Vec<LogEntry>,
    next_id: usize,
    checkpoint: Option<Snapshot>,
}

impl CheckpointableStore {
    pub fn new() -> Self {
        CheckpointableStore {
            state: HashMap::new(),
            wal: Vec::new(),
            next_id: 1,
            checkpoint: None,
        }
    }

    pub fn apply(&mut self, operation: &str, key: &str, value: Option<&str>) {
        let entry = LogEntry {
            id: self.next_id,
            operation: operation.to_string(),
            key: key.to_string(),
            value: value.map(|v| v.to_string()),
        };
        self.next_id += 1;
        self.execute_op(&entry);
        self.wal.push(entry);
    }

    pub fn get(&self, key: &str) -> Option<&str> {
        self.state.get(key).map(|s| s.as_str())
    }

    pub fn take_checkpoint(&mut self) {
        self.checkpoint = Some(Snapshot {
            state: self.state.clone(),
            wal_position: self.wal.len(),
        });
    }

    pub fn simulate_crash(&mut self) {
        self.state.clear();
    }

    pub fn recover(&mut self) -> usize {
        if let Some(ref snap) = self.checkpoint {
            self.state = snap.state.clone();
            let start = snap.wal_position;
            let mut replayed = 0;
            for i in start..self.wal.len() {
                self.execute_op_by_index(i);
                replayed += 1;
            }
            return replayed;
        }
        self.state.clear();
        for i in 0..self.wal.len() {
            self.execute_op_by_index(i);
        }
        self.wal.len()
    }

    fn execute_op(&mut self, entry: &LogEntry) {
        if entry.operation == "SET" {
            if let Some(ref v) = entry.value {
                self.state.insert(entry.key.clone(), v.clone());
            }
        } else if entry.operation == "DELETE" {
            self.state.remove(&entry.key);
        }
    }

    fn execute_op_by_index(&mut self, idx: usize) {
        let op = self.wal[idx].operation.clone();
        let key = self.wal[idx].key.clone();
        let value = self.wal[idx].value.clone();
        if op == "SET" {
            if let Some(v) = value {
                self.state.insert(key, v);
            }
        } else if op == "DELETE" {
            self.state.remove(&key);
        }
    }

    pub fn wal_length(&self) -> usize { self.wal.len() }
    pub fn state_size(&self) -> usize { self.state.len() }
}
