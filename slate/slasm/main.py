from textwrap import dedent
from slate.slasm.function import BasicBlock, Function
from slate.slasm.program import Program
from slate.slasm.slasm import Word
from slate.slasm.emitters import llvm_emitter, nasm_emitter, xml_emitter
from slate.slasm import instruction

from llvmlite import ir # type: ignore

def main():
    program = Program(target="x86-64-linux-nasm")
    function = Function("SLASM_Main", 0, 0, True)

    basic_block = BasicBlock()
    # basic_block.append_instr(instruction.LoadConst(Word.FromUI64(123)))
    # basic_block.append_instr(instruction.LoadConst(Word.FromUI64(0x2000001)))
    # basic_block.append_instr(instruction.NativeCall("LINUX_x86_64_SYSCALL1", 2, False))
    basic_block.append_instr(instruction.LOAD_CONST(Word.FromUI64(64)))
    basic_block.append_instr(instruction.RET())

    function.add_basic_block("entry", basic_block)
    function.entry = "entry"

    program.add_function(function)
    program.entry = function.name

    with open('tests/test.slasm.xml', 'w') as file:
        file.write(xml_emitter.to_string(xml_emitter.emit_Program(program)))

    with open('tests/test.asm', 'w') as file:
        text_section_header = dedent(
            """
            LINUX_x86_64_SYSCALL1:
                mov rax, [rsp + 8]
                mov rdi, [rsp + 16]
                syscall
                ret
            """
        )

        file.write(nasm_emitter.emit_Program(program, "", text_section_header))

    with open('tests/test.ll', 'w') as file:
        def append_LINUX_x86_64_SYSCALL1(llvm_module: ir.Module) -> None:
            func = ir.Function(llvm_module, ir.FunctionType(ir.VoidType(), [ir.IntType(64), ir.IntType(64)]), "LINUX_x86_64_SYSCALL1")
            builder = ir.IRBuilder(func.append_basic_block(name=""))
            
            code, arg1 = func.args
            builder.asm(func.function_type, "movq $0, %rax\nmovq $1, %rdi\nsyscall", "r,r", [code, arg1], True)
            builder.ret_void()
        
        def append_main(llvm_module: ir.Module) -> None:
            func = ir.Function(llvm_module, ir.FunctionType(ir.IntType(32), []), "main")
            builder = ir.IRBuilder(func.append_basic_block(name=""))
            
            entry_return_value = builder.call(llvm_module.get_global(program.entry), [])
            exit_code = builder.trunc(entry_return_value, ir.IntType(32))
            builder.ret(exit_code)

        def setup(llvm_module: ir.Module) -> None:
            append_LINUX_x86_64_SYSCALL1(llvm_module)

        llvm_module = llvm_emitter.emit_Program(program, setup)
        append_main(llvm_module)

        file.write(str(llvm_module))

    import subprocess

    # process = subprocess.run("nasm -f macho64 tests/test.asm && gcc -arch x86_64 -o tests/test tests/test.o && rm tests/test.o && ./tests/test", shell=True)
    # print(f"{str(process.stdout)}\n{str(process.stderr)}\nExited with code {process.returncode}")

    process = subprocess.run(f"clang tests/test.ll -o tests/test-llvm && ./tests/test-llvm", shell=True)
    print(f"{str(process.stdout)}\n{str(process.stderr)}\nExited with code {process.returncode}")


    