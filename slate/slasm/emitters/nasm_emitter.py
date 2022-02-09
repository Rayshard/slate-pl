from typing import Any, Callable, Dict
from slate.slasm.function import Function
from slate.slasm.instruction import ADD, DIV, LOAD_CONST, LOAD_FUNC_ADDR, LOAD_GLOBAL, LOAD_LOCAL, LOAD_MEM, LOAD_PARAM, MOD, MUL, NATIVE_CALL, NOOP, POP, RET, STORE_GLOBAL, STORE_LOCAL, STORE_MEM, STORE_PARAM, SUB, Instruction, OpCode
from slate.slasm.program import Program
from slate.slasm.slasm import VERSION, DataType, Word

class FunctionContext:
    def __init__(self, returns_value: bool) -> None:
        self.__returns_value = returns_value

    @property
    def returns_value(self) -> bool:
        return self.__returns_value

def __emit_NOOP(instr: NOOP, ctx: FunctionContext) -> str:
    return "; NOOP\n" \
           "xchg rax, rax"

def __emit_LOAD_CONST(instr: LOAD_CONST, ctx: FunctionContext) -> str:
    value_hex = instr.value.as_hex()
    
    return f"; LOAD_CONST {value_hex}\n" \
           f"mov rax, {value_hex}\n" \
            "push rax"

def __emit_LOAD_FUNC_ADDR(instr: LOAD_FUNC_ADDR, ctx: FunctionContext) -> str:
    return f"; LOAD_FUNC_ADDR {instr.func_name}\n" \
           f"lea rax, [rel .{instr.func_name}]\n" \
            "push rax"

def __emit_LOAD_LOCAL(instr: LOAD_LOCAL, ctx: FunctionContext) -> str:
    return f"; LOAD_LOCAL {instr.idx}\n" \
           f"push qword [rbp-{(instr.idx + 1) * Word.SIZE()}]"

def __emit_LOAD_PARAM(instr: LOAD_PARAM, ctx: FunctionContext) -> str:
    return f"; LOAD_PARAM {instr.idx}\n" \
           f"push qword [rbp+{(instr.idx + 2) * Word.SIZE()}]"

def __emit_LOAD_GLOBAL(instr: LOAD_GLOBAL, ctx: FunctionContext) -> str:
    return f"; LOAD_GLOBAL {instr.name}\n" \
           f"push qword [rel {instr.name}]"

def __emit_LOAD_MEM(instr: LOAD_MEM, ctx: FunctionContext) -> str:
    sign = "-" if instr.offset < 0 else "+"
    
    return f"; LOAD_MEM {instr.offset}\n" \
            "pop rax\n" \
           f"push qword [rax{sign}{abs(instr.offset)}]"
    
def __emit_STORE_LOCAL(instr: STORE_LOCAL, ctx: FunctionContext) -> str:
    return f"; STORE_LOCAL {instr.idx}\n" \
           f"pop qword [rbp-{(instr.idx + 1) * Word.SIZE()}]"

def __emit_STORE_PARAM(instr: STORE_PARAM, ctx: FunctionContext) -> str:
    return f"; STORE_PARAM {instr.idx}\n" \
           f"pop qword [rbp+{(instr.idx + 2) * Word.SIZE()}]"

def __emit_STORE_GLOBAL(instr: STORE_GLOBAL, ctx: FunctionContext) -> str:
    return f"; STORE_GLOBAL {instr.name}\n" \
           f"pop qword [rel {instr.name}]"

def __emit_STORE_MEM(instr: STORE_MEM, ctx: FunctionContext) -> str:
    sign = "-" if instr.offset < 0 else "+"
    
    return f"; STORE_MEM {instr.offset}\n" \
            "pop rax\n" \
           f"pop qword [rax{sign}{abs(instr.offset)}]"

def __emit_POP(instr: POP, ctx: FunctionContext) -> str:
    return  "; POP\n" \
           f"add rsp, {Word.SIZE()}"

def __emit_ADD(instr: ADD, ctx: FunctionContext) -> str:
    dt = instr.data_type
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

def __emit_SUB(instr: SUB, ctx: FunctionContext) -> str:
    dt = instr.data_type
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

def __emit_MUL(instr: MUL, ctx: FunctionContext) -> str:
    dt = instr.data_type
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

def __emit_DIV(instr: DIV, ctx: FunctionContext) -> str:
    dt = instr.data_type
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

def __emit_MOD(instr: MOD, ctx: FunctionContext) -> str:
    dt = instr.data_type
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

def __emit_NATIVE_CALL(instr: NATIVE_CALL, ctx: FunctionContext) -> str:
    string = f"; NATIVE CALL\n" \
             f"call {instr.target}\n"

    if instr.num_params != 0:
        string += f"add rsp, {instr.num_params * Word.SIZE()} ; remove arguments from stack"
        
    if instr.returns_value:
        string += "push rax ; push return value"
    
    return string

def __emit_RET(instr: RET, ctx: FunctionContext) -> str:
    string = "; RET\n"

    if ctx.returns_value:
        string += "pop rax\n"
    
    string += "ret"
    return string

__INSTRUCTION_TRANSLATORS : Dict[OpCode, Callable[..., str]] = {
    OpCode.NOOP: __emit_NOOP,
    OpCode.LOAD_CONST: __emit_LOAD_CONST,
    OpCode.LOAD_LOCAL: __emit_LOAD_LOCAL,
    OpCode.LOAD_PARAM: __emit_LOAD_PARAM,
    OpCode.LOAD_GLOBAL: __emit_LOAD_GLOBAL,
    OpCode.LOAD_MEM: __emit_LOAD_MEM,
    OpCode.LOAD_FUNC_ADDR: __emit_LOAD_FUNC_ADDR,
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
}

def emit_Instruction(instr: Instruction, ctx: FunctionContext) -> str:
    if instr.opcode not in __INSTRUCTION_TRANSLATORS:
        raise NotImplementedError(instr.opcode)

    return __INSTRUCTION_TRANSLATORS[instr.opcode](instr, ctx)

def emit_Function(function: Function) -> str:
    ctx = FunctionContext(function.returns_value)
    string = f"{function.name}:"

    for label, bb in function.basic_blocks:
        string += f"\n  .{label}:"

        for instr in bb:
            nasm = emit_Instruction(instr, ctx).replace('\n', '\n    ')
            string += f"\n    {nasm}"

    return string

def emit_Program(program: Program, global_header: str = "", text_section_header: str = "") -> str:
    string = f"; SLASM_VERSION {VERSION()}\n" \
             f"; TARGET {program.target}\n\n"

    string += (global_header + "\n\n") if len(global_header) != 0 else ""
    string += f"    global _main\n\n    section .text\n_main:\n    call {program.entry}\n    ret ; note that rax alreeady contains the exit code from previous call instruction\n"
    string += text_section_header if len(text_section_header) != 0 else ""

    for function in program.functions:
        string += f"\n{emit_Function(function)}"

    return string
