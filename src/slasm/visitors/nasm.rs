extern crate textwrap;

use crate::slasm::instruction::Instruction;
use crate::slasm::prelude::VERSION;
use crate::slasm::program::Program;
use crate::Function;

pub fn emit_instruction(instr: &Instruction) -> String {
    match instr {
        Instruction::Noop => String::from(""),
        Instruction::Pop => String::from(""),
        Instruction::Or => String::from(""),
        Instruction::And => String::from(""),
        Instruction::Xor => String::from(""),
        Instruction::Not => String::from(""),
        Instruction::Shl => String::from(""),
        Instruction::Shr => String::from(""),
        Instruction::Ret => String::from(""),
        Instruction::LoadConst { value } => String::from(""),
        Instruction::LoadLocal { name } => String::from(""),
        Instruction::StoreLocal { name } => String::from(""),
        Instruction::LoadParam { name } => String::from(""),
        Instruction::StoreParam { name } => String::from(""),
        Instruction::LoadGlobal { name } => String::from(""),
        Instruction::StoreGlobal { name } => String::from(""),
        Instruction::LoadMem { offset } => String::from(""),
        Instruction::StoreMem { offset } => String::from(""),
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
        Instruction::Convert { dt_from, dt_to } => String::from(""),
        Instruction::Jump { target } => String::from(""),
        Instruction::CondJump { target } => String::from(""),
        Instruction::Call { target } => String::from(""),
        Instruction::IndirectCall {
            num_params,
            num_returns,
        } => String::from(""),
        _ => todo!("{:?}", instr),
    }
}

pub fn emit_function(function: &Function) -> String {
    todo!();
}

pub fn emit_program(program: &Program) -> String {
    String::from(textwrap::dedent(
        r#"
        global _main
        section .text
        _main:
            mov rax, 0x2000004 ; write
            mov rdi, 1 ; stdout
            mov rsi, msg
            mov rdx, msg.len
            syscall
            mov rax, 0x2000001 ; exit
            mov rdi, 0
            syscall
        section .data
        msg:    db      "Hello, world!", 10
        .len:   equ     $ - msg
        "#,
    ))
}
