use crate::slasm::basic_block::BasicBlock;
use std::collections::HashMap;

pub struct Function {
    name: String,
    params: HashMap<String, u64>,
    locals: HashMap<String, u64>,
    ret_buffer_size: u64,
    basic_blocks: HashMap<String, BasicBlock>,
    entry: Option<String>,
}

impl Function {
    pub fn new(
        name: String,
        params: HashMap<String, u64>,
        locals: HashMap<String, u64>,
        ret_buffer_size: u64,
    ) -> Function {
        Function {
            name: name,
            params: params,
            locals: locals,
            ret_buffer_size: ret_buffer_size,
            basic_blocks: HashMap::new(),
            entry: None,
        }
    }

    pub fn add_basic_block(&mut self, name: String, basic_block: BasicBlock) {
        assert!(
            !self.basic_blocks.contains_key(&name),
            "Function '{}' already contains a basic block with name '{}'!",
            self.name,
            name
        );

        self.basic_blocks.insert(name, basic_block);
    }

    pub fn contains_nonterminated_basic_block(&self) -> bool {
        !self.basic_blocks.values().all(|bb| bb.is_terminated())
    }

    pub fn name(&self) -> &String {
        &self.name
    }

    pub fn params(&self) -> &HashMap<String, u64> {
        &self.params
    }

    pub fn locals(&self) -> &HashMap<String, u64> {
        &self.locals
    }

    pub fn ret_buffer_size(&self) -> u64 {
        self.ret_buffer_size
    }

    pub fn basic_blocks(&self) -> &HashMap<String, BasicBlock> {
        &self.basic_blocks
    }

    pub fn is_procedure(&self) -> bool {
        self.ret_buffer_size == 0
    }

    pub fn entry(&self) -> &String {
        if let Some(name) = &self.entry {
            return name;
        }

        panic!("Function '{}' does not have a set entry!", self.name);
    }

    pub fn set_entry(&mut self, value: String) {
        assert!(
            self.basic_blocks.contains_key(&value),
            "Function '{}' does not contain a basic block with name '{}'!",
            self.name,
            value
        );

        self.entry = Some(value);
    }
}