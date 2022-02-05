from typing import Any, Callable, Dict
from slasm.function import Function
from slasm.instruction import Instruction, OpCode
from slasm.program import Program
from slasm.slasm import VERSION, DataType, Word

from llvmlite import ir # type: ignore

LLVMTypeI64 = ir.IntType(64)

def __translate_InstrNoop(instr: Instruction) -> ir.Value:
    assert False, "Not implemented"

def __translate_InstrLoadConst(instr: Instruction) -> ir.Value:
    assert False, "Not implemented"

def __translate_InstrInlineLLVM(instr: Instruction) -> ir.Value:
    return instr.get_operand(0, ir.Value)

def __translate_InstrRet(instr: Instruction) -> ir.Value:
    assert False, "Not implemented"

def __translate_InstrLoadLabel(instr: Instruction) -> ir.Value:
    assert False, "Not implemented"

def __translate_InstrLoadLocal(instr: Instruction) -> ir.Value:
    assert False, "Not implemented"

def __translate_InstrLoadParam(instr: Instruction) -> ir.Value:
    assert False, "Not implemented"

def __translate_InstrLoadGlobal(instr: Instruction) -> ir.Value:
    assert False, "Not implemented"

def __translate_InstrLoadMem(instr: Instruction) -> ir.Value:
    assert False, "Not implemented"
    
def __translate_InstrStoreLocal(instr: Instruction) -> ir.Value:
    assert False, "Not implemented"

def __translate_InstrStoreParam(instr: Instruction) -> ir.Value:
    assert False, "Not implemented"

def __translate_InstrStoreGlobal(instr: Instruction) -> ir.Value:
    assert False, "Not implemented"

def __translate_InstrStoreMem(instr: Instruction) -> ir.Value:
    assert False, "Not implemented"

def __translate_InstrPop(instr: Instruction) -> ir.Value:
    assert False, "Not implemented"

def __translate_InstrAdd(instr: Instruction) -> ir.Value:
    assert False, "Not implemented"

def __translate_InstrSub(instr: Instruction) -> ir.Value:
    assert False, "Not implemented"

def __translate_InstrMul(instr: Instruction) -> ir.Value:
    assert False, "Not implemented"

def __translate_InstrDiv(instr: Instruction) -> ir.Value:
    assert False, "Not implemented"

def __translate_InstrMod(instr: Instruction) -> ir.Value:
    assert False, "Not implemented"

__TRANSLATORS : Dict[Any, Callable[..., ir.Value]] = {
    OpCode.NOOP: __translate_InstrNoop,
    OpCode.LOAD_CONST: __translate_InstrLoadConst,
    OpCode.INLINE_LLVM: __translate_InstrInlineLLVM,
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

def translate_Instruction(instr: Instruction) -> ir.Value:
    if instr.opcode not in __TRANSLATORS:
        raise NotImplementedError(instr.opcode)

    return __TRANSLATORS[instr.opcode](instr)

def translate_Function(function: Function, module: ir.Module) -> ir.Function:
    entry_func_type = ir.FunctionType(LLVMTypeI64, ())
    entry_func = ir.Function(ir_module, entry_func_type, module.get_path() + "#entry")
    start_block = entry_func.append_basic_block("start")
    builder = ir.IRBuilder(start_block)

    last_value = ir.Constant(TypeI64, 0)

    for node in module.get_nodes():
        last_value = __visit_ASTNode(node, builder)

    builder.ret(last_value)
    
    # element = ET.Element("function", {"name": function.name, "params": str(function.num_params), "locals": str(function.num_locals)})

    # for elem in function.code:
    #     if isinstance(elem, Instruction):
    #         element.append(translate_Instruction(elem))
    #     else:
    #         element.append(ET.Element("LABEL", {"name": elem}))

    # return element

def translate_Program(program: Program) -> ir.Module:
    ir_module = ir.Module(name="")
    
    return ir_module
    
    document = ET.Element("program", {"slasm_version": VERSION(), "target": program.target})
    code = ET.SubElement(document, "code", {"entry": program.entry})

    for function in program.functions:
        code.append(translate_Function(function))

    return document
