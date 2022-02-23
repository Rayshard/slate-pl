use crate::slasm::instruction::Instruction;
use core::slice::Iter;
use std::ops::Index;

pub struct BasicBlock {
    instructions: Vec<Instruction>,
}

impl BasicBlock {
    pub fn new() -> BasicBlock {
        BasicBlock {
            instructions: Vec::new(),
        }
    }

    pub fn append(&mut self, instr: Instruction) {
        assert!(
            !self.is_terminated(),
            "Cannot append an instruction to a terminated block!"
        );

        self.instructions.push(instr);
    }

    pub fn is_terminated(&self) -> bool {
        match self.instructions.last() {
            Some(instr) => match instr {
                Instruction::Jump { .. } | Instruction::CondJump { .. } | Instruction::Ret => true,
                _ => false,
            },
            None => false,
        }
    }

    pub fn iter(&self) -> Iter<'_, Instruction> {
        self.instructions.iter()
    }

    pub fn size(&self) -> usize {
        self.instructions.len()
    }
}

impl Index<usize> for BasicBlock {
    type Output = Instruction;

    fn index(&self, idx: usize) -> &Self::Output {
        &self.instructions[idx]
    }
}
