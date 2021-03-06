import subprocess
from textwrap import dedent
from slate.slasm.function import BasicBlock, Function
from slate.slasm.program import Program
from slate.slasm.slasm import Word
from slate.slasm.visitors import json_visitor, llvm_visitor, nasm_visitor, xml_visitor
from slate.slasm import instruction

from llvmlite import ir # type: ignore

def main():
    program = Program("x86-64-linux-nasm", {"GLOBAL_1", "GLOBAL_2", "GLOBAL_3"})
    program.add_data("DATA_my_string", b"Hello, World!\0")

    function = Function("FUNCTION_Main", {"p0", "p1", "p2"}, {"l1", "l2", "l3"}, True)

    basic_block = BasicBlock()
    # basic_block.append_instr(instruction.LoadConst(Word.FromUI64(123)))
    # basic_block.append_instr(instruction.LoadConst(Word.FromUI64(0x2000001)))
    # basic_block.append_instr(instruction.NativeCall("LINUX_x86_64_SYSCALL1", 2, False))
    basic_block.append_instr(instruction.LOAD_CONST(Word.FromI64(123)))
    basic_block.append_instr(instruction.CALL("DEBUG_PRINT_I64"))
    basic_block.append_instr(instruction.LOAD_CONST(Word.FromI64(64)))
    basic_block.append_instr(instruction.RET())

    function.add_basic_block("entry", basic_block)
    function.entry = "entry"

    program.add_function(function)
    program.entry = function.name

    with open('tests/test.slasm.xml', 'w') as file:
        file.write(xml_visitor.to_string(xml_visitor.emit_Program(program)))

    with open('tests/test.slasm.json', 'w') as file:
        file.write(json_visitor.to_string(json_visitor.emit_Program(program)))

    with open('slate/slasm/nasm_template.asm', 'r') as template_file:
        template = template_file.read()

        native_funcs = {
            "LINUX_x86_64_SYSCALL1_WITH_RET": nasm_visitor.GlobalContext.FuncDef(["p0", "p1"], [], True),
            "LINUX_x86_64_SYSCALL1_NO_RET": nasm_visitor.GlobalContext.FuncDef(["p0", "p1"], [], False),
            "C_CALL_3_WITH_RET": nasm_visitor.GlobalContext.FuncDef(["p0", "p1", "p2", "p3"], [], True),
            "C_CALL_3_NO_RET": nasm_visitor.GlobalContext.FuncDef(["p0", "p1", "p2", "p3"], [], False),
            "DEBUG_PRINT_I64": nasm_visitor.GlobalContext.FuncDef(["p0"], [], False),
        }

        with open('tests/test.asm', 'w') as file:
            file.write(nasm_visitor.emit_Program(program, template, native_funcs))

    # with open('tests/test.ll', 'w') as file:
    #     def append_LINUX_x86_64_SYSCALL1(llvm_module: ir.Module) -> None:
    #         func = ir.Function(llvm_module, ir.FunctionType(ir.VoidType(), [ir.IntType(64), ir.IntType(64)]), "LINUX_x86_64_SYSCALL1")
    #         builder = ir.IRBuilder(func.append_basic_block(name=""))
            
    #         code, arg1 = func.args
    #         builder.asm(func.function_type, "movq $0, %rax\nmovq $1, %rdi\nsyscall", "r,r", [code, arg1], True)
    #         builder.ret_void()
        
    #     def append_main(llvm_module: ir.Module) -> None:
    #         func = ir.Function(llvm_module, ir.FunctionType(ir.IntType(32), []), "main")
    #         builder = ir.IRBuilder(func.append_basic_block(name=""))
            
    #         entry_return_value = builder.call(llvm_module.get_global(program.entry), [])
    #         exit_code = builder.trunc(entry_return_value, ir.IntType(32))
    #         builder.ret(exit_code)

    #     def setup(llvm_module: ir.Module) -> None:
    #         append_LINUX_x86_64_SYSCALL1(llvm_module)

    #     llvm_module = llvm_visitor.emit_Program(program, setup)
    #     append_main(llvm_module)

    #     file.write(str(llvm_module))

    process = subprocess.run("nasm -f macho64 tests/test.asm && gcc -arch x86_64 -o tests/test tests/test.o && rm tests/test.o && ./tests/test", shell=True)
    print(f"{str(process.stdout)}\n{str(process.stderr)}\nExited with code {process.returncode}")

    # process = subprocess.run(f"clang tests/test.ll -o tests/test-llvm && ./tests/test-llvm", shell=True)
    # print(f"{str(process.stdout)}\n{str(process.stderr)}\nExited with code {process.returncode}")


    