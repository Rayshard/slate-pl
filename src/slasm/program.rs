use crate::slasm::function::Function;
use crate::slasm::prelude::WORD_SIZE;
use std::collections::HashMap;

pub struct Program {
    data: HashMap<String, Vec<u8>>,
    functions: HashMap<String, Function>,
    entry: Option<String>,
}

impl Program {
    pub fn new() -> Program {
        Program {
            data: HashMap::new(),
            functions: HashMap::new(),
            entry: None
        }
    }

    pub fn add_function(&mut self, function: Function) {
        if self.functions.contains_key(function.name()) {
            panic!("Program already contains a function with name '{}'!", function.name());
        }

        self.functions.insert(function.name().clone(), function);
    }

    pub fn add_data(&mut self, label: String, mut data: Vec<u8>) {
        if self.data.contains_key(&label) {
            panic!("Program already contains a data with label '{}'!", label);
        }

        data.extend(vec![0; (WORD_SIZE - data.len() % WORD_SIZE) % WORD_SIZE]); //Add padding if needed        
        self.data.insert(label, data);
    }

    pub fn contains_nonterminated_basic_block(&self) -> bool {
        self.functions.values().any(|f| f.contains_nonterminated_basic_block())
    }

    pub fn data(&self) -> &HashMap<String, Vec<u8>> {
        &self.data
    }

    pub fn functions(&self) -> &HashMap<String, Function> {
        &self.functions
    }

    pub fn entry(&self) -> &String {
        if let Some(name) = &self.entry {
            return name
        }

        panic!("Program does not have a set entry!");
    }

    pub fn set_entry(&mut self, value: String) {
        if !self.functions.contains_key(&value) {
            panic!("Program does not contain a function with name '{}'!", value);
        }

        self.entry = Some(value);
    }
}
