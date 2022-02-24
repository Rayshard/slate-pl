use crate::slasm::instruction::Instruction;
use crate::slasm::prelude::VERSION;
use crate::slasm::program::Program;
use crate::Function;
use std::io::Write;
use xml::writer::{EventWriter, XmlEvent};

pub fn emit_instruction<W: Write>(instr: &Instruction, writer: &mut EventWriter<W>) {
    match instr {
        Instruction::Noop => writer.write(XmlEvent::start_element("NOOP")).unwrap(),
        Instruction::Or => writer.write(XmlEvent::start_element("OR")).unwrap(),
        Instruction::And => writer.write(XmlEvent::start_element("AND")).unwrap(),
        Instruction::Xor => writer.write(XmlEvent::start_element("XOR")).unwrap(),
        Instruction::Not => writer.write(XmlEvent::start_element("NOT")).unwrap(),
        Instruction::Shl => writer.write(XmlEvent::start_element("SHL")).unwrap(),
        Instruction::Shr => writer.write(XmlEvent::start_element("SHR")).unwrap(),
        Instruction::Ret => writer.write(XmlEvent::start_element("RET")).unwrap(),
        Instruction::Push { data } => writer
            .write(XmlEvent::start_element("PUSH").attr("data", &hex::encode_upper(data)))
            .unwrap(),
        Instruction::Pop { amt } => writer
            .write(XmlEvent::start_element("POP").attr("amt", &amt.to_string()))
            .unwrap(),
        Instruction::LoadLocal { name } => writer
            .write(XmlEvent::start_element("LOAD_LOCAL").attr("name", name))
            .unwrap(),
        Instruction::StoreLocal { name } => writer
            .write(XmlEvent::start_element("STORE_LOCAL").attr("name", name))
            .unwrap(),
        Instruction::LoadParam { name } => writer
            .write(XmlEvent::start_element("LOAD_PARAM").attr("name", name))
            .unwrap(),
        Instruction::StoreParam { name } => writer
            .write(XmlEvent::start_element("STORE_PARAM").attr("name", name))
            .unwrap(),
        Instruction::LoadGlobal { name } => writer
            .write(XmlEvent::start_element("LOAD_GLOBAL").attr("name", name))
            .unwrap(),
        Instruction::StoreGlobal { name } => writer
            .write(XmlEvent::start_element("STORE_GLOBAL").attr("name", name))
            .unwrap(),
        Instruction::LoadMem { offset } => writer
            .write(XmlEvent::start_element("LOAD_MEM").attr("offset", &offset.to_string()))
            .unwrap(),
        Instruction::StoreMem { offset } => writer
            .write(XmlEvent::start_element("STORE_MEM").attr("offset", &offset.to_string()))
            .unwrap(),
        Instruction::Add { data_type } => writer
            .write(XmlEvent::start_element("ADD").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Sub { data_type } => writer
            .write(XmlEvent::start_element("SUB").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Mul { data_type } => writer
            .write(XmlEvent::start_element("MUL").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Div { data_type } => writer
            .write(XmlEvent::start_element("Div").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Mod { data_type } => writer
            .write(XmlEvent::start_element("MOD").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Inc { data_type } => writer
            .write(XmlEvent::start_element("INC").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Dec { data_type } => writer
            .write(XmlEvent::start_element("DEC").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Eq { data_type } => writer
            .write(XmlEvent::start_element("EQ").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Neq { data_type } => writer
            .write(XmlEvent::start_element("NEQ").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Gt { data_type } => writer
            .write(XmlEvent::start_element("GT").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Lt { data_type } => writer
            .write(XmlEvent::start_element("LT").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::GtEq { data_type } => writer
            .write(XmlEvent::start_element("GTEQ").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::LtEq { data_type } => writer
            .write(XmlEvent::start_element("LTEQ").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Neg { data_type } => writer
            .write(XmlEvent::start_element("NEG").attr("data_type", &data_type.to_string()))
            .unwrap(),
        Instruction::Convert { dt_from, dt_to } => writer
            .write(
                XmlEvent::start_element("CONVERT")
                    .attr("from", &dt_from.to_string())
                    .attr("to", &dt_to.to_string()),
            )
            .unwrap(),
        Instruction::Jump { target } => writer
            .write(XmlEvent::start_element("JUMP").attr("target", target))
            .unwrap(),
        Instruction::CondJump { target } => writer
            .write(XmlEvent::start_element("COND_JUMP").attr("target", target))
            .unwrap(),
        Instruction::Call { target } => writer
            .write(XmlEvent::start_element("Call").attr("target", target))
            .unwrap(),
        Instruction::IndirectCall {
            num_params,
            num_returns,
        } => writer
            .write(
                XmlEvent::start_element("INDIRECT_CALL")
                    .attr("num_params", &num_params.to_string())
                    .attr("num_returns", &num_returns.to_string()),
            )
            .unwrap(),
        _ => todo!("{:?}", instr),
    }
    writer.write(XmlEvent::end_element()).unwrap();
}

pub fn emit_function<W: Write>(function: &Function, writer: &mut EventWriter<W>) {
    writer
        .write(
            XmlEvent::start_element("function")
                .attr("name", function.name())
                .attr("num_returns", &function.num_returns().to_string())
                .attr("entry", function.entry()),
        )
        .unwrap();

    for param in function.params() {
        writer
            .write(XmlEvent::start_element("param").attr("name", param))
            .unwrap();

        writer.write(XmlEvent::end_element()).unwrap();
    }

    for local in function.locals() {
        writer
            .write(XmlEvent::start_element("local").attr("name", local))
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

    // Emit data
    for (label, data) in program.data() {
        writer
            .write(
                XmlEvent::start_element("data")
                    .attr("label", label)
                    .attr("bytes", &hex::encode_upper(data)),
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
