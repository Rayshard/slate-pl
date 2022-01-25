from enum import Enum, auto
from typing import Any, Dict, List, Optional, Type, TypeVar, cast
import xml.etree.ElementTree as ET
import xml.dom.minidom

_VERSION = "1.0"

class OpCode(Enum):
    NOOP = 0

    PUSH_CONSTANT = auto()
    PUSH_LABEL = auto()
    POP = auto()

    SLOAD = auto()
    SSTORE = auto()
    LLOAD = auto()
    LSTORE = auto()
    PLOAD = auto()
    PSTORE = auto()
    GLOAD = auto()
    GSTORE = auto()
    MLOAD = auto()
    MSTORE = auto()

    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    EQ = auto()
    NEQ = auto()

    JUMP = auto()
    JUMPZ = auto()
    JUMPNZ = auto()
    CALL = auto()
    RET = auto()

    SYSCALL_LINUX = auto()
    SYSCALL_WINDOWS = auto()

    def to_bytes(self) -> bytes:
        return bytes([cast(int, self.value)])

assert len(OpCode) <= 256

class Word:
    def __init__(self, bs: bytes) -> None:
        assert len(bs) == Word.SIZE()
        self.bytes = bs

    def as_hex(self) -> str:
        return "0x" + self.bytes.hex()

    def as_i64(self) -> int:
        return int.from_bytes(self.bytes, 'big', signed=True)

    def as_ui64(self) -> int:
        return int.from_bytes(self.bytes, 'big', signed=False)

    @staticmethod
    def FromI64(value: int) -> 'Word':
        return Word(value.to_bytes(Word.SIZE(), 'big', signed=True))

    @staticmethod
    def FromUI64(value: int) -> 'Word':
        return Word(value.to_bytes(Word.SIZE(), 'big', signed=False))

    @staticmethod
    def SIZE() -> int:
        return 8

class BinaryContext:
    def __init__(self) -> None:
        self.__functions : Dict[str, int] = {}
        self.__ip = 0
        self.__entry : Optional[str] = None

    def add_function(self, name: str, size: int, is_entry: bool = False) -> None:
        assert name not in self.__functions
        self.__functions[name] = self.__ip
        self.__ip += size

        if is_entry:
            self.__entry = name

    def get_func_addr(self, name: str) -> Word:
        assert name in self.__functions
        return Word.FromUI64(self.__functions[name])

    def get_entry(self) -> str:
        assert self.__entry is not None
        return self.__entry

    def has_entry(self) -> bool:
        return self.__entry is not None

_TOperand = TypeVar("_TOperand")
Operand = Any

class Instruction:
    def __init__(self, opcode: OpCode, operands: List[Operand], size: int) -> None:
        self.__opcode = opcode
        self.__operands = operands
        self.__size = size

    def get_opcode(self) -> OpCode:
        return self.__opcode

    def get_size(self) -> int:
        return self.__size

    def get_operands(self) -> List[Operand]:
        return self.__operands

    def get_operand(self, idx: int, op_type: Type[_TOperand]) -> _TOperand:
        assert idx < len(self.__operands)
        assert type(self.__operands[idx]) == op_type
        return cast(op_type, self.__operands[idx]) # type: ignore

    def to_binary(self, ctx: BinaryContext) -> bytes:
        binary = bytearray(self.__opcode.to_bytes())

        if self.__opcode == OpCode.NOOP:
            pass
        elif self.__opcode == OpCode.PUSH:
            binary.extend(self.get_operand(0, Word).bytes)
        elif self.__opcode == OpCode.POP:
            pass
        elif self.__opcode == OpCode.RET:
            pass
        elif self.__opcode == OpCode.SYSCALL_LINUX:
            binary.extend(Word.FromUI64(self.get_operand(0, int)).bytes)
            binary.extend(Word.FromUI64(self.get_operand(1, int)).bytes[:1])
        else:
            assert False, "Not implemented"

        return bytes(binary)

    def to_xml(self) -> ET.Element:
        if self.__opcode == OpCode.NOOP:
            return ET.Element("NOOP")
        elif self.__opcode == OpCode.PUSH:
            return ET.Element("PUSH", {"value": self.get_operand(0, Word).as_hex()})
        elif self.__opcode == OpCode.POP:
            return ET.Element("POP")
        elif self.__opcode == OpCode.RET:
            return ET.Element("RET")
        elif self.__opcode == OpCode.SYSCALL_LINUX:
            return ET.Element("SYSCALL_LINUX", {"code": str(self.get_operand(0, int)), "num_params": str(self.get_operand(1, int))})
        
        assert False, "Not implemented"    

    def to_nasm(self) -> str:
        string : str = ""

        if self.__opcode == OpCode.NOOP:
            string = "; NOOP\nXCHG RAX, RAX"
        elif self.__opcode == OpCode.PUSH:
            value_hex = self.get_operand(0, Word).as_hex()
            string = f"; PUSH {value_hex}\nMOV RAX, {value_hex}\nPUSH RAX"
        elif self.__opcode == OpCode.POP:
            string = "; POP\nPOP RAX"
        elif self.__opcode == OpCode.RET:
            string = "; RET\nRET"
        elif self.__opcode == OpCode.SYSCALL_LINUX:
            __PARAM_REGISTERS = ["RDI", "RSI", "RDX", "R10", "R8", "R9"]
            syscall_code, num_params = self.get_operand(0, int), self.get_operand(1, int)
            string = f"; SYSCALL_LINUX {syscall_code}, {num_params}\nMOV RAX, {syscall_code}"

            for i in range(num_params):
                string += f"\nPOP {__PARAM_REGISTERS[i]}"

            string += "\nSYSCALL"
        else:
            assert False, "Not implemented"       
        
        return string 

    def __str__(self) -> str:
        return xml.dom.minidom.parseString(ET.tostring(self.to_xml(), 'unicode')).toprettyxml(indent='    ')

    @staticmethod
    def FromBytes(bs: bytes) -> 'Instruction':
        assert len(bs) > 0 and bs[0] < len(OpCode)
        opcode = OpCode(bs[0])

        if opcode == OpCode.NOOP:
            return Instruction.Noop()
        elif opcode == OpCode.PUSH:
            value = Word(bs[1:Word.SIZE() + 1])
            return Instruction.Push(value)
        elif opcode == OpCode.POP:
            return Instruction.Pop()
        elif opcode == OpCode.RET:
            return Instruction.Ret()
        elif opcode == OpCode.SYSCALL_LINUX:
            syscall_code = int.from_bytes(bs[1:Word.SIZE()], 'big', signed=False)
            num_params = int.from_bytes(bs[1 + Word.SIZE():2 + Word.SIZE()], 'big', signed=False)
            return Instruction.SyscallLinux(syscall_code, num_params)
        
        assert False, "Not implemented"

    @staticmethod
    def Noop() -> 'Instruction':
        return Instruction(OpCode.NOOP, [], 1)

    @staticmethod
    def Push(value: Word) -> 'Instruction':
        return Instruction(OpCode.PUSH, [value], 9)

    @staticmethod
    def Pop() -> 'Instruction':
        return Instruction(OpCode.POP, [], 1)

    @staticmethod
    def Ret() -> 'Instruction':
        return Instruction(OpCode.RET, [], 1)

    @staticmethod
    def SyscallLinux(code: int, num_params: int) -> 'Instruction':
        assert num_params <= 6
        return Instruction(OpCode.SYSCALL_LINUX, [code, num_params], 10)

class Function:
    def __init__(self, name: str, num_params: int, num_locals: int) -> None:
        self.__name = name
        self.__num_params = num_params
        self.__num_locals = num_locals
        self.__size = 0
        self.__instructions : List[Instruction] = []

    def insert_instr(self, instr: Instruction) -> None:
        self.__instructions.append(instr)
        self.__size += instr.get_size()

    def get_name(self) -> str:
        return self.__name

    def get_size(self) -> int:
        return self.__size

    def get_num_params(self) -> int:
        return self.__num_params

    def get_num_locals(self) -> int:
        return self.__num_locals

    def to_xml(self) -> ET.Element:
        element = ET.Element("function", {"name": self.__name, "params": str(self.__num_params), "locals": str(self.__num_locals)})

        for instr in self.__instructions:
            element.append(instr.to_xml())

        return element
    
    def to_binary(self, ctx: BinaryContext) -> bytes:
        binary = bytearray()

        for instr in self.__instructions:
            binary.extend(instr.to_binary(ctx))

        return bytes(binary)

    def to_nasm(self) -> str:
        string = f"FUNC_{self.__name}:"

        for instr in self.__instructions:
            nasm = instr.to_nasm().replace('\n', '\n    ')
            string += f"\n    {nasm}"

        return string

    def __str__(self) -> str:
        return xml.dom.minidom.parseString(ET.tostring(self.to_xml(), 'unicode')).toprettyxml(indent='    ')

class Program:
    def __init__(self) -> None:
        self.__functions : List[Function] = []
        self.__binary_ctx = BinaryContext()

    def add_function(self, function: Function, is_entry: bool = False) -> None:
        self.__binary_ctx.add_function(function.get_name(), function.get_size(), is_entry)
        self.__functions.append(function)

    def to_binary(self) -> bytes:
        binary = bytearray()
        
        for function in self.__functions:
            binary.extend(function.to_binary(self.__binary_ctx))

        return bytes(binary)

    def to_xml(self) -> ET.Element:
        document = ET.Element("program", {"slasm_version": _VERSION})
        code = ET.SubElement(document, "code", {"entry":self.__binary_ctx.get_entry()})

        for function in self.__functions:
            code.append(function.to_xml())

        return document

    def to_nasm(self) -> str:
        string = "    global _main\n\n    section .text"

        for function in self.__functions:
            if function.get_name() == self.__binary_ctx.get_entry():
                string += f"\n_main:"

            string += f"\n{function.to_nasm()}"

        return string

    def __str__(self) -> str:
        return xml.dom.minidom.parseString(ET.tostring(self.to_xml(), 'unicode')).toprettyxml(indent='    ')
