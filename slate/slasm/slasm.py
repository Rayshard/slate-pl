from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Union, cast
import xml.etree.ElementTree as ET
import xml.dom.minidom

_VERSION = "1.0"

class OpCodes(Enum):
    NOOP = 0
    PUSH = auto()
    POP = auto()
    RET = auto()
    SYSCALL_LINUX = auto()

    def to_bytes(self) -> bytes:
        return bytes([cast(int, self.value)])

assert len(OpCodes) <= 256

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

Operand = Union[Word, str]

class Instruction(ABC):
    def __init__(self, opcode: OpCodes) -> None:
        self.__opcode = opcode

    def get_opcode(self) -> OpCodes:
        return self.__opcode

    def to_binary(self, ctx: BinaryContext) -> bytes:
        binary = bytearray(self.__opcode.to_bytes())

        for operand in self.get_operands(ctx):
            binary.extend(operand)

        return bytes(binary)

    @abstractmethod
    def to_xml(self) -> ET.Element:
        pass    

    @abstractmethod
    def to_nasm(self) -> str:
        pass        

    @abstractmethod
    def get_operands(self, ctx: BinaryContext) -> List[bytes]:
        pass

    def __str__(self) -> str:
        return xml.dom.minidom.parseString(ET.tostring(self.to_xml(), 'unicode')).toprettyxml(indent='    ')

    @staticmethod
    def GetSize(opcode: OpCodes) -> int:
        if opcode == OpCodes.PUSH:
            return 9
        elif opcode == OpCodes.SYSCALL_LINUX:
            return 10
        else:
            return 1

class Function:
    def __init__(self, name: str, num_params: int, num_locals: int) -> None:
        self.__name = name
        self.__num_params = num_params
        self.__num_locals = num_locals
        self.__size = 0
        self.__instructions : List[Instruction] = []

    def insert_instr(self, instr: Instruction) -> None:
        self.__instructions.append(instr)
        self.__size += Instruction.GetSize(instr.get_opcode())

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
