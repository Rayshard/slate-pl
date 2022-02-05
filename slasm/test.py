from slasm.function import Function
from slasm.program import Program
from slasm.slasm import Word
from slasm.translators import nasm, xml_serializer
from slasm import instruction

# __PARAM_REGISTERS = ["RDI", "RSI", "RDX", "R10", "R8", "R9"]
# syscall_code, num_params = self.get_operand(0, Word), self.get_operand(1, int)
# string = f"; SYSCALL_LINUX {syscall_code.as_ui64()}, {num_params}\n" \
#             f"MOV RAX, {syscall_code.as_hex()}"

# for i in range(num_params):
#     string += f"\nPOP {__PARAM_REGISTERS[i]}"

# string += "\nSYSCALL"

def main():
    program = Program(target="x86-64-linux")
    function = Function("Main", 0, 0)
    function.insert_instr(instruction.LoadConst(Word.FromUI64(123)))
    function.insert_instr(instruction.InlineNativeAsm("LINUX_x86_64_SYSCALL1 0x2000001"))
    function.insert_instr(instruction.Ret())

    program.add_function(function)
    program.entry = function.name

    # with open('tests/test.slasm', 'wb') as file:
    #     file.write(program.get_bytes())

    with open('tests/test.slasm.xml', 'w') as file:
        file.write(xml_serializer.to_string(xml_serializer.translate_Program(program)))

    with open('tests/test.asm', 'w') as file:
        with open('slasm/nasm_header.asm') as header_file:
            header = header_file.read()

        file.write(nasm.translate_Program(program, header))

    import subprocess

    process = subprocess.run("nasm -f macho64 tests/test.asm && gcc -arch x86_64 -o tests/test tests/test.o && rm tests/test.o && ./tests/test", shell=True)
    print(f"{str(process.stdout)}\n{str(process.stderr)}\nExited with code {process.returncode}")