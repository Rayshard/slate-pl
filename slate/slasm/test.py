from slasm import Function, Instruction, Program, Word


program = Program()
function = Function("Main", 0, 0)
function.insert_instr(Instruction.Push(Word.FromUI64(123)))
function.insert_instr(Instruction.SyscallLinux(0x2000001, 1))
function.insert_instr(Instruction.Ret())

program.add_function(function, True)

# with open('tests/test.slasm', 'wb') as file:
#     file.write(program.get_bytes())

with open('tests/test.slasm.xml', 'w') as file:
    file.write(str(program))

with open('tests/test.asm', 'w') as file:
    file.write(program.to_nasm())

import subprocess

process = subprocess.run("nasm -f macho64 tests/test.asm && gcc -arch x86_64 -o tests/test tests/test.o && rm tests/test.o && ./tests/test", shell=True)
print(f"{str(process.stdout)}\n{str(process.stderr)}\nExited with code {process.returncode}")