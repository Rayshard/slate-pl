extern crate textwrap;

use crate::slasm::instruction::Instruction;
use crate::slasm::prelude::VERSION;
use crate::slasm::program::Program;
use crate::Function;

pub fn emit_instruction(instr: &Instruction) -> String {
    match instr {
        Instruction::Noop => String::from(""),
        Instruction::Or => String::from(""),
        Instruction::And => String::from(""),
        Instruction::Xor => String::from(""),
        Instruction::Not => String::from(""),
        Instruction::Shl => String::from(""),
        Instruction::Shr => String::from(""),
        Instruction::Ret => String::from(""),
        Instruction::Push { data } => String::from(""),
        Instruction::Pop { amt } => String::from(""),
        Instruction::Allocate { amt } => String::from(""),
        Instruction::LoadLocal { name } => String::from(""),
        Instruction::StoreLocal { name } => String::from(""),
        Instruction::LoadParam { name } => String::from(""),
        Instruction::StoreParam { name } => String::from(""),
        Instruction::LoadGlobal { name } => String::from(""),
        Instruction::StoreGlobal { name } => String::from(""),
        Instruction::LoadMem { offset, amt } => String::from(""),
        Instruction::StoreMem { offset, amt } => String::from(""),
        Instruction::LoadLocalAddr { name } => String::from(""),
        Instruction::LoadParamAddr { name } => String::from(""),
        Instruction::LoadGlobalAddr { name } => String::from(""),
        Instruction::LoadFuncAddr { name } => String::from(""),
        Instruction::Add { data_type } => String::from(""),
        Instruction::Sub { data_type } => String::from(""),
        Instruction::Mul { data_type } => String::from(""),
        Instruction::Div { data_type } => String::from(""),
        Instruction::Mod { data_type } => String::from(""),
        Instruction::Inc { data_type } => String::from(""),
        Instruction::Dec { data_type } => String::from(""),
        Instruction::Eq { data_type } => String::from(""),
        Instruction::Neq { data_type } => String::from(""),
        Instruction::Gt { data_type } => String::from(""),
        Instruction::Lt { data_type } => String::from(""),
        Instruction::GtEq { data_type } => String::from(""),
        Instruction::LtEq { data_type } => String::from(""),
        Instruction::Neg { data_type } => String::from(""),
        Instruction::Convert { from, to } => String::from(""),
        Instruction::Jump { target } => String::from(""),
        Instruction::CondJump { true_target, false_target } => String::from(""),
        Instruction::Call { target } => String::from(""),
        Instruction::IndirectCall {
            param_buffer_size,
            ret_buffer_size,
        } => String::from(""),
    }
}

pub fn emit_function(function: &Function) -> String {
    todo!();
}

pub fn emit_program(program: &Program, template: String) -> String {
    template
}
