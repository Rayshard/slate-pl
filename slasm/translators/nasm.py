from typing import Any, Callable, Dict
from slasm.function import Function
from slasm.instruction import Instruction, OpCode
from slasm.program import Program
from slasm.slasm import VERSION, DataType, Word

def __translate_InstrNoop(instr: Instruction) -> str:
    return "; NOOP\n" \
            "XCHG RAX, RAX"

def __translate_InstrLoadConst(instr: Instruction) -> str:
    value_hex = instr.get_operand(0, Word).as_hex()
    
    return f"; LOAD_CONST {value_hex}\n" \
           f"MOV RAX, {value_hex}\n" \
            "PUSH RAX"

def __translate_InstrInlineNasm(instr: Instruction) -> str:
    return f"; NATIVE ASSEMBLY\n{instr.get_operand(0, str)}"

def __translate_InstrRet(instr: Instruction) -> str:
    return "; RET\n" \
           "RET"

def __translate_InstrLoadLabel(instr: Instruction) -> str:
    label = instr.get_operand(0, str)
    
    return f"; LOAD_LABEL {label}\n" \
           f"LEA RAX, [REL .{label}]\n" \
            "PUSH RAX"

def __translate_InstrLoadLocal(instr: Instruction) -> str:
    idx = instr.get_operand(0, Word).as_ui64()
    
    return f"; LOAD_LOCAL {idx}\n" \
           f"PUSH QWORD [RBP-{(idx + 1) * Word.SIZE()}]"

def __translate_InstrLoadParam(instr: Instruction) -> str:
    idx = instr.get_operand(0, Word).as_ui64()
    
    return f"; LOAD_PARAM {idx}\n" \
           f"PUSH QWORD [RBP+{(idx + 2) * Word.SIZE()}]"

def __translate_InstrLoadGlobal(instr: Instruction) -> str:
    name = instr.get_operand(0, str)
    
    return f"; LOAD_GLOBAL {name}\n" \
           f"PUSH QWORD [REL {name}]"

def __translate_InstrLoadMem(instr: Instruction) -> str:
    offset = instr.get_operand(0, Word).as_i64()
    sign = "-" if offset < 0 else "+"
    
    return f"; LOAD_MEM {offset}\n" \
            "POP RAX\n" \
           f"PUSH QWORD [RAX{sign}{offset}]"
    
def __translate_InstrStoreLocal(instr: Instruction) -> str:
    idx = instr.get_operand(0, Word).as_ui64()
    
    return f"; STORE_LOCAL {idx}\n" \
           f"POP QWORD [RBP-{(idx + 1) * Word.SIZE()}]"

def __translate_InstrStoreParam(instr: Instruction) -> str:
    idx = instr.get_operand(0, Word).as_ui64()
    
    return f"; STORE_PARAM {idx}\n" \
           f"POP QWORD [RBP+{(idx + 2) * Word.SIZE()}]"

def __translate_InstrStoreGlobal(instr: Instruction) -> str:
    name = instr.get_operand(0, str)
    
    return f"; STORE_GLOBAL {name}\n" \
           f"POP QWORD [REL {name}]"

def __translate_InstrStoreMem(instr: Instruction) -> str:
    offset = instr.get_operand(0, Word).as_i64()
    sign = "-" if offset < 0 else "+"
    
    return f"; STORE_MEM {offset}\n" \
            "POP RAX\n" \
           f"POP QWORD [RAX{sign}{offset}]"

def __translate_InstrPop(instr: Instruction) -> str:
    return "; POP\n" \
           f"ADD RSP, {Word.SIZE()}"

def __translate_InstrAdd(instr: Instruction) -> str:
    dt = instr.get_operand(0, DataType)
    string = f"; ADD {dt.name}\n" \
                "POP RAX\n" \
                "POP RBX\n"
                
    if dt == DataType.I8 or dt == DataType.UI8:
        string += "ADD AL, BL\n"
    elif dt == DataType.I16 or dt == DataType.UI16:
        string += "ADD AX, BX\n"
    elif dt == DataType.I32 or dt == DataType.UI32:
        string += "ADD EAX, EBX\n"
    elif dt == DataType.I64 or dt == DataType.UI64:
        string += "ADD RAX, RBX\n"
    elif dt == DataType.F32:
        string += "MOVQ XMM0, RAX\n" \
                    "MOVQ XMM1, RBX\n" \
                    "ADDSS XMM0, XMM1\n" \
                    "MOVQ RAX, XMM0\n"
    elif dt == DataType.F64:
        string += "MOVQ XMM0, RAX\n" \
                    "MOVQ XMM1, RBX\n" \
                    "ADDSD XMM0, XMM1\n" \
                    "MOVQ RAX, XMM0\n"
    else:
        assert False, "Not implemented"

    string += "PUSH RAX"
    return string

def __translate_InstrSub(instr: Instruction) -> str:
    dt = instr.get_operand(0, DataType)
    string = f"; SUB {dt.name}\n" \
                "POP RAX\n" \
                "POP RBX\n"
                
    if dt == DataType.I8 or dt == DataType.UI8:
        string += "SUB AL, BL\n"
    elif dt == DataType.I16 or dt == DataType.UI16:
        string += "SUB AX, BX\n"
    elif dt == DataType.I32 or dt == DataType.UI32:
        string += "SUB EAX, EBX\n"
    elif dt == DataType.I64 or dt == DataType.UI64:
        string += "SUB RAX, RBX\n"
    elif dt == DataType.F32:
        string += "MOVQ XMM0, RAX\n" \
                    "MOVQ XMM1, RBX\n" \
                    "SUBSS XMM0, XMM1\n" \
                    "MOVQ RAX, XMM0\n"
    elif dt == DataType.F64:
        string += "MOVQ XMM0, RAX\n" \
                    "MOVQ XMM1, RBX\n" \
                    "SUBSD XMM0, XMM1\n" \
                    "MOVQ RAX, XMM0\n"
    else:
        assert False, "Not implemented"

    string += "PUSH RAX"
    return string

def __translate_InstrMul(instr: Instruction) -> str:
    dt = instr.get_operand(0, DataType)
    string = f"; MUL {dt.name}\n" \
                "POP RAX\n" \
                "POP RBX\n"
                
    if dt == DataType.I8 or dt == DataType.UI8:
        string += "IMUL AL, BL\n"
    elif dt == DataType.I16 or dt == DataType.UI16:
        string += "IMUL AX, BX\n"
    elif dt == DataType.I32 or dt == DataType.UI32:
        string += "IMUL EAX, EBX\n"
    elif dt == DataType.I64 or dt == DataType.UI64:
        string += "IMUL RAX, RBX\n"
    elif dt == DataType.F32:
        string += "MOVQ XMM0, RAX\n" \
                    "MOVQ XMM1, RBX\n" \
                    "MULSS XMM0, XMM1\n" \
                    "MOVQ RAX, XMM0\n"
    elif dt == DataType.F64:
        string += "MOVQ XMM0, RAX\n" \
                    "MOVQ XMM1, RBX\n" \
                    "MULSD XMM0, XMM1\n" \
                    "MOVQ RAX, XMM0\n"
    else:
        assert False, "Not implemented"

    string += "PUSH RAX"
    return string

def __translate_InstrDiv(instr: Instruction) -> str:
    dt = instr.get_operand(0, DataType)
    string = f"; DIV {dt.name}\n" \
                "POP RAX\n" \
                "POP RBX\n"
                
    if dt == DataType.I8:
        string += "MOVSX EAX, EAX\n" \
                    "MOVSX ECX, EBX\n" \
                    "CDQ\n" \
                    "IDIV ECX\n"
    elif dt == DataType.UI8:
        string += "MOV RDX, 0\n" \
                    "DIV BL\n"
    elif dt == DataType.I16:
        string += "MOVSX EAX, EAX\n" \
                    "MOVSX ECX, EBX\n" \
                    "CDQ\n" \
                    "IDIV ECX\n"
    elif dt == DataType.UI16:
        string += "MOV RDX, 0\n" \
                    "DIV BX\n"
    elif dt == DataType.I32:
        string += "CDQ\n" \
                    "IDIV EBX\n"
    elif dt == DataType.UI32:
        string += "MOV RDX, 0\n" \
                    "DIV EBX\n"
    elif dt == DataType.I64:
        string += "CQO\n" \
                    "IDIV RBX\n"
    elif dt == DataType.UI64:
        string += "MOV RDX, 0\n" \
                    "DIV RBX\n"
    elif dt == DataType.F32:
        string += "MOVQ XMM0, RAX\n" \
                    "MOVQ XMM1, RBX\n" \
                    "DIVSS XMM0, XMM1\n" \
                    "MOVQ RAX, XMM0\n"
    elif dt == DataType.F64:
        string += "MOVQ XMM0, RAX\n" \
                    "MOVQ XMM1, RBX\n" \
                    "DIVSD XMM0, XMM1\n" \
                    "MOVQ RAX, XMM0\n"
    else:
        assert False, "Not implemented"

    string += "PUSH RAX"
    return string

def __translate_InstrMod(instr: Instruction) -> str:
    dt = instr.get_operand(0, DataType)
    string = f"; MOD {dt.name}\n" \
                "POP RAX\n" \
                "POP RBX\n"
                
    if dt == DataType.I8:
        string += "MOVSX EAX, EAX\n" \
                    "MOVSX ECX, EBX\n" \
                    "CDQ\n" \
                    "IDIV ECX\n" \
                    "MOV EAX, EDX"
    elif dt == DataType.UI8:
        string += "MOV RDX, 0\n" \
                    "DIV BL\n" \
                    "MOV AL, BL"
    elif dt == DataType.I16:
        string += "MOVSX EAX, EAX\n" \
                    "MOVSX ECX, EBX\n" \
                    "CDQ\n" \
                    "IDIV ECX\n" \
                    "MOV AX, DX"
    elif dt == DataType.UI16:
        string += "MOV RDX, 0\n" \
                    "DIV BX\n" \
                    "MOV AX, DX"
    elif dt == DataType.I32:
        string += "CDQ\n" \
                    "IDIV EBX\n" \
                    "MOV EAX, EDX"
    elif dt == DataType.UI32:
        string += "MOV RDX, 0\n" \
                    "DIV EBX\n" \
                    "MOV EAX, EDX"
    elif dt == DataType.I64:
        string += "CQO\n" \
                    "IDIV RBX\n" \
                    "MOV RAX, RDX"
    elif dt == DataType.UI64:
        string += "MOV RDX, 0\n" \
                    "DIV RBX\n" \
                    "MOV RAX, RDX"
    elif dt == DataType.F32:
        string += "MOVQ XMM0, RAX\n" \
                    "MOVQ XMM1, RBX\n" \
                    "MOVQ XMM2, RAX\n" \
                    "DIVSS XMM2, XMM1\n" \
                    "CVTTSS2SI RAX, XMM2\n" \
                    "CVTSI2SS XMM2, RAX\n" \
                    "MULSS XMM2, XMM1\n" \
                    "SUBSS XMM0, XMM2\n" \
                    "MOVQ RAX, XMM0\n"
    elif dt == DataType.F64:
        string += "MOVQ XMM0, RAX\n" \
                    "MOVQ XMM1, RBX\n" \
                    "MOVQ XMM2, RAX\n" \
                    "DIVSD XMM2, XMM1\n" \
                    "CVTTSD2SI RAX, XMM2\n" \
                    "CVTSI2SD XMM2, RAX\n" \
                    "MULSD XMM2, XMM1\n" \
                    "SUBSD XMM0, XMM2\n" \
                    "MOVQ RAX, XMM0\n"
    else:
        assert False, "Not implemented"

    string += "PUSH RAX"
    return string

__TRANSLATORS : Dict[Any, Callable[..., str]] = {
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

def translate_Instruction(instr: Instruction) -> str:
    if instr.opcode not in __TRANSLATORS:
        raise NotImplementedError(instr.opcode)

    return __TRANSLATORS[instr.opcode](instr)

def translate_Function(function: Function) -> str:
    string = f"FUNC_{function.name}:"

    for elem in function.code:
        if isinstance(elem, Instruction):
            nasm = translate_Instruction(elem).replace('\n', '\n    ')
            string += f"\n    {nasm}"
        else:
            string += f"\n  .{elem}:"

    return string

def translate_Program(program: Program, header: str = "") -> str:
    string = f"; SLASM_VERSION {VERSION()}\n" \
             f"; TARGET {program.target}\n\n"

    string += (header + "\n\n") if len(header) != 0 else ""
    string += "    global _main\n\n    section .text"

    for function in program.functions:
        if function.name == program.entry:
            string += f"\n_main:"

        string += f"\n{translate_Function(function)}"

    return string
