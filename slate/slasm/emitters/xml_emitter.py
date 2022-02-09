import xml.etree.ElementTree as ET
import xml.dom.minidom
from typing import Any, Callable, Dict
from slate.slasm.function import Function
from slate.slasm.instruction import ADD, DIV, LOAD_CONST, LOAD_FUNC_ADDR, LOAD_GLOBAL, LOAD_LOCAL, LOAD_MEM, LOAD_PARAM, MOD, MUL, NATIVE_CALL, NOOP, POP, RET, STORE_GLOBAL, STORE_LOCAL, STORE_MEM, STORE_PARAM, SUB, Instruction, OpCode
from slate.slasm.program import Program
from slate.slasm.slasm import VERSION, DataType, Word

def __emit_NOOP(instr: NOOP) -> ET.Element:
    return ET.Element("NOOP")

def __emit_LOAD_CONST(instr: LOAD_CONST) -> ET.Element:
    return ET.Element("LOAD_CONST", {"value": instr.value.as_hex()})

def __emit_LOAD_FUNC_ADDR(instr: LOAD_FUNC_ADDR) -> ET.Element:
    return ET.Element("LOAD_FUNC_ADDR", {"name": instr.func_name})

def __emit_LOAD_LOCAL(instr: LOAD_LOCAL) -> ET.Element:
    return ET.Element("LOAD_LOCAL", {"idx": str(instr.idx)})

def __emit_LOAD_PARAM(instr: LOAD_PARAM) -> ET.Element:
    return ET.Element("LOAD_PARAM", {"idx": str(instr.idx)})

def __emit_LOAD_GLOBAL(instr: LOAD_GLOBAL) -> ET.Element:
    return ET.Element("LOAD_GLOBAL", {"name": instr.name})

def __emit_LOAD_MEM(instr: LOAD_MEM) -> ET.Element:
    return ET.Element("LOAD_MEM", {"offset": str(instr.offset)})
    
def __emit_STORE_LOCAL(instr: STORE_LOCAL) -> ET.Element:
    return ET.Element("STORE_LOCAL", {"idx": str(instr.idx)})

def __emit_STORE_PARAM(instr: STORE_PARAM) -> ET.Element:
    return ET.Element("STORE_PARAM", {"idx": str(instr.idx)})

def __emit_STORE_GLOBAL(instr: STORE_GLOBAL) -> ET.Element:
    return ET.Element("STORE_GLOBAL", {"name": instr.name})

def __emit_STORE_MEM(instr: STORE_MEM) -> ET.Element:
    return ET.Element("STORE_MEM", {"offset": str(instr.offset)})

def __emit_POP(instr: POP) -> ET.Element:
    return ET.Element("POP")

def __emit_ADD(instr: ADD) -> ET.Element:
    return ET.Element("ADD", {"type": str(instr.data_type.name)})

def __emit_SUB(instr: SUB) -> ET.Element:
    return ET.Element("SUB", {"type": str(instr.data_type.name)})

def __emit_MUL(instr: MUL) -> ET.Element:
    return ET.Element("MUL", {"type": str(instr.data_type.name)})

def __emit_DIV(instr: DIV) -> ET.Element:
    return ET.Element("DIV", {"type": str(instr.data_type.name)})

def __emit_MOD(instr: MOD) -> ET.Element:
    return ET.Element("MOD", {"type": str(instr.data_type.name)})

def __emit_NATIVE_CALL(instr: NATIVE_CALL) -> ET.Element:
    return ET.Element("NATIVE_CALL", {"target": instr.target, "num_params": str(instr.num_params), "returns_value": str(instr.returns_value)})

def __emit_RET(instr: RET) -> ET.Element:
    return ET.Element("RET")

__TRANSLATORS : Dict[Any, Callable[..., ET.Element]] = {
    OpCode.NOOP: __emit_NOOP,
    OpCode.LOAD_CONST: __emit_LOAD_CONST,
    OpCode.LOAD_LOCAL: __emit_LOAD_LOCAL,
    OpCode.LOAD_PARAM: __emit_LOAD_PARAM,
    OpCode.LOAD_GLOBAL: __emit_LOAD_GLOBAL,
    OpCode.LOAD_MEM: __emit_LOAD_MEM,
    OpCode.STORE_LOCAL: __emit_STORE_LOCAL,
    OpCode.STORE_PARAM: __emit_STORE_PARAM,
    OpCode.STORE_GLOBAL: __emit_STORE_GLOBAL,
    OpCode.STORE_MEM: __emit_STORE_MEM,
    OpCode.POP: __emit_POP,
    OpCode.ADD: __emit_ADD,
    OpCode.SUB: __emit_SUB,
    OpCode.MUL: __emit_MUL,
    OpCode.DIV: __emit_DIV,
    OpCode.MOD: __emit_MOD,
    OpCode.NATIVE_CALL: __emit_NATIVE_CALL,
    OpCode.RET: __emit_RET,
    OpCode.LOAD_FUNC_ADDR: __emit_LOAD_FUNC_ADDR,
}

def emit_Instruction(instr: Instruction) -> ET.Element:
    if instr.opcode not in __TRANSLATORS:
        raise NotImplementedError(instr.opcode)

    return __TRANSLATORS[instr.opcode](instr)

def emit_Function(function: Function) -> ET.Element:
    element = ET.Element("function", {"name": function.name,
                                      "params": str(function.num_params),
                                      "locals": str(function.num_locals),
                                      "entry": function.entry
                                      })

    for label, bb in function.basic_blocks:
        bb_elem = ET.Element("BasicBlock", {"label": label})
        
        for instr in bb:
            bb_elem.append(emit_Instruction(instr))

        element.append(bb_elem)

    return element

def emit_Program(program: Program) -> ET.Element:
    document = ET.Element("program", {"slasm_version": VERSION(), "target": program.target})
    code = ET.SubElement(document, "code", {"entry": program.entry})

    for function in program.functions:
        code.append(emit_Function(function))

    return document

def to_string(element: ET.Element) -> str:
    return xml.dom.minidom.parseString(ET.tostring(element, 'unicode')).toprettyxml(indent='    ')
