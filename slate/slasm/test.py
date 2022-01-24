from slasm import Function, Instruction, Program, Word
import instructions as Instructions


program = Program()
function = Function("Main", 0, 0)
function.insert_instr(Instructions.Push(Word.FromUI64(123)))
function.insert_instr(Instructions.SyscallLinux(0x2000001, 1))
function.insert_instr(Instructions.Ret())

program.add_function(function, True)

# with open('tests/test.slasm', 'wb') as file:
#     file.write(program.get_bytes())

with open('tests/test.slasm.xml', 'w') as file:
    file.write(str(program))

with open('tests/test.asm', 'w') as file:
    file.write(program.to_nasm())

import subprocess

process = subprocess.run("nasm -f macho64 tests/test.asm && gcc -arch x86_64 -o tests/test tests/test.o && ./tests/test", shell=True)
print(f"{process.stdout}\n{process.stderr}\nExited with code {process.returncode}")