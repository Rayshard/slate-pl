extern crate textwrap;

use crate::slasm::basic_block::BasicBlock;
use crate::slasm::function::Function;
use crate::slasm::instruction::Instruction;
use crate::slasm::prelude::VERSION;
use crate::slasm::program::Program;
use std::collections::HashMap;

struct FunctionDefinition<'a> {
    params: HashMap<&'a String, (u64, u64)>,
    locals: HashMap<&'a String, (u64, u64)>,
    returns: Vec<u64>,
}

struct GlobalContext<'a> {
    functions: HashMap<&'a String, FunctionDefinition<'a>>,
}

struct FunctionContext<'a> {
    global_ctx: &'a GlobalContext<'a>,
    function_name: &'a String,
    function_definition: &'a FunctionDefinition<'a>,
}

impl GlobalContext<'_> {
    pub fn get_function(&self, function_name: &String) -> &FunctionDefinition {
        if !self.functions.contains_key(function_name) {
            panic!(
                "Global Context does not contain a function named {}",
                function_name
            );
        }

        return &self.functions[function_name];
    }
}

fn emit_instruction(instr: &Instruction, ctx: &FunctionContext) -> String {
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
        Instruction::CondJump {
            true_target,
            false_target,
        } => String::from(""),
        Instruction::Call { target } => String::from(""),
        Instruction::IndirectCall {
            param_buffer_size,
            ret_buffer_size,
        } => String::from(""),
    }
}

fn emit_basic_block(name: &String, basic_block: &BasicBlock, ctx: &FunctionContext) -> String {
    //format!("\n{}:\n    push 0x0000000000000010\n    call DEBUG_PRINT_I64\n    add rsp, 8\n    mov rax, 17\n    ret", function.name())

    format!(
        "\n    .{}:    {}",
        name,
        basic_block
            .iter()
            .map(|instruction| emit_instruction(instruction, ctx))
            .collect::<Vec<String>>()
            .join("\n    ")
    )
}

fn emit_function(function: &Function, global_ctx: &GlobalContext) -> String {
    //format!("\n{}:\n    push 0x0000000000000010\n    call DEBUG_PRINT_I64\n    add rsp, 8\n    mov rax, 17\n    ret", function.name())

    let ctx = FunctionContext {
        global_ctx: global_ctx,
        function_name: function.name(),
        function_definition: global_ctx.get_function(function.name()),
    };

    format!(
        "\n{}:    {}",
        function.name(),
        function
            .basic_blocks()
            .iter()
            .map(|(bb_name, bb)| emit_basic_block(bb_name, bb, &ctx))
            .collect::<Vec<String>>()
            .join("\n    ")
    )
}

pub fn emit_program(program: &Program, header: String) -> String {
    let mut result = header;

    assert!(result.contains("#ENTRY_FUNC_NAME#"));
    result = result.replace("#ENTRY_FUNC_NAME#", program.entry().as_str());

    result.push_str("\n\n; ==================== END OF HEADER ====================");
    result.push_str(&format!("\n\n; GENERATED FROM SLASM VERSION {}", VERSION));

    // Add globals
    result.push_str("\n\n    section .data");

    for (name, data) in program.globals() {
        let text = format!(
            "\n{}: db {}",
            name,
            data.iter()
                .map(|x| x.to_string())
                .collect::<Vec<String>>()
                .join(", ")
        );

        result.push_str(text.as_str());
    }

    // Add functions
    let global_ctx = GlobalContext {
        functions: {
            let mut functions: HashMap<&String, FunctionDefinition> = HashMap::new();

            for (func_name, func) in program.functions() {
                functions.insert(
                    func_name,
                    FunctionDefinition {
                        params: {
                            let mut params: HashMap<&String, (u64, u64)> = HashMap::new();
                            let mut byte_offset: u64 = 0;

                            for (name, size) in func.params() {
                                params.insert(name, (byte_offset, size.clone()));
                                byte_offset += size;
                            }

                            params
                        },
                        locals: {
                            let mut locals: HashMap<&String, (u64, u64)> = HashMap::new();
                            let mut byte_offset: u64 = 0;

                            for (name, size) in func.locals() {
                                locals.insert(name, (byte_offset, size.clone()));
                                byte_offset += size;
                            }

                            locals
                        },
                        returns: func.returns().clone(),
                    },
                );
            }

            functions
        },
    };

    result.push_str("\n\n    section .text");
    result.push_str(
        &program
            .functions()
            .iter()
            .map(|(_, function)| emit_function(function, &global_ctx))
            .collect::<Vec<String>>()
            .join("\n"),
    );

    result
}
