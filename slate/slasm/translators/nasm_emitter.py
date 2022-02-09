from typing import Any, Callable, Dict
from slate.slasm.function import Function
from slate.slasm.instruction import Instruction, OpCode
from slate.slasm.program import Program
from slate.slasm.slasm import VERSION, DataType, Word

class FunctionContext:
    def __init__(self, returns_value: bool) -> None:
        self.__returns_value = returns_value

    @property
    def returns_value(self) -> bool:
        return self.__returns_value

def __translate_InstrNoop(instr: Instruction, ctx: FunctionContext) -> str:
    return "; NOOP\n" \
           "xchg rax, rax"

def __translate_InstrLoadConst(instr: Instruction, ctx: FunctionContext) -> str:
    value_hex = instr.get_operand(0, Word).as_hex()
    
    return f"; LOAD_CONST {value_hex}\n" \
           f"mov rax, {value_hex}\n" \
            "push rax"

def __translate_InstrLoadLabel(instr: Instruction, ctx: FunctionContext) -> str:
    label = instr.get_operand(0, str)
    
    return f"; LOAD_LABEL {label}\n" \
           f"lea rax, [rel .{label}]\n" \
            "push rax"

def __translate_InstrLoadLocal(instr: Instruction, ctx: FunctionContext) -> str:
    idx = instr.get_operand(0, Word).as_ui64()
    
    return f"; LOAD_LOCAL {idx}\n" \
           f"push qword [rbp-{(idx + 1) * Word.SIZE()}]"

def __translate_InstrLoadParam(instr: Instruction, ctx: FunctionContext) -> str:
    idx = instr.get_operand(0, Word).as_ui64()
    
    return f"; LOAD_PARAM {idx}\n" \
           f"push qword [rbp+{(idx + 2) * Word.SIZE()}]"

def __translate_InstrLoadGlobal(instr: Instruction, ctx: FunctionContext) -> str:
    name = instr.get_operand(0, str)
    
    return f"; LOAD_GLOBAL {name}\n" \
           f"push qword [rel {name}]"

def __translate_InstrLoadMem(instr: Instruction, ctx: FunctionContext) -> str:
    offset = instr.get_operand(0, Word).as_i64()
    sign = "-" if offset < 0 else "+"
    
    return f"; LOAD_MEM {offset}\n" \
            "pop rax\n" \
           f"push qword [rax{sign}{offset}]"
    
def __translate_InstrStoreLocal(instr: Instruction, ctx: FunctionContext) -> str:
    idx = instr.get_operand(0, Word).as_ui64()
    
    return f"; STORE_LOCAL {idx}\n" \
           f"pop qword [rbp-{(idx + 1) * Word.SIZE()}]"

def __translate_InstrStoreParam(instr: Instruction, ctx: FunctionContext) -> str:
    idx = instr.get_operand(0, Word).as_ui64()
    
    return f"; STORE_PARAM {idx}\n" \
           f"pop qword [rbp+{(idx + 2) * Word.SIZE()}]"

def __translate_InstrStoreGlobal(instr: Instruction, ctx: FunctionContext) -> str:
    name = instr.get_operand(0, str)
    
    return f"; STORE_GLOBAL {name}\n" \
           f"pop qword [rel {name}]"

def __translate_InstrStoreMem(instr: Instruction, ctx: FunctionContext) -> str:
    offset = instr.get_operand(0, Word).as_i64()
    sign = "-" if offset < 0 else "+"
    
    return f"; STORE_MEM {offset}\n" \
            "pop rax\n" \
           f"pop qword [rax{sign}{offset}]"

def __translate_InstrPop(instr: Instruction, ctx: FunctionContext) -> str:
    return  "; POP\n" \
           f"add rsp, {Word.SIZE()}"

def __translate_InstrAdd(instr: Instruction, ctx: FunctionContext) -> str:
    dt = instr.get_operand(0, DataType)
    string = f"; ADD {dt.name}\n" \
              "pop rax\n" \
              "pop rbx\n"
                
    if dt == DataType.I8 or dt == DataType.UI8:
        string += "add al, bl\n"
    elif dt == DataType.I16 or dt == DataType.UI16:
        string += "add ax, bx\n"
    elif dt == DataType.I32 or dt == DataType.UI32:
        string += "add eax, ebx\n"
    elif dt == DataType.I64 or dt == DataType.UI64:
        string += "add rax, rbx\n"
    elif dt == DataType.F32:
        string += "movq xmm0, rax\n" \
                  "movq xmm1, rbx\n" \
                  "addss xmm0, xmm1\n" \
                  "movq rax, xmm0\n"
    elif dt == DataType.F64:
        string += "movq xmm0, rax\n" \
                  "movq xmm1, rbx\n" \
                  "addsd xmm0, xmm1\n" \
                  "movq rax, xmm0\n"
    else:
        assert False, "Not implemented"

    string += "push rax"
    return string

def __translate_InstrSub(instr: Instruction, ctx: FunctionContext) -> str:
    dt = instr.get_operand(0, DataType)
    string = f"; SUB {dt.name}\n" \
              "pop rax\n" \
              "pop rbx\n"
                
    if dt == DataType.I8 or dt == DataType.UI8:
        string += "sub al, bl\n"
    elif dt == DataType.I16 or dt == DataType.UI16:
        string += "sub ax, bx\n"
    elif dt == DataType.I32 or dt == DataType.UI32:
        string += "sub eax, ebx\n"
    elif dt == DataType.I64 or dt == DataType.UI64:
        string += "sub rax, rbx\n"
    elif dt == DataType.F32:
        string += "movq xmm0, rax\n" \
                  "movq xmm1, rbx\n" \
                  "subss xmm0, xmm1\n" \
                  "movq rax, xmm0\n"
    elif dt == DataType.F64:
        string += "movq xmm0, rax\n" \
                  "movq xmm1, rbx\n" \
                  "subsd xmm0, xmm1\n" \
                  "movq rax, xmm0\n"
    else:
        assert False, "Not implemented"

    string += "push rax"
    return string

def __translate_InstrMul(instr: Instruction, ctx: FunctionContext) -> str:
    dt = instr.get_operand(0, DataType)
    string = f"; MUL {dt.name}\n" \
              "pop rax\n" \
              "pop rbx\n"
                
    if dt == DataType.I8 or dt == DataType.UI8:
        string += "imul al, bl\n"
    elif dt == DataType.I16 or dt == DataType.UI16:
        string += "imul ax, bx\n"
    elif dt == DataType.I32 or dt == DataType.UI32:
        string += "imul eax, ebx\n"
    elif dt == DataType.I64 or dt == DataType.UI64:
        string += "imul rax, rbx\n"
    elif dt == DataType.F32:
        string += "movq xmm0, rax\n" \
                  "movq xmm1, rbx\n" \
                  "mulss xmm0, xmm1\n" \
                  "movq rax, xmm0\n"
    elif dt == DataType.F64:
        string += "movq xmm0, rax\n" \
                  "movq xmm1, rbx\n" \
                  "mulsd xmm0, xmm1\n" \
                  "movq rax, xmm0\n"
    else:
        assert False, "Not implemented"

    string += "push rax"
    return string

def __translate_InstrDiv(instr: Instruction, ctx: FunctionContext) -> str:
    dt = instr.get_operand(0, DataType)
    string = f"; DIV {dt.name}\n" \
              "pop rax\n" \
              "pop rbx\n"
                
    if dt == DataType.I8:
        string += "movsx eax, eax\n" \
                  "movsx ecx, ebx\n" \
                  "cdq\n" \
                  "idiv ecx\n"
    elif dt == DataType.UI8:
        string += "mov rdx, 0\n" \
                  "DIV bl\n"
    elif dt == DataType.I16:
        string += "movsx eax, eax\n" \
                  "movsx ecx, ebx\n" \
                  "cdq\n" \
                  "idiv ecx\n"
    elif dt == DataType.UI16:
        string += "mov rdx, 0\n" \
                  "div BX\n"
    elif dt == DataType.I32:
        string += "cdq\n" \
                  "idiv ebx\n"
    elif dt == DataType.UI32:
        string += "mov rdx, 0\n" \
                  "div ebx\n"
    elif dt == DataType.I64:
        string += "cqo\n" \
                  "idiv rbx\n"
    elif dt == DataType.UI64:
        string += "mov rdx, 0\n" \
                  "div rbx\n"
    elif dt == DataType.F32:
        string += "movq xmm0, rax\n" \
                  "movq xmm1, rbx\n" \
                  "divss xmm0, xmm1\n" \
                  "movq rax, xmm0\n"
    elif dt == DataType.F64:
        string += "movq xmm0, rax\n" \
                  "movq xmm1, rbx\n" \
                  "divsd xmm0, xmm1\n" \
                  "movq rax, xmm0\n"
    else:
        raise NotImplementedError()

    string += "push rax"
    return string

def __translate_InstrMod(instr: Instruction, ctx: FunctionContext) -> str:
    dt = instr.get_operand(0, DataType)
    string = f"; MOD {dt.name}\n" \
              "pop rax\n" \
              "pop rbx\n"
                
    if dt == DataType.I8:
        string += "movsx eax, eax\n" \
                  "movsx ecx, ebx\n" \
                  "cdq\n" \
                  "idiv ecx\n" \
                  "mov eax, edx"
    elif dt == DataType.UI8:
        string += "mov rdx, 0\n" \
                  "div bl\n" \
                  "mov al, bl"
    elif dt == DataType.I16:
        string += "movsx eax, eax\n" \
                  "movsx ecx, ebx\n" \
                  "cdq\n" \
                  "idiv ecx\n" \
                  "mov ax, dx"
    elif dt == DataType.UI16:
        string += "mov rdx, 0\n" \
                  "div bx\n" \
                  "mov ax, dx"
    elif dt == DataType.I32:
        string += "cdq\n" \
                  "idiv ebx\n" \
                  "mov eax, edx"
    elif dt == DataType.UI32:
        string += "mov rdx, 0\n" \
                  "div ebx\n" \
                  "mov eax, edx"
    elif dt == DataType.I64:
        string += "cqo\n" \
                  "idiv rbx\n" \
                  "mov rax, rdx"
    elif dt == DataType.UI64:
        string += "mov rdx, 0\n" \
                  "div rbx\n" \
                  "mov rax, rdx"
    elif dt == DataType.F32:
        string += "movq xmm0, rax\n" \
                  "movq xmm1, rbx\n" \
                  "movq xmm2, rax\n" \
                  "divss xmm2, xmm1\n" \
                  "cvttss2si rax, xmm2\n" \
                  "cvtsi2ss xmm2, rax\n" \
                  "mulss xmm2, xmm1\n" \
                  "subss xmm0, xmm2\n" \
                  "movq rax, xmm0\n"
    elif dt == DataType.F64:
        string += "movq xmm0, rax\n" \
                  "movq xmm1, rbx\n" \
                  "movq xmm2, rax\n" \
                  "divsd xmm2, xmm1\n" \
                  "cvttsd2si rax, xmm2\n" \
                  "cvtsi2sd xmm2, rax\n" \
                  "mulsd xmm2, xmm1\n" \
                  "subsd xmm0, xmm2\n" \
                  "movq rax, xmm0\n"
    else:
        assert False, "Not implemented"

    string += "push rax"
    return string

def __translate_InstrNativeCall(instr: Instruction, ctx: FunctionContext) -> str:
    target, num_params, returns_value = instr.get_operand(0, str), instr.get_operand(1, int), instr.get_operand(2, bool)
    string = f"; NATIVE CALL\n" \
             f"call {target}\n"

    if num_params != 0:
        string += f"add rsp, {num_params * Word.SIZE()} ; remove arguments from stack"
        
    if returns_value:
        string += "push rax ; push return value"
    
    return string

def __translate_InstrRet(instr: Instruction, ctx: FunctionContext) -> str:
    string = "; RET\n"

    if ctx.returns_value:
        string += "pop rax\n"
    
    string += "ret"
    return string

__INSTRUCTION_TRANSLATORS : Dict[OpCode, Callable[[Instruction, FunctionContext], str]] = {
    OpCode.NOOP: __translate_InstrNoop,
    OpCode.LOAD_CONST: __translate_InstrLoadConst,
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
    OpCode.NATIVE_CALL: __translate_InstrNativeCall,
    OpCode.RET: __translate_InstrRet,
}

def translate_Instruction(instr: Instruction, ctx: FunctionContext) -> str:
    if instr.opcode not in __INSTRUCTION_TRANSLATORS:
        raise NotImplementedError(instr.opcode)

    return __INSTRUCTION_TRANSLATORS[instr.opcode](instr, ctx)

def translate_Function(function: Function) -> str:
    ctx = FunctionContext(function.returns_value)
    string = f"{function.name}:"

    for label, bb in function.basic_blocks:
        string += f"\n  .{label}:"

        for instr in bb:
            nasm = translate_Instruction(instr, ctx).replace('\n', '\n    ')
            string += f"\n    {nasm}"

    return string

def translate_Program(program: Program, global_header: str = "", text_section_header: str = "") -> str:
    string = f"; SLASM_VERSION {VERSION()}\n" \
             f"; TARGET {program.target}\n\n"

    string += (global_header + "\n\n") if len(global_header) != 0 else ""
    string += f"    global _main\n\n    section .text\n_main:\n    call {program.entry}\n    ret ; note that rax alreeady contains the exit code from previous call instruction\n"
    string += text_section_header if len(text_section_header) != 0 else ""

    for function in program.functions:
        string += f"\n{translate_Function(function)}"

    return string
