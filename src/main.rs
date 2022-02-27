use crate::slasm::basic_block::BasicBlock;
use crate::slasm::function::Function;
use crate::slasm::instruction::Instruction;
use crate::slasm::prelude::Word;
use crate::slasm::program::Program;
use crate::slasm::visitors::nasm;
use crate::slasm::visitors::xml;
use ::xml::EmitterConfig;
use std::collections::HashMap;
use std::env;
use std::fs;
use std::fs::File;
use std::process;
use std::process::Command;

mod slasm;

static NASM_TEMPLATE_WINDOWS: &'static [u8] = include_bytes!("etc/nasm_template_windows.asm");
static NASM_TEMPLATE_MACOS: &'static [u8] = include_bytes!("etc/nasm_template_macos.asm");
static NASM_TEMPLATE_LINUX: &'static [u8] = include_bytes!("etc/nasm_template_linux.asm");

fn command_to_string(cmd: &Command) -> String {
    format!(
        "{} {}",
        cmd.get_program().to_str().unwrap(),
        cmd.get_args()
            .map(|x| String::from(x.to_str().unwrap()))
            .collect::<Vec<String>>()
            .join(" ")
    )
}

fn main() {
    let os_name = env::consts::OS;
    let mut program = Program::new(format!("test_{}", os_name));
    program.add_global(String::from("my_string"), b"Hello, World!\0".to_vec());

    let mut function = Function::new(
        String::from("Main"),
        HashMap::from([(String::from("a"), 8), (String::from("b"), 16)]),
        HashMap::from([(String::from("c"), 2), (String::from("d"), 7)]),
        8,
    );

    let mut basic_block = BasicBlock::new();
    basic_block.append(Instruction::Push {
        data: Word::from_i64(123).bytes.to_vec(),
    });
    basic_block.append(Instruction::Call {
        target: String::from("DEBUG_PRINT_I64"),
    });
    basic_block.append(Instruction::Push {
        data: Word::from_i64(64).bytes.to_vec(),
    });
    basic_block.append(Instruction::Ret);

    function.add_basic_block(String::from("entry"), basic_block);
    function.set_entry(String::from("entry"));

    program.add_function(function);
    program.set_entry(String::from("Main"));

    // Emit XML serialization
    let mut xml_file = File::create(format!("tests/rust/{}.slasm.xml", program.name())).unwrap();
    let mut xml_writer = EmitterConfig::new()
        .perform_indent(true)
        .create_writer(&mut xml_file);

    xml::emit_program(&program, &mut xml_writer);

    // Emit nasm
    let asm_path = format!("tests/rust/{}.asm", program.name());

    // Compile
    let (compilation_cmds, mut exec_cmd) = match os_name {
        "linux" => {
            fs::write(
                &asm_path,
                nasm::emit_program(
                    &program,
                    String::from_utf8(NASM_TEMPLATE_LINUX.to_vec()).unwrap(),
                ),
            )
            .unwrap();

            let obj_path = format!("tests/rust/{}.o", program.name());
            let exe_path = format!("tests/rust/{}", program.name());

            let mut assembler_cmd = process::Command::new("nasm");
            assembler_cmd.arg("-f");
            assembler_cmd.arg("elf64");
            assembler_cmd.arg(&asm_path);

            let mut linker_cmd = process::Command::new("ld");
            linker_cmd.arg("-o");
            linker_cmd.arg(&exe_path);
            linker_cmd.arg(&obj_path);

            (
                vec![assembler_cmd, linker_cmd],
                process::Command::new(exe_path),
            )
        }
        "macos" => {
            fs::write(
                &asm_path,
                nasm::emit_program(
                    &program,
                    String::from_utf8(NASM_TEMPLATE_MACOS.to_vec()).unwrap(),
                ),
            )
            .unwrap();

            let obj_path = format!("tests/rust/{}.o", program.name());
            let exe_path = format!("tests/rust/{}", program.name());

            let mut assembler_cmd = process::Command::new("nasm");
            assembler_cmd.arg("-f");
            assembler_cmd.arg("macho64");
            assembler_cmd.arg(&asm_path);

            let mut linker_cmd = process::Command::new("gcc");
            linker_cmd.arg("-Wl,-no_pie");
            linker_cmd.arg("-arch");
            linker_cmd.arg("x86_64");
            linker_cmd.arg("-o");
            linker_cmd.arg(&exe_path);
            linker_cmd.arg(&obj_path);

            (
                vec![assembler_cmd, linker_cmd],
                process::Command::new(exe_path),
            )
        }
        "windows" => {
            fs::write(
                &asm_path,
                nasm::emit_program(
                    &program,
                    String::from_utf8(NASM_TEMPLATE_WINDOWS.to_vec()).unwrap(),
                ),
            )
            .unwrap();

            let obj_path = format!("tests/rust/{}.obj", program.name());
            let exe_path = format!("tests/rust/{}.exe", program.name());

            let mut assembler_cmd = process::Command::new("nasm");
            assembler_cmd.arg("-f");
            assembler_cmd.arg("win64");
            assembler_cmd.arg(&asm_path);
            assembler_cmd.arg("-o");
            assembler_cmd.arg(&obj_path);

            let mut linker_cmd = process::Command::new("golink");
            linker_cmd.arg("/entry:Start");
            linker_cmd.arg("/console");
            linker_cmd.arg("kernel32.dll");
            linker_cmd.arg("user32.dll");
            linker_cmd.arg(&obj_path);

            (
                vec![assembler_cmd, linker_cmd],
                process::Command::new(exe_path),
            )
        }
        os => panic!("Compilation to {} is not supported!", os),
    };

    for mut cmd in compilation_cmds {
        println!("\x1b[93m[CMD]\x1b[0m {}", command_to_string(&cmd));

        if !cmd.spawn().unwrap().wait().unwrap().success() {
            return;
        }
    }

    // Run
    println!("\x1b[93m[CMD]\x1b[0m {}", command_to_string(&exec_cmd));
    let exec_exit_code = exec_cmd.spawn().unwrap().wait().unwrap();

    println!("Exited with code {}.", exec_exit_code.code().unwrap());
}
