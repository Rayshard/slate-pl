import xml.etree.ElementTree as ET
import xml.dom.minidom
from typing import Any, Callable, Dict
from slasm.function import Function
from slasm.instruction import Instruction, OpCode
from slasm.program import Program
from slasm.slasm import VERSION, DataType, Word

def __translate_InstrNoop(instr: Instruction) -> ET.Element:
    return ET.Element("NOOP")

def __translate_InstrLoadConst(instr: Instruction) -> ET.Element:
    return ET.Element("LOAD_CONST", {"value": instr.get_operand(0, Word).as_hex()})

def __translate_InstrInlineNasm(instr: Instruction) -> ET.Element:
    return ET.Element("INLINE_NASM", {"asm": instr.get_operand(0, str)})

def __translate_InstrRet(instr: Instruction) -> ET.Element:
    return ET.Element("RET")

def __translate_InstrLoadLabel(instr: Instruction) -> ET.Element:
    return ET.Element("LOAD_LABEL", {"label": instr.get_operand(0, str)})

def __translate_InstrLoadLocal(instr: Instruction) -> ET.Element:
    return ET.Element("LOAD_LOCAL", {"idx": str(instr.get_operand(0, Word).as_ui64())})

def __translate_InstrLoadParam(instr: Instruction) -> ET.Element:
    return ET.Element("LOAD_PARAM", {"idx": str(instr.get_operand(0, Word).as_ui64())})

def __translate_InstrLoadGlobal(instr: Instruction) -> ET.Element:
    return ET.Element("LOAD_GLOBAL", {"name": instr.get_operand(0, str)})

def __translate_InstrLoadMem(instr: Instruction) -> ET.Element:
    return ET.Element("LOAD_MEM", {"offset": str(instr.get_operand(0, Word).as_i64())})
    
def __translate_InstrStoreLocal(instr: Instruction) -> ET.Element:
    return ET.Element("STORE_LOCAL", {"idx": str(instr.get_operand(0, Word).as_ui64())})

def __translate_InstrStoreParam(instr: Instruction) -> ET.Element:
    return ET.Element("STORE_PARAM", {"idx": str(instr.get_operand(0, Word).as_ui64())})

def __translate_InstrStoreGlobal(instr: Instruction) -> ET.Element:
    return ET.Element("STORE_GLOBAL", {"name": instr.get_operand(0, str)})

def __translate_InstrStoreMem(instr: Instruction) -> ET.Element:
    return ET.Element("STORE_MEM", {"offset": str(instr.get_operand(0, Word).as_i64())})

def __translate_InstrPop(instr: Instruction) -> ET.Element:
    return ET.Element("POP")

def __translate_InstrAdd(instr: Instruction) -> ET.Element:
    return ET.Element("ADD", {"type": str(instr.get_operand(0, DataType).name)})

def __translate_InstrSub(instr: Instruction) -> ET.Element:
    return ET.Element("SUB", {"type": str(instr.get_operand(0, DataType).name)})

def __translate_InstrMul(instr: Instruction) -> ET.Element:
    return ET.Element("MUL", {"type": str(instr.get_operand(0, DataType).name)})

def __translate_InstrDiv(instr: Instruction) -> ET.Element:
    return ET.Element("DIV", {"type": str(instr.get_operand(0, DataType).name)})

def __translate_InstrMod(instr: Instruction) -> ET.Element:
    return ET.Element("MOD", {"type": str(instr.get_operand(0, DataType).name)})

__TRANSLATORS : Dict[Any, Callable[..., ET.Element]] = {
    OpCode.NOOP: __translate_InstrNoop,
    OpCode.LOAD_CONST: __translate_InstrLoadConst,
    OpCode.INLINE_NASM: __translate_InstrInlineNasm,
    OpCode.RET: __translate_InstrRet,
    OpCode.LOAD_LABEL: __translate_InstrLoadLabel,
    OpCode.LOAD_LOCAL: __translate_InstrLoadLocal,
    OpCode.LOAD_PARAM: __translate_InstrLoadParam,
    OpCode.LOAD_GLOBAL: __translate_InstrLoadGlobal,
    OpCode.LOAD_MEM: __translate_InstrLoadMem,
    OpCode.STORE_LOCAL: __translate_InstrStoreLocal,
    OpCode.STORE_PARAM: __translate_InstrStoreParam,
    OpCode.STORE_GLOBAL: __translate_InstrStoreGlobal,
    OpCode.STORE_MEM: __translate_InstrStoreMem,
    OpCode.POP: __translate_InstrPop,
    OpCode.ADD: __translate_InstrAdd,
    OpCode.SUB: __translate_InstrSub,
    OpCode.MUL: __translate_InstrMul,
    OpCode.DIV: __translate_InstrDiv,
    OpCode.MOD: __translate_InstrMod,
}

def translate_Instruction(instr: Instruction) -> ET.Element:
    if instr.opcode not in __TRANSLATORS:
        raise NotImplementedError(instr.opcode)

    return __TRANSLATORS[instr.opcode](instr)

def translate_Function(function: Function) -> ET.Element:
    element = ET.Element("function", {"name": function.name, "params": str(function.num_params), "locals": str(function.num_locals)})

    for elem in function.code:
        if isinstance(elem, Instruction):
            element.append(translate_Instruction(elem))
        else:
            element.append(ET.Element("LABEL", {"name": elem}))

    return element

def translate_Program(program: Program) -> ET.Element:
    document = ET.Element("program", {"slasm_version": VERSION(), "target": program.target})
    code = ET.SubElement(document, "code", {"entry": program.entry})

    for function in program.functions:
        code.append(translate_Function(function))

    return document

def to_string(element: ET.Element) -> str:
    return xml.dom.minidom.parseString(ET.tostring(element, 'unicode')).toprettyxml(indent='    ')
