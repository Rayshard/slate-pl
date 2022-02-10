from typing import Any, Callable, Dict, List, NamedTuple, Optional, cast
from slate.slasm.function import Function
from slate.slasm.instruction import *
from slate.slasm.program import Program
from slate.slasm.slasm import Word

from llvmlite import ir # type: ignore
import llvmlite.binding as llvm # type: ignore


LLVMTypeWord = ir.IntType(64)

class GlobalContext:
    FuncDef = NamedTuple('FuncDef', [('llvm_func', ir.Function), ('num_params', int), ('returns_value', bool)])
    
    def __init__(self, llvm_module: ir.Module) -> None:
        self.__llvm_module = llvm_module

    def get_global(self, name: str) -> ir.Value:
        llvm_global = self.__llvm_module.get_global(name)
        assert isinstance(llvm_global, ir.GlobalVariable)

        return llvm_global 

    def get_function(self, name: str) -> FuncDef:
        llvm_func = self.__llvm_module.get_global(name)
        assert isinstance(llvm_func, ir.Function)

        return GlobalContext.FuncDef(llvm_func, len(llvm_func.args), llvm_func.return_value.type == ir.VoidType())

class FunctionContext:
    def __init__(self, func_name: str, global_ctx: GlobalContext) -> None:
        self.__func_name = func_name
        self.__global_ctx = global_ctx
        self.__params : List[ir.Value] = []
        self.__locals : List[ir.Value] = []
        self.__stack : List[ir.Value] = []

    def push_value_onto_stack(self, value: ir.Value) -> None:
        self.__stack.append(value)
    
    def pop_value_from_stack(self) -> ir.Value:
        return self.__stack.pop()

    def get_basic_block(self, label: str) -> ir.Block:
        for block in cast(List[ir.Block], self.global_ctx.get_function(self.func_name).llvm_func.basic_blocks):
            if block.name == label:
                return block

        raise Exception(f"Functoin '{self.func_name}' does not contain a basic block labelled '{label}'")

    def get_param(self, idx: int) -> ir.Value:
        return self.__params[idx]

    def get_local(self, idx: int) -> ir.Value:
        return self.__locals[idx]

    @property
    def func_name(self) -> str:
        return self.__func_name

    @property
    def global_ctx(self) -> GlobalContext:
        return self.__global_ctx

    @property
    def num_params(self) -> int:
        return self.global_ctx.get_function(self.func_name).num_params

    @property
    def returns_value(self) -> bool:
        return self.global_ctx.get_function(self.func_name).returns_value

def __emit_LOAD_CONST(instr: LOAD_CONST, llvm_builder: ir.IRBuilder, ctx: FunctionContext) -> None:
    ctx.push_value_onto_stack(ir.Constant(LLVMTypeWord, instr.value.as_ui64()))

def __emit_LOAD_FUNC_ADDR(instr: LOAD_FUNC_ADDR, llvm_builder: ir.IRBuilder, ctx: FunctionContext) -> None:
    ctx.push_value_onto_stack(ctx.global_ctx.get_function(instr.func_name))

def __emit_CALL(instr: CALL, llvm_builder: ir.IRBuilder, ctx: FunctionContext) -> None:
    target_func_def = ctx.global_ctx.get_function(instr.target)
    call_value = llvm_builder.call(target_func_def.llvm_func, [ctx.pop_value_from_stack() for _ in range(target_func_def.num_params)])
    
    if target_func_def.returns_value:
        ctx.push_value_onto_stack(call_value)

def __emit_RET(instr: RET, llvm_builder: ir.IRBuilder, ctx: FunctionContext) -> None:
    if ctx.returns_value:
        llvm_builder.ret(ctx.pop_value_from_stack())
    else:
        llvm_builder.ret_void()

__TRANSLATORS : Dict[Any, Callable[..., None]] = {
    OpCode.LOAD_CONST: __emit_LOAD_CONST,
    OpCode.LOAD_FUNC_ADDR: __emit_LOAD_FUNC_ADDR,
    OpCode.CALL: __emit_CALL,
    OpCode.RET: __emit_RET,
}

def emit_Instruction(instr: Instruction, llvm_builder: ir.IRBuilder, ctx: FunctionContext) -> None:
    if instr.opcode not in __TRANSLATORS:
        raise NotImplementedError(instr.opcode)

    __TRANSLATORS[instr.opcode](instr, llvm_builder, ctx)

def emit_Function(function: Function, ctx: GlobalContext) -> None:
    llvm_func = ctx.get_function(function.name).llvm_func

    # Forward declare basic blocks
    for label, _ in function.basic_blocks:
        llvm_func.append_basic_block(label)

    # Append instructions
    func_ctx = FunctionContext(function.name, ctx)

    for label, bb in function.basic_blocks:
        llvm_builder = ir.IRBuilder(func_ctx.get_basic_block(label))

        for instr in bb:
            emit_Instruction(instr, llvm_builder, func_ctx)

def emit_Program(program: Program, setup_callback: Callable[[ir.Module], None]) -> ir.Module:
    llvm_module = ir.Module(name="")
    setup_callback(llvm_module)

    global_ctx = GlobalContext(llvm_module)

    # Forward declare functions
    for function in program.functions:
        llvm_func_type = ir.FunctionType(LLVMTypeWord if function.returns_value else ir.VoidType(), [LLVMTypeWord] * function.num_params)
        ir.Function(llvm_module, llvm_func_type, function.name)

    # Populate functions
    for function in program.functions:
        emit_Function(function, global_ctx)

    return llvm_module
