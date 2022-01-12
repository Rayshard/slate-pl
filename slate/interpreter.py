from typing import Optional
import llvmlite.binding as llvm # type: ignore
from llvmlite import ir as llvm_ir # type: ignore
from ctypes import CFUNCTYPE, c_int64

ExitCode = int

__LLVM_INITED : bool = False
__LLVM_TARGET_MACHINE : Optional[llvm.TargetMachine] = None

def run_llvm(module: llvm_ir.Module, entry_func_name: str) -> ExitCode:
    global __LLVM_INITED, __LLVM_TARGET_MACHINE

    if not __LLVM_INITED:
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        # Create a target machine representing the host
        target = llvm.Target.from_default_triple()
        __LLVM_TARGET_MACHINE = target.create_target_machine()

        __LLVM_INITED = True

    assert __LLVM_TARGET_MACHINE is not None # drops Optional from type

    # Create an execution engine
    engine = llvm.create_mcjit_compiler(llvm.parse_assembly(""), __LLVM_TARGET_MACHINE)
    engine.add_module(llvm.parse_assembly(str(module)))
    engine.finalize_object()
    engine.run_static_constructors()

    # Run the function via ctypes
    entry_func_ptr = engine.get_function_address(entry_func_name)
    entry_func = CFUNCTYPE(c_int64)(entry_func_ptr)

    exit_code = entry_func()
    assert isinstance(exit_code, ExitCode)

    return exit_code 
