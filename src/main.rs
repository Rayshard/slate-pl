use std::fs;
use crate::slasm::basic_block::BasicBlock;
use crate::slasm::function::Function;
use crate::slasm::instruction::Instruction;
use crate::slasm::prelude::Word;
use crate::slasm::program::Program;
use crate::slasm::visitors::nasm;
use crate::slasm::visitors::xml;
use ::xml::EmitterConfig;
use std::collections::HashSet;
use std::env;
use std::fs::File;
mod slasm;

fn main() {
    let mut program = Program::new();
    program.add_data(String::from("my_string"), b"Hello, World!\0".to_vec());

    let mut function = Function::new(
        String::from("Main"),
        HashSet::from([String::from("a"), String::from("b")]),
        HashSet::from([String::from("c"), String::from("d")]),
        1,
    );

    let mut basic_block = BasicBlock::new();
    basic_block.append(Instruction::LoadConst {
        value: Word::from_i64(123),
    });
    basic_block.append(Instruction::Call {
        target: String::from("DEBUG_PRINT_I64"),
    });
    basic_block.append(Instruction::LoadConst {
        value: Word::from_i64(64),
    });
    basic_block.append(Instruction::Ret);

    function.add_basic_block(String::from("entry"), basic_block);
    function.set_entry(String::from("entry"));

    program.add_function(function);
    program.set_entry(String::from("Main"));

    // Emit XML serialization
    let mut xml_file = File::create("tests/rust/test.slasm.xml").unwrap();
    let mut xml_writer = EmitterConfig::new()
        .perform_indent(true)
        .create_writer(&mut xml_file);

    xml::emit_program(&program, &mut xml_writer);

    // Emit nasm
    fs::write("tests/rust/test.slasm.asm", nasm::emit_program(&program)).unwrap();

    // Compile
    match env::consts::OS {
        "linux" => {
            todo!("linux")
        }
        "macos" => {
            todo!("macos")
        }
        "windows" => {
            todo!("windows")
        }
        os => panic!("Compilation to {} is not supported!", os),
    }
}
