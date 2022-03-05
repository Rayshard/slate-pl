extern crate textwrap;

use crate::slasm::basic_block::BasicBlock;
use crate::slasm::function::Function;
use crate::slasm::instruction::Instruction;
use crate::slasm::prelude::to_hex_string;
use crate::slasm::prelude::VERSION;
use crate::slasm::program::Program;
use indoc::{formatdoc, indoc};
use std::cmp;
use std::collections::HashMap;

const WORD_SIZE: u64 = 8;

struct FunctionInfo {
    pub param_buffer_size: u64, // the amount of bytes needed to hold all parameters
    pub return_buffer_size: u64, // the amount of bytes needed to hold all return values
    pub padded_return_buffer_size: u64, // the return buffer size rounded to the next mulitple of WORD_SIZE
    pub pre_call_allocated_space: u64,
    pub pre_call_padding: u64,
    pub return_buffer_padding: u64, // the number of bytes that when added to the return buffer size, makes it a multiple of WORD_SIZE
    pub post_call_pop_amt: u64,
}

impl FunctionInfo {
    pub fn new(function: &Function) -> FunctionInfo {
        let param_buffer_size: u64 = function.params().values().sum();
        let return_buffer_size: u64 = function.returns().iter().sum();
        let return_buffer_padding = (WORD_SIZE - return_buffer_size % WORD_SIZE) % WORD_SIZE;
        let padded_return_buffer_size = return_buffer_size + return_buffer_padding;
        let pre_call_padding = std::cmp::min(0, padded_return_buffer_size - param_buffer_size);
        let pre_call_allocated_space = param_buffer_size + pre_call_padding;
        let post_call_pop_amt = pre_call_allocated_space - return_buffer_size;

        FunctionInfo {
            param_buffer_size: param_buffer_size,
            return_buffer_size: return_buffer_size,
            padded_return_buffer_size: padded_return_buffer_size,
            pre_call_allocated_space: pre_call_allocated_space,
            pre_call_padding: pre_call_padding,
            return_buffer_padding: return_buffer_padding,
            post_call_pop_amt: post_call_pop_amt,
        }
    }
}

struct GlobalContext {
    functions: HashMap<String, FunctionInfo>,
}

impl GlobalContext {
    pub fn get_function_info(&self, name: &String) -> &FunctionInfo {
        if let Some(info) = self.functions.get(name) {
            return info;
        }

        panic!("Global Context does not contain a function named {}", name);
    }
}

struct FunctionContext<'a> {
    global_ctx: &'a GlobalContext,
    name: &'a String,
    params: HashMap<&'a String, (u64, u64)>, // name -> (offset, size)
    locals: HashMap<&'a String, (u64, u64)>, // name -> (offset, size)
    cc_info: &'a FunctionInfo,
}

impl FunctionContext<'_> {
    pub fn global_ctx(&self) -> &GlobalContext {
        return self.global_ctx;
    }

    pub fn cc_info(&self) -> &FunctionInfo {
        return self.cc_info;
    }
}

fn emit_instruction(instr: &Instruction, ctx: &FunctionContext) -> String {
    match instr {
        Instruction::Noop => formatdoc!(
            "
            ; noop
            nop
            "
        ),
        Instruction::Push { data } => formatdoc!(
            "
            ; push {}
            {}
            ",
            data.iter()
                .map(|x| format!("{:02x}", x).to_uppercase())
                .collect::<Vec<String>>()
                .join(":"),
            data.chunks(8)
                .map(|x| match x.len() {
                    8 => format!("mov rax, {}\npush rax", to_hex_string(x)),
                    7 => format!("mov rax, {}00\npush rax\nadd rsp, 1", to_hex_string(x)),
                    6 => format!("mov rax, {}0000\npush rax\nadd rsp, 2", to_hex_string(x)),
                    5 => format!("mov rax, {}000000\npush rax\nadd rsp, 3", to_hex_string(x)),
                    4 => format!(
                        "mov rax, {}00000000\npush rax\nadd rsp, 4",
                        to_hex_string(x)
                    ),
                    3 => format!(
                        "mov rax, {}0000000000\npush rax\nadd rsp, 5",
                        to_hex_string(x)
                    ),
                    2 => format!(
                        "mov rax, {}000000000000\npush rax\nadd rsp, 6",
                        to_hex_string(x)
                    ),
                    1 => format!(
                        "mov rax, {}00000000000000\npush rax\nadd rsp, 7",
                        to_hex_string(x)
                    ),
                    size => panic!("Invalid chunk size: {}", size),
                })
                .collect::<Vec<String>>()
                .join("\n")
        ),
        Instruction::Pop { amt } => formatdoc!(
            "
            ; pop {}
            add rsp, {}
            ",
            amt,
            amt
        ),
        Instruction::Allocate { amt } => formatdoc!(
            "
            ; allocate {}
            mov rax, rsp
            sub rsp, {}
            push rax
            ",
            amt,
            amt
        ),
        Instruction::Call { target } => {
            let target_cc_info = ctx.global_ctx().get_function_info(target);

            formatdoc!(
                "
                ; call {}
                {}call {}{}
                ",
                target,
                if target_cc_info.pre_call_padding != 0 {
                    format!(
                        "\nsub rsp, {} ; pad stack for the return buffer",
                        target_cc_info.pre_call_padding
                    )
                } else {
                    String::new()
                },
                target,
                if target_cc_info.post_call_pop_amt != 0 {
                    format!(
                        "\nadd rsp, {} ; leave only the return buffer on the stack",
                        target_cc_info.post_call_pop_amt
                    )
                } else {
                    String::new()
                }
            )
        }
        Instruction::Ret => {
            let cc_info = ctx.cc_info();

            formatdoc!(
                "
                ; ret
                {}mov rsp, rbp
                pop rbp
                ret
                ",
                if cc_info.return_buffer_size != 0 {
                    formatdoc!(
                        "
                        {}mov rax, rbp
                        add rax, {}
                        {}\n
                        ",
                        if cc_info.return_buffer_padding != 0 {
                            format!("sub rsp, {}\n", cc_info.return_buffer_padding)
                        } else {
                            String::new()
                        },
                        cc_info.pre_call_allocated_space - cc_info.padded_return_buffer_size,
                        formatdoc!(
                            "
                            pop r10
                            sub rax, {}
                            mov [rax], r10
                            ",
                            WORD_SIZE
                        )
                        .repeat((cc_info.padded_return_buffer_size / WORD_SIZE) as usize),
                    )
                } else {
                    String::new()
                }
            )
        }
        _ => unimplemented!("{:?}", instr),
    }
}

fn emit_basic_block(name: &String, basic_block: &BasicBlock, ctx: &FunctionContext) -> String {
    format!(
        ".{}:\n{}",
        name,
        textwrap::indent(
            &basic_block
                .iter()
                .map(|instruction| emit_instruction(instruction, ctx))
                .collect::<Vec<String>>()
                .join("\n"),
            "    "
        )
    )
}

fn emit_function(function: &Function, global_ctx: &GlobalContext) -> String {
    let ctx = FunctionContext {
        name: function.name(),
        params: {
            let mut params: HashMap<&String, (u64, u64)> = HashMap::new();
            let mut byte_offset: u64 = 0;
            for (name, size) in function.params() {
                params.insert(name, (byte_offset, size.clone()));
                byte_offset += size;
            }
            params
        },
        locals: {
            let mut locals: HashMap<&String, (u64, u64)> = HashMap::new();
            let mut byte_offset: u64 = 0;
            for (name, size) in function.locals() {
                locals.insert(name, (byte_offset, size.clone()));
                byte_offset += size;
            }
            locals
        },
        global_ctx: global_ctx,
        cc_info: global_ctx.get_function_info(function.name()),
    };

    format!(
        "{}:\n{}",
        function.name(),
        textwrap::indent(
            &function
                .basic_blocks()
                .iter()
                .map(|(bb_name, bb)| emit_basic_block(bb_name, bb, &ctx))
                .collect::<Vec<String>>()
                .join("\n    "),
            "    "
        )
    )
}

fn emit_global(name: &String, data: &Vec<u8>) -> String {
    format!(
        "{}: db {}",
        name,
        data.iter()
            .map(|x| x.to_string())
            .collect::<Vec<String>>()
            .join(", ")
    )
}

pub fn emit_program(program: &Program, header: String) -> String {
    let global_ctx = GlobalContext {
        functions: program
            .functions()
            .iter()
            .map(|(name, func)| (name.clone(), FunctionInfo::new(func)))
            .collect::<HashMap<String, FunctionInfo>>(),
    };

    formatdoc!(
        "
        {}
        ; ==================== END OF HEADER ====================

        ; GENERATED FROM SLASM VERSION {}

            section .data
        {}

            section .text
        {}
        ",
        header.replace("#ENTRY_FUNC_NAME#", program.entry().as_str()),
        VERSION,
        program
            .globals()
            .iter()
            .map(|(name, data)| emit_global(name, data))
            .collect::<Vec<String>>()
            .join("\n"),
        program
            .functions()
            .iter()
            .map(|(_, function)| emit_function(function, &global_ctx))
            .collect::<Vec<String>>()
            .join("\n")
    )
}
