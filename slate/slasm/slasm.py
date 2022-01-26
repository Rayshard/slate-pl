from enum import Enum, auto
from typing import Any, Dict, List, Optional, Type, TypeVar, cast, Literal, Union
import xml.etree.ElementTree as ET
import xml.dom.minidom

_VERSION = "1.0"

class OpCode(Enum):
    NOOP = 0

    LOAD_CONST = auto()
    LOAD_LABEL = auto()
    LOAD_LOCAL = auto()
    LOAD_PARAM = auto()
    LOAD_GLOBAL = auto()
    LOAD_MEM = auto()

    POP = auto()
    STORE_LOCAL = auto()
    STORE_PARAM = auto()
    STORE_GLOBAL = auto()
    STORE_MEM = auto()

    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    EQ = auto()
    NEQ = auto()
    GT = auto()
    LT = auto()
    GTEQ = auto()
    LTEQ = auto()
    NEG = auto()

    OR = auto()
    AND = auto()
    XOR = auto()
    NOT = auto()
    LSHIFT = auto()
    RSHIFT = auto()

    JUMP = auto()
    JUMP_ADDR = auto()
    JUMPZ = auto()
    JUMPZ_ADDR = auto()
    JUMPNZ = auto()
    JUMPNZ_ADDR = auto()
    CALL = auto()
    CALL_ADDR = auto()
    RET = auto()

    SYSCALL_LINUX = auto()
    SYSCALL_WINDOWS = auto()

class DataType(Enum):
    I8 = 0
    UI8 = auto()
    I16 = auto()
    UI16 = auto()
    I32 = auto()
    UI32 = auto()
    I64 = auto()
    UI64 = auto()
    F32 = auto()
    F64 = auto()

class Word:
    def __init__(self, bs: bytes) -> None:
        assert len(bs) == Word.SIZE()
        self.bytes = bs

    def as_hex(self, endianness: Literal['little', 'big'] = 'little') -> str:
        return "0x" + (self.bytes.hex() if endianness == 'little' else self.bytes[::-1].hex())

    def as_i64(self) -> int:
        return int.from_bytes(self.bytes, 'little', signed=True)

    def as_ui64(self) -> int:
        return int.from_bytes(self.bytes, 'little', signed=False)

    @staticmethod
    def FromI64(value: int) -> 'Word':
        return Word(value.to_bytes(8, 'little', signed=True))

    @staticmethod
    def FromUI64(value: int) -> 'Word':
        return Word(value.to_bytes(8, 'little', signed=False))

    @staticmethod
    def SIZE() -> int:
        return 8

_TOperand = TypeVar("_TOperand")
Operand = Any
Label = str

class Instruction:
    def __init__(self, opcode: OpCode, operands: List[Operand]) -> None:
        self.__opcode = opcode
        self.__operands = operands

    def get_opcode(self) -> OpCode:
        return self.__opcode

    def get_operands(self) -> List[Operand]:
        return self.__operands

    def get_operand(self, idx: int, op_type: Type[_TOperand]) -> _TOperand:
        assert idx < len(self.__operands)
        assert type(self.__operands[idx]) == op_type
        return cast(op_type, self.__operands[idx]) # type: ignore

    def to_xml(self) -> ET.Element:
        if self.__opcode == OpCode.NOOP:
            return ET.Element("NOOP")
        elif self.__opcode == OpCode.LOAD_CONST:
            return ET.Element("LOAD_CONST", {"value": self.get_operand(0, Word).as_hex('big')})
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
        elif self.__opcode == OpCode.LOAD_CONST:
            value_hex = self.get_operand(0, Word).as_hex('big')
            string = f"; LOAD_CONST {value_hex}\nMOV RAX, {value_hex}\nPUSH RAX"
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
    def Noop() -> 'Instruction':
        return Instruction(OpCode.NOOP, [])

    @staticmethod
    def LoadConst(value: Word) -> 'Instruction':
        return Instruction(OpCode.LOAD_CONST, [value])

    @staticmethod
    def LoadLabel(label: Label) -> 'Instruction':
        return Instruction(OpCode.LOAD_LABEL, [label])

    @staticmethod
    def LoadLocal(idx: int) -> 'Instruction':
        return Instruction(OpCode.LOAD_LOCAL, [Word.FromUI64(idx)])

    @staticmethod
    def LoadParam(idx: int) -> 'Instruction':
        return Instruction(OpCode.LOAD_PARAM, [Word.FromUI64(idx)])

    @staticmethod
    def LoadGlobal(name: str) -> 'Instruction':
        return Instruction(OpCode.LOAD_GLOBAL, [name])

    @staticmethod
    def LoadMem(offset: int) -> 'Instruction':
        return Instruction(OpCode.LOAD_MEM, [Word.FromI64(offset)])

    @staticmethod
    def StoreLocal(idx: int) -> 'Instruction':
        return Instruction(OpCode.STORE_LOCAL, [Word.FromUI64(idx)])

    @staticmethod
    def StoreParam(idx: int) -> 'Instruction':
        return Instruction(OpCode.STORE_PARAM, [Word.FromUI64(idx)])

    @staticmethod
    def StoreGlobal(name: str) -> 'Instruction':
        return Instruction(OpCode.STORE_GLOBAL, [name])

    @staticmethod
    def StoreMem(offset: int) -> 'Instruction':
        return Instruction(OpCode.STORE_MEM, [Word.FromI64(offset)])

    @staticmethod
    def Jump(label: Label) -> 'Instruction':
        return Instruction(OpCode.JUMP, [label])

    @staticmethod
    def JumpZ(label: Label) -> 'Instruction':
        return Instruction(OpCode.JUMPZ, [label])

    @staticmethod
    def JumpNZ(label: Label) -> 'Instruction':
        return Instruction(OpCode.JUMPNZ, [label])

    @staticmethod
    def JumpAddr() -> 'Instruction':
        return Instruction(OpCode.JUMP_ADDR, [])

    @staticmethod
    def JumpZAddr() -> 'Instruction':
        return Instruction(OpCode.JUMPZ_ADDR, [])

    @staticmethod
    def JumpNZAddr() -> 'Instruction':
        return Instruction(OpCode.JUMPNZ_ADDR, [])

    @staticmethod
    def Call(label: Label) -> 'Instruction':
        return Instruction(OpCode.CALL, [label])

    @staticmethod
    def CallAddr() -> 'Instruction':
        return Instruction(OpCode.CALL_ADDR, [])

    @staticmethod
    def Pop() -> 'Instruction':
        return Instruction(OpCode.POP, [])

    @staticmethod
    def Ret() -> 'Instruction':
        return Instruction(OpCode.RET, [])

    @staticmethod
    def SyscallLinux(code: int, num_params: int) -> 'Instruction':
        assert num_params <= 6
        return Instruction(OpCode.SYSCALL_LINUX, [code, num_params])

class Function:
    def __init__(self, name: str, num_params: int, num_locals: int) -> None:
        self.__name = name
        self.__num_params = num_params
        self.__num_locals = num_locals
        self.__instructions : List[Instruction] = []
        self.__labels : Dict[Label, int] = {}

    def insert_instr(self, instr: Instruction) -> None:
        self.__instructions.append(instr)

    def insert_label(self, label: Label) -> None:
        assert label not in self.__labels
        self.__labels[label] = len(self.__instructions)

    def get_name(self) -> str:
        return self.__name

    def get_num_params(self) -> int:
        return self.__num_params

    def get_num_locals(self) -> int:
        return self.__num_locals

    def __get_inv_labels(self) -> Dict[int, List[Label]]:
        result : Dict[int, List[Label]] = {}

        for label, offset in self.__labels.items():
            if offset in result:
                result[offset].append(label)
            else:
                result[offset] = [label]

        return result

    def __get_code(self) -> List[Union[Instruction, Label]]:
        code : List[Union[Instruction, Label]] = []
        inv_labels = self.__get_inv_labels()

        for idx, instr in enumerate(self.__instructions):
            if idx in inv_labels:
                code.extend(inv_labels[idx])

            code.append(instr)

        return code

    def to_xml(self) -> ET.Element:
        element = ET.Element("function", {"name": self.__name, "params": str(self.__num_params), "locals": str(self.__num_locals)})

        for elem in self.__get_code():
            if isinstance(elem, Instruction):
                element.append(elem.to_xml())
            else:
                element.append(ET.Element("LABEL", {"name": elem}))

        return element
    
    def to_nasm(self) -> str:
        string = f"FUNC_{self.__name}:"
        inv_labels = self.__get_inv_labels()

        for elem in self.__get_code():
            if isinstance(elem, Instruction):
                nasm = elem.to_nasm().replace('\n', '\n    ')
                string += f"\n    {nasm}"
            else:
                string += f"\n  .{elem}:"

        return string

    def __str__(self) -> str:
        return xml.dom.minidom.parseString(ET.tostring(self.to_xml(), 'unicode')).toprettyxml(indent='    ')

class Program:
    def __init__(self) -> None:
        self.__functions : Dict[str, Function] = {}
        self.__entry : Optional[str] = None

    def add_function(self, function: Function, is_entry: bool = False) -> None:
        assert function.get_name() not in self.__functions
        self.__functions[function.get_name()] = function

    def set_entry(self, func_name: str) -> None:
        assert self.__entry is None and func_name in self.__functions
        self.__entry = func_name

    def to_xml(self) -> ET.Element:
        assert self.__entry is not None

        document = ET.Element("program", {"slasm_version": _VERSION})
        code = ET.SubElement(document, "code", {"entry":self.__entry})

        for function in self.__functions.values():
            code.append(function.to_xml())

        return document

    def to_nasm(self) -> str:
        assert self.__entry is not None

        string = "    global _main\n\n    section .text"

        for function in self.__functions.values():
            if function.get_name() == self.__entry:
                string += f"\n_main:"

            string += f"\n{function.to_nasm()}"

        return string

    def __str__(self) -> str:
        return xml.dom.minidom.parseString(ET.tostring(self.to_xml(), 'unicode')).toprettyxml(indent='    ')
