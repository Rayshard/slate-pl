use crate::slasm::basic_block::BasicBlock;
use crate::slasm::function::Function;
use crate::slasm::instruction::Instruction;
use crate::slasm::prelude::Word;
use crate::slasm::program::Program;
use crate::slasm::visitors::json;
use crate::slasm::visitors::nasm;
use crate::slasm::visitors::xml;
use ::tempdir::TempDir;
use ::xml::EmitterConfig;
use std::collections::HashMap;
use std::env;
use std::fs;
use std::fs::File;
use std::process;
use std::process::Command;
use std::time;

mod slasm;

fn get_include_file(name: String) -> Vec<u8> {
    match name.as_str() {
        "nasm_template_windows.asm" => {
            static FILE: &'static [u8] = include_bytes!("include/nasm_template_windows.asm");
            FILE.to_vec()
        }
        "nasm_template_macos.asm" => {
            static FILE: &'static [u8] = include_bytes!("include/nasm_template_macos.asm");
            FILE.to_vec()
        }
        "nasm_template_linux.asm" => {
            static FILE: &'static [u8] = include_bytes!("include/nasm_template_linux.asm");
            FILE.to_vec()
        }
        _ => {
            panic!("Unknown file: {}", name);
        }
    }
}

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
    let mut program = Program::new(String::from("test"));
    program.add_global(String::from("my_string"), b"Hello, World!\0".to_vec());

    let mut function = Function::new(
        String::from("Main"),
        HashMap::from([(String::from("a"), 8), (String::from("b"), 16)]),
        HashMap::from([(String::from("c"), 2), (String::from("d"), 7)]),
        vec![],
    );

    // let mut basic_block = BasicBlock::new();
    // basic_block.append(Instruction::Push {
    //     data: Word::from_i64(123).bytes.to_vec(),
    // });
    // basic_block.append(Instruction::Call {
    //     target: String::from("DEBUG_PRINT_I64"),
    // });
    // basic_block.append(Instruction::Push {
    //     data: Word::from_i64(64).bytes.to_vec(),
    // });
    // basic_block.append(Instruction::Ret);

    let mut basic_block = BasicBlock::new();
    basic_block.append(Instruction::Push {
        data: vec![15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2],
    });
    basic_block.append(Instruction::Call {
        target: String::from("Main"),
    });

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

    // Emit JSON serialization
    fs::write(
        format!("tests/rust/{}.slasm.json", program.name()),
        serde_json::to_string_pretty(&json::emit_program(&program)).unwrap(),
    )
    .expect("Unable to write to json file!");

    // Emit nasm and compile
    let os_name = env::consts::OS;
    let temp_dir = TempDir::new("").expect("Unable to create temporary directory for compilation!");
    let asm_path = temp_dir.path().join(format!("{}.asm", program.name()));

    fs::write(
        &asm_path,
        nasm::emit_program(
            &program,
            String::from_utf8(get_include_file(format!("nasm_template_{}.asm", os_name))).unwrap(),
        ),
    )
    .unwrap();

    fs::copy(&asm_path, "tests/rust/output.asm").unwrap();

    let (compilation_cmds, mut exec_cmd) = match os_name {
        "linux" => {
            let obj_path = asm_path.with_extension("o");
            let exe_path = asm_path.with_extension("");

            let mut assembler_cmd = process::Command::new("nasm");
            assembler_cmd.arg("-f");
            assembler_cmd.arg("elf64");
            assembler_cmd.arg(&asm_path);

            let mut linker_cmd = process::Command::new("gcc");
            linker_cmd.arg("-m64");
            linker_cmd.arg("-o");
            linker_cmd.arg(&exe_path);
            linker_cmd.arg(&obj_path);

            (
                vec![assembler_cmd, linker_cmd],
                process::Command::new(exe_path),
            )
        }
        "macos" => {
            let obj_path = asm_path.with_extension("o");
            let exe_path = asm_path.with_extension("");

            let mut assembler_cmd = process::Command::new("nasm");
            assembler_cmd.arg("-f");
            assembler_cmd.arg("macho64");
            assembler_cmd.arg(&asm_path);

            let mut linker_cmd = process::Command::new("gcc");
            //linker_cmd.arg("-Wl,-no_pie");
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
            let obj_path = asm_path.with_extension("obj");
            let exe_path = asm_path.with_extension("exe");

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
            linker_cmd.arg("msvcrt.dll");
            linker_cmd.arg(&obj_path);

            (
                vec![assembler_cmd, linker_cmd],
                process::Command::new(exe_path),
            )
        }
        os => panic!("Compilation to {} is not supported!", os),
    };

    for mut cmd in compilation_cmds {
        let now = time::Instant::now();
        println!("\x1b[93m[CMD]\x1b[0m {}", command_to_string(&cmd));

        if !cmd.spawn().unwrap().wait().unwrap().success() {
            return;
        }

        println!(
            "\x1b[93m[Finished in {} seconds]\x1b[0m",
            now.elapsed().as_secs_f64()
        );
    }

    // Run
    // let now = time::Instant::now();

    // println!("\x1b[93m[CMD]\x1b[0m {}", command_to_string(&exec_cmd));
    // let exec_exit_code = exec_cmd.spawn().unwrap().wait().unwrap();

    // println!(
    //     "\x1b[93m[Exited with code {}]\x1b[0m\n\x1b[93m[Finished in {} seconds]\x1b[0m",
    //     exec_exit_code.code().unwrap(),
    //     now.elapsed().as_secs_f64()
    // );
}
