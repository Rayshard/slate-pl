use crate::slasm::instruction::Instruction;
use crate::slasm::prelude::VERSION;
use crate::slasm::program::Program;
use crate::Function;
use std::io::Write;
use xml::writer::{EventWriter, XmlEvent};

pub fn emit_instruction<W: Write>(instr: &Instruction, writer: &mut EventWriter<W>) {
    match instr {
        Instruction::Noop => writer.write(XmlEvent::start_element("noop")).unwrap(),
        Instruction::Or => writer.write(XmlEvent::start_element("or")).unwrap(),
        Instruction::And => writer.write(XmlEvent::start_element("and")).unwrap(),
        Instruction::Xor => writer.write(XmlEvent::start_element("xor")).unwrap(),
        Instruction::Not => writer.write(XmlEvent::start_element("not")).unwrap(),
        Instruction::Shl => writer.write(XmlEvent::start_element("shl")).unwrap(),
        Instruction::Shr => writer.write(XmlEvent::start_element("shr")).unwrap(),
        Instruction::Ret => writer.write(XmlEvent::start_element("ret")).unwrap(),
        Instruction::Push { data } => writer
            .write(
                XmlEvent::start_element("push").attr(
                    "data",
                    &data
                        .iter()
                        .map(|x| format!("{:02x}", x).to_uppercase())
                        .collect::<Vec<String>>()
                        .join(":"),
                ),
            )
            .unwrap(),
        Instruction::Pop { amt } => writer
            .write(XmlEvent::start_element("pop").attr("amt", &amt.to_string()))
            .unwrap(),
        Instruction::LoadLocal { name } => writer
            .write(XmlEvent::start_element("load_local").attr("name", name))
            .unwrap(),
        Instruction::StoreLocal { name } => writer
            .write(XmlEvent::start_element("store_local").attr("name", name))
            .unwrap(),
        Instruction::LoadParam { name } => writer
            .write(XmlEvent::start_element("load_param").attr("name", name))
            .unwrap(),
        Instruction::StoreParam { name } => writer
            .write(XmlEvent::start_element("store_param").attr("name", name))
            .unwrap(),
        Instruction::LoadGlobal { name } => writer
            .write(XmlEvent::start_element("load_global").attr("name", name))
            .unwrap(),
        Instruction::StoreGlobal { name } => writer
            .write(XmlEvent::start_element("store_global").attr("name", name))
            .unwrap(),
        Instruction::LoadMem { offset } => writer
            .write(XmlEvent::start_element("load_mem").attr("offset", &offset.to_string()))
            .unwrap(),
        Instruction::StoreMem { offset } => writer
            .write(XmlEvent::start_element("store_mem").attr("offset", &offset.to_string()))
            .unwrap(),
        Instruction::LoadLocalAddr { name } => writer
            .write(XmlEvent::start_element("load_local_addr").attr("name", name))
            .unwrap(),
        Instruction::LoadParamAddr { name } => writer
            .write(XmlEvent::start_element("load_param_addr").attr("name", name))
            .unwrap(),
        Instruction::LoadGlobalAddr { name } => writer
            .write(XmlEvent::start_element("load_global_addr").attr("name", name))
            .unwrap(),
        Instruction::LoadFuncAddr { name } => writer
            .write(XmlEvent::start_element("load_func_addr").attr("name", name))
            .unwrap(),
        Instruction::Add { data_type } => writer
            .write(XmlEvent::start_element("add").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Sub { data_type } => writer
            .write(XmlEvent::start_element("sub").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Mul { data_type } => writer
            .write(XmlEvent::start_element("mul").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Div { data_type } => writer
            .write(XmlEvent::start_element("div").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Mod { data_type } => writer
            .write(XmlEvent::start_element("mod").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Inc { data_type } => writer
            .write(XmlEvent::start_element("inc").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Dec { data_type } => writer
            .write(XmlEvent::start_element("dec").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Eq { data_type } => writer
            .write(XmlEvent::start_element("eq").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Neq { data_type } => writer
            .write(XmlEvent::start_element("neq").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Gt { data_type } => writer
            .write(XmlEvent::start_element("gt").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Lt { data_type } => writer
            .write(XmlEvent::start_element("lt").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::GtEq { data_type } => writer
            .write(XmlEvent::start_element("gteq").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::LtEq { data_type } => writer
            .write(XmlEvent::start_element("lteq").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Neg { data_type } => writer
            .write(XmlEvent::start_element("neg").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Convert { dt_from, dt_to } => writer
            .write(
                XmlEvent::start_element("convert")
                    .attr("from", &dt_from.to_string())
                    .attr("to", &dt_to.to_string()),
            )
            .unwrap(),
        Instruction::Jump { target } => writer
            .write(XmlEvent::start_element("jump").attr("target", target))
            .unwrap(),
        Instruction::CondJump { target } => writer
            .write(XmlEvent::start_element("cond_jump").attr("target", target))
            .unwrap(),
        Instruction::Call { target } => writer
            .write(XmlEvent::start_element("call").attr("target", target))
            .unwrap(),
        Instruction::IndirectCall {
            param_buffer_size,
            ret_buffer_size,
        } => writer
            .write(
                XmlEvent::start_element("indirect_call")
                    .attr("param_buffer_size", &param_buffer_size.to_string())
                    .attr("ret_buffer_size", &ret_buffer_size.to_string()),
            )
            .unwrap(),
    }
    writer.write(XmlEvent::end_element()).unwrap();
}

pub fn emit_function<W: Write>(function: &Function, writer: &mut EventWriter<W>) {
    writer
        .write(
            XmlEvent::start_element("function")
                .attr("name", function.name())
                .attr("ret_buffer_size", &function.ret_buffer_size().to_string())
                .attr("entry", function.entry()),
        )
        .unwrap();

    for (name, size) in function.params() {
        writer
            .write(
                XmlEvent::start_element("param")
                    .attr("name", name)
                    .attr("size", &size.to_string()),
            )
            .unwrap();

        writer.write(XmlEvent::end_element()).unwrap();
    }

    for (name, size) in function.locals() {
        writer
            .write(
                XmlEvent::start_element("local")
                    .attr("name", name)
                    .attr("size", &size.to_string()),
            )
            .unwrap();

        writer.write(XmlEvent::end_element()).unwrap();
    }

    for (label, bb) in function.basic_blocks() {
        writer
            .write(XmlEvent::start_element("basic_block").attr("label", label))
            .unwrap();

        for instr in bb.iter() {
            emit_instruction(instr, writer);
        }

        writer.write(XmlEvent::end_element()).unwrap();
    }

    writer.write(XmlEvent::end_element()).unwrap();
}

pub fn emit_program<W: Write>(program: &Program, writer: &mut EventWriter<W>) {
    writer
        .write(
            XmlEvent::start_element("program")
                .attr("slasm_version", VERSION)
                .attr("entry", program.entry()),
        )
        .unwrap();

    // Emit globals
    for (name, data) in program.globals() {
        writer
            .write(
                XmlEvent::start_element("global").attr("name", name).attr(
                    "data",
                    &data
                        .iter()
                        .map(|x| format!("{:02x}", x).to_uppercase())
                        .collect::<Vec<String>>()
                        .join(":"),
                ),
            )
            .unwrap();

        writer.write(XmlEvent::end_element()).unwrap();
    }

    // Emit functions
    for (_, function) in program.functions() {
        emit_function(function, writer);
    }

    writer.write(XmlEvent::end_element()).unwrap();
}
