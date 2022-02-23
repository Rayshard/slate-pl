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
use std::fs;
use std::fs::File;
use std::path::{Path, PathBuf};
use std::process;

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
    let asm_path = Path::new("tests/rust/test.asm");
    fs::write(asm_path, nasm::emit_program(&program)).unwrap();

    // Compile
    let mut bin_path: PathBuf;
    let output = match env::consts::OS {
        "linux" => {
            bin_path = asm_path.with_extension("");

            todo!("linux")
        }
        "macos" => {
            bin_path = asm_path.with_extension("");

            let obj_path = asm_path.with_extension("o");

            process::Command::new("sh")
                .arg("-c")
                .arg(format!(
                    "nasm -f macho64 {} && gcc -Wl,-no_pie -arch x86_64 -o {} {}",
                    asm_path.to_str().unwrap(),
                    bin_path.to_str().unwrap(),
                    obj_path.to_str().unwrap()
                ))
                .output()
        }
        "windows" => {
            bin_path = asm_path.with_extension("");

            todo!("windows")
        }
        os => panic!("Compilation to {} is not supported!", os),
    }
    .expect("Failed to compile!");

    if output.stderr.len() != 0 {
        println!(
            "----------STDERR---------\n{}--------------------------",
            String::from_utf8(output.stderr).unwrap(),
        );
    }

    if output.stdout.len() != 0 {
        println!(
            "----------STDOUT---------\n{}--------------------------",
            String::from_utf8(output.stdout).unwrap()
        );
    }

    if output.status.code().unwrap() == 0 {
        let output = process::Command::new(format!("./{}", bin_path.to_str().unwrap()))
            .output()
            .expect(&format!("Failed to run {}", bin_path.to_str().unwrap()));

        println!(
            "{}{}Exited with code {}.",
            String::from_utf8(output.stderr).unwrap(),
            String::from_utf8(output.stdout).unwrap(),
            output.status.code().unwrap_or(0)
        );
    }
}
