use crate::slasm::function::Function;
use std::collections::HashMap;

pub struct Program {
    name: String,
    globals: HashMap<String, Vec<u8>>,
    functions: HashMap<String, Function>,
    entry: Option<String>,
}

impl Program {
    pub fn new(name: String) -> Program {
        Program {
            name: name,
            globals: HashMap::new(),
            functions: HashMap::new(),
            entry: None,
        }
    }

    pub fn add_function(&mut self, function: Function) {
        assert!(
            !self.functions.contains_key(function.name()),
            "Program already contains a function with name '{}'!",
            function.name()
        );

        self.functions.insert(function.name().clone(), function);
    }

    pub fn add_global(&mut self, label: String, data: Vec<u8>) {
        assert!(
            !self.globals.contains_key(&label),
            "Program already contains a global with name '{}'!",
            label
        );

        self.globals.insert(label, data);
    }

    pub fn contains_nonterminated_basic_block(&self) -> bool {
        self.functions
            .values()
            .any(|f| f.contains_nonterminated_basic_block())
    }

    pub fn name(&self) -> &String {
        &self.name
    }

    pub fn globals(&self) -> &HashMap<String, Vec<u8>> {
        &self.globals
    }

    pub fn functions(&self) -> &HashMap<String, Function> {
        &self.functions
    }

    pub fn entry(&self) -> &String {
        if let Some(name) = &self.entry {
            return name;
        }

        panic!("Program does not have a set entry!");
    }

    pub fn set_entry(&mut self, value: String) {
        assert!(
            self.functions.contains_key(&value),
            "Program does not contain a function with name '{}'!",
            value
        );

        self.entry = Some(value);
    }
}
