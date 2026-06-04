use std::collections::HashMap;

pub struct Interner {
    str_to_id: HashMap<String, u32>,
    id_to_str: Vec<String>,
}

impl Interner {
    pub fn new() -> Self {
        Interner { str_to_id: HashMap::new(), id_to_str: Vec::new() }
    }

    pub fn intern(&mut self, s: &str) -> u32 {
        if let Some(&id) = self.str_to_id.get(s) {
            return id;
        }
        let id = self.id_to_str.len() as u32;
        self.str_to_id.insert(s.to_string(), id);
        self.id_to_str.push(s.to_string());
        id
    }

    pub fn resolve(&self, id: u32) -> Option<&str> {
        self.id_to_str.get(id as usize).map(|s| s.as_str())
    }
}
