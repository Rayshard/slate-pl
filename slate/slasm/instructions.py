import opcode
from typing import Callable, Dict, List
from slasm import Instruction
from slate.slasm.slasm import BinaryContext, OpCodes, Word
import xml.etree.ElementTree as ET

class Noop(Instruction):
    def __init__(self) -> None:
        super().__init__(OpCodes.NOOP)

    def get_operands(self, ctx: BinaryContext) -> List[bytes]:
        return []

    def to_xml(self) -> ET.Element:
        return ET.Element("NOOP")

    def to_nasm(self) -> str:
        return "; NOOP\nXCHG RAX, RAX"  

class Pop(Instruction):
    def __init__(self) -> None:
        super().__init__(OpCodes.POP)

    def get_operands(self, ctx: BinaryContext) -> List[bytes]:
        return []

    def to_xml(self) -> ET.Element:
        return ET.Element("POP")

    def to_nasm(self) -> str:
        return "; POP\nPOP RAX"

class Ret(Instruction):
    def __init__(self) -> None:
        super().__init__(OpCodes.POP)

    def get_operands(self, ctx: BinaryContext) -> List[bytes]:
        return []

    def to_xml(self) -> ET.Element:
        return ET.Element("RET")

    def to_nasm(self) -> str:
        return "; RET\nRET"

class Push(Instruction):
    def __init__(self, value: Word) -> None:
        super().__init__(OpCodes.PUSH)
        self.__value = value

    def get_value(self) -> Word:
        return self.__value

    def get_operands(self, ctx: BinaryContext) -> List[bytes]:
        return [self.__value.bytes]

    def to_xml(self) -> ET.Element:
        return ET.Element("PUSH", {"value": self.__value.as_hex()})

    def to_nasm(self) -> str:
        return f"; PUSH {self.__value.as_hex()}\nMOV RAX, {self.__value.as_hex()}\nPUSH RAX"

class SyscallLinux(Instruction):
    _PARAM_REGISTERS = ["RDI", "RSI", "RDX", "R10", "R8", "R9"]

    def __init__(self, code: int, num_params: int) -> None:
        super().__init__(OpCodes.SYSCALL_LINUX)
        assert code >= 0 and 0 <= num_params <= 6

        self.__code = code
        self.__num_params = num_params

    def get_code(self) -> int:
        return self.__code

    def get_num_params(self) -> int:
        return self.__num_params

    def get_operands(self, ctx: BinaryContext) -> List[bytes]:
        return [Word.FromUI64(self.__code).bytes, Word.FromUI64(self.__num_params).bytes[:1]]

    def to_xml(self) -> ET.Element:
        return ET.Element("SYSCALL_LINUX", {"code": str(self.__code), "num_params": str(self.__num_params)})

    def to_nasm(self) -> str:
        string = f"; SYSCALL_LINUX {self.__code}, {self.__num_params}\nMOV RAX, {self.__code}"

        for i in range(self.__num_params):
            string += f"\nPOP {SyscallLinux._PARAM_REGISTERS[i]}"

        string += "\nSYSCALL"
        return string

__CONVERTERS : Dict[OpCodes, Callable[[bytes], Instruction]] = {
    OpCodes.NOOP: lambda bs: Noop(),
    OpCodes.PUSH: lambda bs: Push(Word(bs[1:Word.SIZE() + 1])),
    OpCodes.POP: lambda bs: Pop(),
    OpCodes.SYSCALL_LINUX: lambda bs: SyscallLinux(int.from_bytes(bs[1:Word.SIZE()], 'big', signed=False), int.from_bytes(bs[1 + Word.SIZE():2 + Word.SIZE()], 'big', signed=False)),
    OpCodes.RET: lambda bs: Ret(),
}

assert all([opcode in __CONVERTERS for opcode in OpCodes])

def FromBytes(bs: bytes) -> Instruction:
    assert len(bs) > 0 and bs[0] < len(OpCodes)
    opcode = OpCodes(bs[0])

    assert len(bs) >= Instruction.GetSize(opcode)
    return __CONVERTERS[opcode]