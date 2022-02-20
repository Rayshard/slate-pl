from enum import Enum, auto
import subprocess
from tempfile import TemporaryDirectory, TemporaryFile
from typing import Tuple
import unittest
from slate.slasm.program import Program
from slate.slasm.function import Function, BasicBlock
from slate.slasm import instruction
from slate.slasm.slasm import Word
from slate.slasm.visitors import nasm_visitor
from pathlib import Path

class OSTarget(Enum):
    WINDOWS = auto()
    LINUX = auto()
    MACOS = auto()


class TestSlasm(unittest.TestCase):

    def _create_LOAD_CONST(self) -> Tuple[Program, str]:
        program = Program(target="x86-64-linux-nasm", globals={})
        function = Function("SLASM_Main", {}, {}, True)

        basic_block = BasicBlock()
        basic_block.append_instr(instruction.LOAD_CONST(Word.FromI64(123)))
        basic_block.append_instr(instruction.CALL("DEBUG_PRINT_I64"))
        basic_block.append_instr(instruction.LOAD_CONST(Word.FromI64(0)))
        basic_block.append_instr(instruction.RET())

        function.add_basic_block("entry", basic_block)
        function.entry = "entry"

        program.add_function(function)
        program.entry = function.name

        return program, "123"

    def _run_nasm_program(self, program: Program, target_os: OSTarget) -> str:
        with open('tests/slasm/nasm_template.asm', 'r') as template_file:
            template = template_file.read()

            native_funcs = {
                "LINUX_x86_64_SYSCALL1_WITH_RET": nasm_visitor.GlobalContext.FuncDef(["arg0", "arg1"], [], True),
                "LINUX_x86_64_SYSCALL1_NO_RET": nasm_visitor.GlobalContext.FuncDef(["arg0", "arg1"], [], False),
                "C_CALL_3_WITH_RET": nasm_visitor.GlobalContext.FuncDef(["arg0", "arg1", "arg2", "arg3"], [], True),
                "C_CALL_3_NO_RET": nasm_visitor.GlobalContext.FuncDef(["arg0", "arg1", "arg2", "arg3"], [], False),
                "DEBUG_PRINT_I64": nasm_visitor.GlobalContext.FuncDef(["arg0"], [], False),
            }

            asm_file_path = Path("tests/slasm/file.asm")
            object_file_path = asm_file_path.with_suffix(".o")
            executable_file_path = asm_file_path.with_suffix("")

            with asm_file_path.open("w") as file:
                file.write(nasm_visitor.emit_Program(program, template, native_funcs))

                process = subprocess.run(f"nasm -felf64 {asm_file_path} && g++ -no-pie -o {executable_file_path} {object_file_path} && rm {object_file_path} && .{executable_file_path}", shell=True)

                return process.stdout

            # with TemporaryDirectory() as temp_dir:
            #     asm_file_path = Path(temp_dir + "/file.asm")

            #     with asm_file_path.open("w") as file:
            #         file.write(nasm_visitor.emit_Program(program, template, native_funcs))

            #         object_file_path = asm_file_path.with_suffix(".o")

            #         if target_os == OSTarget.MACOS:
            #             executable_file_path = asm_file_path.with_suffix("")
            #             process = subprocess.run(f"nasm -fmacho64 {asm_file_path} && gcc -arch x86_64 -o {executable_file_path} {object_file_path} && rm {object_file_path} && .{executable_file_path}", shell=True)
            #         elif target_os == OSTarget.LINUX:
            #             executable_file_path = asm_file_path.with_suffix("")
            #             process = subprocess.run(f"nasm -felf64 {asm_file_path} && g++ -no-pie -o {executable_file_path} {object_file_path} && rm {object_file_path} && .{executable_file_path}", shell=True)
            #             process = subprocess.run(f"nasm -felf64 {asm_file_path} && g++ -no-pie -o {executable_file_path} {object_file_path} && rm {object_file_path} && .{executable_file_path}", shell=True)
            #         else:
            #             raise NotImplementedError(target_os)

            #         return process.stdout

    def test_nasm_LOAD_CONST(self) -> None:
        program, expected = self._create_LOAD_CONST()
        self.assertEqual(self._run_nasm_program(program, OSTarget.LINUX), expected)
        

if __name__ == '__main__':
    unittest.main()