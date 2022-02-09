from typing import Any, Callable, Dict, List, Optional
from slate.slasm.function import Function
from slate.slasm.instruction import LOAD_CONST, NATIVE_CALL, RET, Instruction, OpCode
from slate.slasm.program import Program
from slate.slasm.slasm import Word

from llvmlite import ir # type: ignore
import llvmlite.binding as llvm # type: ignore


LLVMTypeWord = ir.IntType(64)

class FunctionContext:
    def __init__(self, basic_blocks: Dict[str, ir.Block], returns_value: bool) -> None:
        self.__basic_blocks = basic_blocks
        self.__returns_value = returns_value
        self.__params : List[ir.Value] = []
        self.__locals : List[ir.Value] = []
        self.__stack : List[ir.Value] = []

    def push_value_onto_stack(self, value: ir.Value) -> None:
        self.__stack.append(value)
    
    def pop_value_from_stack(self) -> ir.Value:
        return self.__stack.pop()

    def get_basic_block(self, label: str) -> ir.Block:
        return self.__basic_blocks[label]

    def get_param(self, idx: int) -> ir.Value:
        return self.__params[idx]

    def get_local(self, idx: int) -> ir.Value:
        return self.__locals[idx]

    @property
    def returns_value(self) -> bool:
        return self.__returns_value

class GlobalContext:
    def __init__(self, llvm_module: ir.Module) -> None:
        self.__llvm_module = llvm_module

    def get_global(self, name: str) -> ir.Value:
        llvm_global = self.__llvm_module.get_global(name)
        assert isinstance(llvm_global, ir.GlobalVariable)

        return llvm_global 

    def get_function(self, name: str) -> ir.Function:
        llvm_global = self.__llvm_module.get_global(name)
        assert isinstance(llvm_global, ir.Function)

        return llvm_global 

def __emit_LOAD_CONST(instr: LOAD_CONST, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    func_ctx.push_value_onto_stack(ir.Constant(LLVMTypeWord, instr.value.as_ui64()))

def __emit_NATIVE_CALL(instr: NATIVE_CALL, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    call_value = llvm_builder.call(global_ctx.get_function(instr.target), [func_ctx.pop_value_from_stack() for _ in range(instr.num_params)])
    
    if instr.returns_value:
        func_ctx.push_value_onto_stack(call_value)

def __emit_RET(instr: RET, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    if func_ctx.returns_value:
        llvm_builder.ret(func_ctx.pop_value_from_stack())
    else:
        llvm_builder.ret_void()

__TRANSLATORS : Dict[Any, Callable[..., None]] = {
    OpCode.LOAD_CONST: __emit_LOAD_CONST,
    OpCode.NATIVE_CALL: __emit_NATIVE_CALL,
    OpCode.RET: __emit_RET,
}

def emit_Instruction(instr: Instruction, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    if instr.opcode not in __TRANSLATORS:
        raise NotImplementedError(instr.opcode)

    __TRANSLATORS[instr.opcode](instr, llvm_builder, func_ctx, global_ctx)

def emit_Function(function: Function, llvm_module: ir.Module, global_ctx: GlobalContext):
    llvm_func_type = ir.FunctionType(LLVMTypeWord if function.returns_value else ir.VoidType(), [LLVMTypeWord] * function.num_params)
    llvm_func = ir.Function(llvm_module, llvm_func_type, function.name)
    
    llvm_basic_blocks = {label:llvm_func.append_basic_block(label) for label, _ in function.basic_blocks}
    context = FunctionContext(llvm_basic_blocks, function.returns_value)

    for label, bb in function.basic_blocks:
        llvm_builder = ir.IRBuilder(context.get_basic_block(label))

        for instr in bb:
            emit_Instruction(instr, llvm_builder, context, global_ctx)

    return llvm_func

def emit_Program(program: Program, setup_callback: Callable[[ir.Module], None]) -> ir.Module:
    llvm_module = ir.Module(name="")
    setup_callback(llvm_module)

    global_ctx = GlobalContext(llvm_module)

    for function in program.functions:
        emit_Function(function, llvm_module, global_ctx)

    return llvm_module