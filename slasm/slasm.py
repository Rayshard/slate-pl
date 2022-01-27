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
    INC = auto()
    DEC = auto()
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
    SHL = auto()
    SHR = auto()

    CONVERT = auto()

    JUMP = auto()
    JUMPZ = auto()
    JUMPNZ = auto()
    SJUMP = auto()
    SJUMPZ = auto()
    SJUMPNZ = auto()
    CALL = auto()
    SCALL = auto()
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

    def as_hex(self, endianness: Literal['little', 'big'] = 'big') -> str:
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
            return ET.Element("LOAD_CONST", {"value": self.get_operand(0, Word).as_hex()})
        elif self.__opcode == OpCode.LOAD_LABEL:
            return ET.Element("LOAD_LABEL", {"label": self.get_operand(0, str)})
        elif self.__opcode == OpCode.LOAD_LOCAL:
            return ET.Element("LOAD_LOCAL", {"idx": str(self.get_operand(0, Word).as_ui64())})
        elif self.__opcode == OpCode.LOAD_PARAM:
            return ET.Element("LOAD_PARAM", {"idx": str(self.get_operand(0, Word).as_ui64())})
        elif self.__opcode == OpCode.LOAD_GLOBAL:
            return ET.Element("LOAD_GLOBAL", {"name": self.get_operand(0, str)})
        elif self.__opcode == OpCode.LOAD_MEM:
            return ET.Element("LOAD_MEM", {"offset": str(self.get_operand(0, Word).as_i64())})
        elif self.__opcode == OpCode.STORE_LOCAL:
            return ET.Element("STORE_LOCAL", {"idx": str(self.get_operand(0, Word).as_ui64())})
        elif self.__opcode == OpCode.STORE_PARAM:
            return ET.Element("STORE_PARAM", {"idx": str(self.get_operand(0, Word).as_ui64())})
        elif self.__opcode == OpCode.STORE_GLOBAL:
            return ET.Element("STORE_GLOBAL", {"name": self.get_operand(0, str)})
        elif self.__opcode == OpCode.STORE_MEM:
            return ET.Element("STORE_MEM", {"offset": str(self.get_operand(0, Word).as_i64())})
        elif self.__opcode == OpCode.POP:
            return ET.Element("POP")
        elif self.__opcode == OpCode.ADD:
            return ET.Element("ADD", {"type": str(self.get_operand(0, DataType).name)})
        elif self.__opcode == OpCode.SUB:
            return ET.Element("SUB", {"type": str(self.get_operand(0, DataType).name)})
        elif self.__opcode == OpCode.MUL:
            return ET.Element("MUL", {"type": str(self.get_operand(0, DataType).name)})
        elif self.__opcode == OpCode.DIV:
            return ET.Element("DIV", {"type": str(self.get_operand(0, DataType).name)})
        elif self.__opcode == OpCode.MOD:
            return ET.Element("MOD", {"type": str(self.get_operand(0, DataType).name)})
        elif self.__opcode == OpCode.RET:
            return ET.Element("RET")
        elif self.__opcode == OpCode.SYSCALL_LINUX:
            return ET.Element("SYSCALL_LINUX", {"code": str(self.get_operand(0, Word).as_ui64()), "num_params": str(self.get_operand(1, int))})
        
        assert False, "Not implemented"    

    def to_nasm(self) -> str:
        string : str = ""

        if self.__opcode == OpCode.NOOP:
            string = "; NOOP\n" \
                     "XCHG RAX, RAX"
        elif self.__opcode == OpCode.LOAD_CONST:
            value_hex = self.get_operand(0, Word).as_hex()
            string = f"; LOAD_CONST {value_hex}\n" \
                     f"MOV RAX, {value_hex}\n" \
                      "PUSH RAX"
        elif self.__opcode == OpCode.LOAD_LABEL:
            label = self.get_operand(0, str)
            string = f"; LOAD_LABEL {label}\n" \
                     f"LEA RAX, [REL .{label}]\n" \
                      "PUSH RAX"
        elif self.__opcode == OpCode.LOAD_LOCAL:
            idx = self.get_operand(0, Word).as_ui64()
            string = f"; LOAD_LOCAL {idx}\n" \
                     f"PUSH QWORD [RBP-{(idx + 1) * Word.SIZE()}]"
        elif self.__opcode == OpCode.LOAD_PARAM:
            idx = self.get_operand(0, Word).as_ui64()
            string = f"; LOAD_PARAM {idx}\n" \
                     f"PUSH QWORD [RBP+{(idx + 2) * Word.SIZE()}]"
        elif self.__opcode == OpCode.LOAD_GLOBAL:
            name = self.get_operand(0, str)
            string = f"; LOAD_GLOBAL {name}\n" \
                     f"PUSH QWORD [REL {name}]"
        elif self.__opcode == OpCode.LOAD_MEM:
            offset = self.get_operand(0, Word).as_i64()
            sign = "-" if offset < 0 else "+"
            string = f"; LOAD_MEM {offset}\n" \
                      "POP RAX\n" \
                     f"PUSH QWORD [RAX{sign}{offset}]"
        elif self.__opcode == OpCode.STORE_LOCAL:
            idx = self.get_operand(0, Word).as_ui64()
            string = f"; STORE_LOCAL {idx}\n" \
                     f"POP QWORD [RBP-{(idx + 1) * Word.SIZE()}]"
        elif self.__opcode == OpCode.STORE_PARAM:
            idx = self.get_operand(0, Word).as_ui64()
            string = f"; STORE_PARAM {idx}\n" \
                     f"POP QWORD [RBP+{(idx + 2) * Word.SIZE()}]"
        elif self.__opcode == OpCode.STORE_GLOBAL:
            name = self.get_operand(0, str)
            string = f"; STORE_GLOBAL {name}\n" \
                     f"POP QWORD [REL {name}]"
        elif self.__opcode == OpCode.STORE_MEM:
            offset = self.get_operand(0, Word).as_i64()
            sign = "-" if offset < 0 else "+"
            string = f"; STORE_MEM {offset}\n" \
                      "POP RAX\n" \
                     f"POP QWORD [RAX{sign}{offset}]"
        elif self.__opcode == OpCode.POP:
            string = "; POP\n" \
                     "POP RAX"
        elif self.__opcode == OpCode.RET:
            string = "; RET\n" \
                     "RET"
        elif self.__opcode == OpCode.ADD:
            dt = self.get_operand(0, DataType)
            string = f"; ADD {dt.name}\n" \
                      "POP RAX\n" \
                      "POP RBX\n"
                     
            if dt == DataType.I8 or dt == DataType.UI8:
                string += "ADD AL, BL\n"
            elif dt == DataType.I16 or dt == DataType.UI16:
                string += "ADD AX, BX\n"
            elif dt == DataType.I32 or dt == DataType.UI32:
                string += "ADD EAX, EBX\n"
            elif dt == DataType.I64 or dt == DataType.UI64:
                string += "ADD RAX, RBX\n"
            elif dt == DataType.F32:
                string += "MOVQ XMM0, RAX\n" \
                          "MOVQ XMM1, RBX\n" \
                          "ADDSS XMM0, XMM1\n" \
                          "MOVQ RAX, XMM0\n"
            elif dt == DataType.F64:
                string += "MOVQ XMM0, RAX\n" \
                          "MOVQ XMM1, RBX\n" \
                          "ADDSD XMM0, XMM1\n" \
                          "MOVQ RAX, XMM0\n"
            else:
                assert False, "Not implemented"

            string += "PUSH RAX" 
        elif self.__opcode == OpCode.SUB:
            dt = self.get_operand(0, DataType)
            string = f"; SUB {dt.name}\n" \
                      "POP RAX\n" \
                      "POP RBX\n"
                     
            if dt == DataType.I8 or dt == DataType.UI8:
                string += "SUB AL, BL\n"
            elif dt == DataType.I16 or dt == DataType.UI16:
                string += "SUB AX, BX\n"
            elif dt == DataType.I32 or dt == DataType.UI32:
                string += "SUB EAX, EBX\n"
            elif dt == DataType.I64 or dt == DataType.UI64:
                string += "SUB RAX, RBX\n"
            elif dt == DataType.F32:
                string += "MOVQ XMM0, RAX\n" \
                          "MOVQ XMM1, RBX\n" \
                          "SUBSS XMM0, XMM1\n" \
                          "MOVQ RAX, XMM0\n"
            elif dt == DataType.F64:
                string += "MOVQ XMM0, RAX\n" \
                          "MOVQ XMM1, RBX\n" \
                          "SUBSD XMM0, XMM1\n" \
                          "MOVQ RAX, XMM0\n"
            else:
                assert False, "Not implemented"

            string += "PUSH RAX"
        elif self.__opcode == OpCode.MUL:
            dt = self.get_operand(0, DataType)
            string = f"; MUL {dt.name}\n" \
                      "POP RAX\n" \
                      "POP RBX\n"
                     
            if dt == DataType.I8 or dt == DataType.UI8:
                string += "IMUL AL, BL\n"
            elif dt == DataType.I16 or dt == DataType.UI16:
                string += "IMUL AX, BX\n"
            elif dt == DataType.I32 or dt == DataType.UI32:
                string += "IMUL EAX, EBX\n"
            elif dt == DataType.I64 or dt == DataType.UI64:
                string += "IMUL RAX, RBX\n"
            elif dt == DataType.F32:
                string += "MOVQ XMM0, RAX\n" \
                          "MOVQ XMM1, RBX\n" \
                          "MULSS XMM0, XMM1\n" \
                          "MOVQ RAX, XMM0\n"
            elif dt == DataType.F64:
                string += "MOVQ XMM0, RAX\n" \
                          "MOVQ XMM1, RBX\n" \
                          "MULSD XMM0, XMM1\n" \
                          "MOVQ RAX, XMM0\n"
            else:
                assert False, "Not implemented"

            string += "PUSH RAX"
        elif self.__opcode == OpCode.DIV:
            dt = self.get_operand(0, DataType)
            string = f"; DIV {dt.name}\n" \
                      "POP RAX\n" \
                      "POP RBX\n"
                     
            if dt == DataType.I8:
                string += "MOVSX EAX, EAX\n" \
                          "MOVSX ECX, EBX\n" \
                          "CDQ\n" \
                          "IDIV ECX\n"
            elif dt == DataType.UI8:
                string += "MOV RDX, 0\n" \
                          "DIV BL\n"
            elif dt == DataType.I16:
                string += "MOVSX EAX, EAX\n" \
                          "MOVSX ECX, EBX\n" \
                          "CDQ\n" \
                          "IDIV ECX\n"
            elif dt == DataType.UI16:
                string += "MOV RDX, 0\n" \
                          "DIV BX\n"
            elif dt == DataType.I32:
                string += "CDQ\n" \
                          "IDIV EBX\n"
            elif dt == DataType.UI32:
                string += "MOV RDX, 0\n" \
                          "DIV EBX\n"
            elif dt == DataType.I64:
                string += "CQO\n" \
                          "IDIV RBX\n"
            elif dt == DataType.UI64:
                string += "MOV RDX, 0\n" \
                          "DIV RBX\n"
            elif dt == DataType.F32:
                string += "MOVQ XMM0, RAX\n" \
                          "MOVQ XMM1, RBX\n" \
                          "DIVSS XMM0, XMM1\n" \
                          "MOVQ RAX, XMM0\n"
            elif dt == DataType.F64:
                string += "MOVQ XMM0, RAX\n" \
                          "MOVQ XMM1, RBX\n" \
                          "DIVSD XMM0, XMM1\n" \
                          "MOVQ RAX, XMM0\n"
            else:
                assert False, "Not implemented"

            string += "PUSH RAX"
        elif self.__opcode == OpCode.MOD:
            dt = self.get_operand(0, DataType)
            string = f"; MOD {dt.name}\n" \
                      "POP RAX\n" \
                      "POP RBX\n"
                     
            if dt == DataType.I8:
                string += "MOVSX EAX, EAX\n" \
                          "MOVSX ECX, EBX\n" \
                          "CDQ\n" \
                          "IDIV ECX\n" \
                          "MOV EAX, EDX"
            elif dt == DataType.UI8:
                string += "MOV RDX, 0\n" \
                          "DIV BL\n" \
                          "MOV AL, BL"
            elif dt == DataType.I16:
                string += "MOVSX EAX, EAX\n" \
                          "MOVSX ECX, EBX\n" \
                          "CDQ\n" \
                          "IDIV ECX\n" \
                          "MOV AX, DX"
            elif dt == DataType.UI16:
                string += "MOV RDX, 0\n" \
                          "DIV BX\n" \
                          "MOV AX, DX"
            elif dt == DataType.I32:
                string += "CDQ\n" \
                          "IDIV EBX\n" \
                          "MOV EAX, EDX"
            elif dt == DataType.UI32:
                string += "MOV RDX, 0\n" \
                          "DIV EBX\n" \
                          "MOV EAX, EDX"
            elif dt == DataType.I64:
                string += "CQO\n" \
                          "IDIV RBX\n" \
                          "MOV RAX, RDX"
            elif dt == DataType.UI64:
                string += "MOV RDX, 0\n" \
                          "DIV RBX\n" \
                          "MOV RAX, RDX"
            elif dt == DataType.F32:
                string += "MOVQ XMM0, RAX\n" \
                          "MOVQ XMM1, RBX\n" \
                          "MOVQ XMM2, RAX\n" \
                          "DIVSS XMM2, XMM1\n" \
                          "CVTTSS2SI RAX, XMM2\n" \
                          "CVTSI2SS XMM2, RAX\n" \
                          "MULSS XMM2, XMM1\n" \
                          "SUBSS XMM0, XMM2\n" \
                          "MOVQ RAX, XMM0\n"
            elif dt == DataType.F64:
                string += "MOVQ XMM0, RAX\n" \
                          "MOVQ XMM1, RBX\n" \
                          "MOVQ XMM2, RAX\n" \
                          "DIVSD XMM2, XMM1\n" \
                          "CVTTSD2SI RAX, XMM2\n" \
                          "CVTSI2SD XMM2, RAX\n" \
                          "MULSD XMM2, XMM1\n" \
                          "SUBSD XMM0, XMM2\n" \
                          "MOVQ RAX, XMM0\n"
            else:
                assert False, "Not implemented"

            string += "PUSH RAX"
        elif self.__opcode == OpCode.SYSCALL_LINUX:
            __PARAM_REGISTERS = ["RDI", "RSI", "RDX", "R10", "R8", "R9"]
            syscall_code, num_params = self.get_operand(0, Word), self.get_operand(1, int)
            string = f"; SYSCALL_LINUX {syscall_code.as_ui64()}, {num_params}\n" \
                     f"MOV RAX, {syscall_code.as_hex()}"

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
    def Add(dt: DataType) -> 'Instruction':
        return Instruction(OpCode.ADD, [dt])

    @staticmethod
    def Sub(dt: DataType) -> 'Instruction':
        return Instruction(OpCode.SUB, [dt])

    @staticmethod
    def Mul(dt: DataType) -> 'Instruction':
        return Instruction(OpCode.MUL, [dt])

    @staticmethod
    def DIV(dt: DataType) -> 'Instruction':
        return Instruction(OpCode.DIV, [dt])

    @staticmethod
    def MOD(dt: DataType) -> 'Instruction':
        return Instruction(OpCode.MOD, [dt])

    @staticmethod
    def NEG(dt: DataType) -> 'Instruction':
        return Instruction(OpCode.NEG, [dt])

    @staticmethod
    def INC(dt: DataType) -> 'Instruction':
        return Instruction(OpCode.INC, [dt])

    @staticmethod
    def DEC(dt: DataType) -> 'Instruction':
        return Instruction(OpCode.DEC, [dt])

    @staticmethod
    def EQ(dt: DataType) -> 'Instruction':
        return Instruction(OpCode.EQ, [dt])

    @staticmethod
    def NEQ(dt: DataType) -> 'Instruction':
        return Instruction(OpCode.NEQ, [dt])

    @staticmethod
    def GT(dt: DataType) -> 'Instruction':
        return Instruction(OpCode.GT, [dt])
    
    @staticmethod
    def LT(dt: DataType) -> 'Instruction':
        return Instruction(OpCode.LT, [dt])

    @staticmethod
    def GTEQ(dt: DataType) -> 'Instruction':
        return Instruction(OpCode.GTEQ, [dt])
    
    @staticmethod
    def LTEQ(dt: DataType) -> 'Instruction':
        return Instruction(OpCode.LTEQ, [dt])

    @staticmethod
    def OR() -> 'Instruction':
        return Instruction(OpCode.OR, [])

    @staticmethod
    def AND() -> 'Instruction':
        return Instruction(OpCode.AND, [])

    @staticmethod
    def XOR() -> 'Instruction':
        return Instruction(OpCode.XOR, [])

    @staticmethod
    def NOT() -> 'Instruction':
        return Instruction(OpCode.NOT, [])

    @staticmethod
    def SHL(amt: int) -> 'Instruction':
        return Instruction(OpCode.SHL, [amt])

    @staticmethod
    def SHR(amt: int) -> 'Instruction':
        return Instruction(OpCode.SHR, [amt])

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
    def SJump() -> 'Instruction':
        return Instruction(OpCode.SJUMP, [])

    @staticmethod
    def SJumpZ() -> 'Instruction':
        return Instruction(OpCode.SJUMPZ, [])

    @staticmethod
    def SJumpNZ() -> 'Instruction':
        return Instruction(OpCode.SJUMPNZ, [])

    @staticmethod
    def Call(label: Label) -> 'Instruction':
        return Instruction(OpCode.CALL, [label])

    @staticmethod
    def SCall() -> 'Instruction':
        return Instruction(OpCode.SCALL, [])

    @staticmethod
    def Pop() -> 'Instruction':
        return Instruction(OpCode.POP, [])

    @staticmethod
    def Ret() -> 'Instruction':
        return Instruction(OpCode.RET, [])

    @staticmethod
    def SyscallLinux(code: int, num_params: int) -> 'Instruction':
        assert code >= 0
        assert 0 <= num_params <= 6
        return Instruction(OpCode.SYSCALL_LINUX, [Word.FromUI64(code), num_params])

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
