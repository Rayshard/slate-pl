from typing import Any, Callable, Dict, List, Optional
from slasm.function import Function
from slasm.instruction import Instruction, OpCode
from slasm.program import Program
from slasm.slasm import Word

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

def __translate_InstrNoop(instr: Instruction, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    assert False, "Not implemented"

def __translate_InstrLoadConst(instr: Instruction, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    func_ctx.push_value_onto_stack(ir.Constant(LLVMTypeWord, instr.get_operand(0, Word).as_ui64()))

def __translate_InstrLoadLabel(instr: Instruction, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    assert False, "Not implemented"

def __translate_InstrLoadLocal(instr: Instruction, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    assert False, "Not implemented"

def __translate_InstrLoadParam(instr: Instruction, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    assert False, "Not implemented"

def __translate_InstrLoadGlobal(instr: Instruction, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    assert False, "Not implemented"

def __translate_InstrLoadMem(instr: Instruction, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    assert False, "Not implemented"
    
def __translate_InstrStoreLocal(instr: Instruction, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    assert False, "Not implemented"

def __translate_InstrStoreParam(instr: Instruction, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    assert False, "Not implemented"

def __translate_InstrStoreGlobal(instr: Instruction, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    assert False, "Not implemented"

def __translate_InstrStoreMem(instr: Instruction, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    assert False, "Not implemented"

def __translate_InstrPop(instr: Instruction, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    assert False, "Not implemented"

def __translate_InstrAdd(instr: Instruction, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    assert False, "Not implemented"

def __translate_InstrSub(instr: Instruction, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    assert False, "Not implemented"

def __translate_InstrMul(instr: Instruction, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    assert False, "Not implemented"

def __translate_InstrDiv(instr: Instruction, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    assert False, "Not implemented"

def __translate_InstrMod(instr: Instruction, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    assert False, "Not implemented"

def __translate_InstrNativeCall(instr: Instruction, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    target, num_params, returns_value = instr.get_operand(0, str), instr.get_operand(1, int), instr.get_operand(2, bool)
    call_value = llvm_builder.call(global_ctx.get_function(target), [func_ctx.pop_value_from_stack() for _ in range(num_params)])
    
    if returns_value:
        func_ctx.push_value_onto_stack(call_value)

def __translate_InstrRet(instr: Instruction, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    if func_ctx.returns_value:
        llvm_builder.ret(func_ctx.pop_value_from_stack())
    else:
        llvm_builder.ret_void()

__TRANSLATORS : Dict[Any, Callable[[Instruction, ir.IRBuilder, FunctionContext, GlobalContext], None]] = {
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

def translate_Instruction(instr: Instruction, llvm_builder: ir.IRBuilder, func_ctx: FunctionContext, global_ctx: GlobalContext) -> None:
    if instr.opcode not in __TRANSLATORS:
        raise NotImplementedError(instr.opcode)

    __TRANSLATORS[instr.opcode](instr, llvm_builder, func_ctx, global_ctx)

def translate_Function(function: Function, llvm_module: ir.Module, global_ctx: GlobalContext):
    llvm_func_type = ir.FunctionType(LLVMTypeWord if function.returns_value else ir.VoidType(), [LLVMTypeWord] * function.num_params)
    llvm_func = ir.Function(llvm_module, llvm_func_type, function.name)
    
    llvm_basic_blocks = {label:llvm_func.append_basic_block(label) for label, _ in function.basic_blocks}
    context = FunctionContext(llvm_basic_blocks, function.returns_value)

    for label, bb in function.basic_blocks:
        llvm_builder = ir.IRBuilder(context.get_basic_block(label))

        for instr in bb:
            translate_Instruction(instr, llvm_builder, context, global_ctx)

    return llvm_func

def translate_Program(program: Program, setup_callback: Callable[[ir.Module], None]) -> ir.Module:
    llvm_module = ir.Module(name="")
    setup_callback(llvm_module)

    global_ctx = GlobalContext(llvm_module)

    for function in program.functions:
        translate_Function(function, llvm_module, global_ctx)

    return llvm_module
