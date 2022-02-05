from enum import Enum, auto
from typing import Any, List, Type, TypeVar, cast

from slasm.slasm import DataType, Word
from llvmlite import ir # type: ignore


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

    INLINE_NASM = auto()
    INLINE_LLVM = auto()

_TOperand = TypeVar("_TOperand")
Operand = Any
Label = str

class Instruction:
    def __init__(self, opcode: OpCode, operands: List[Operand]) -> None:
        self.__opcode = opcode
        self.__operands = operands

    @property
    def opcode(self) -> OpCode:
        return self.__opcode

    @property
    def operands(self) -> List[Operand]:
        return self.__operands

    def get_operand(self, idx: int, op_type: Type[_TOperand]) -> _TOperand:
        assert idx < len(self.__operands)
        assert isinstance(self.__operands[idx], op_type)
        return cast(op_type, self.__operands[idx]) # type: ignore

def Noop() -> 'Instruction':
    return Instruction(OpCode.NOOP, [])

def LoadConst(value: Word) -> 'Instruction':
    return Instruction(OpCode.LOAD_CONST, [value])

def LoadLabel(label: Label) -> 'Instruction':
    return Instruction(OpCode.LOAD_LABEL, [label])

def LoadLocal(idx: int) -> 'Instruction':
    return Instruction(OpCode.LOAD_LOCAL, [Word.FromUI64(idx)])

def LoadParam(idx: int) -> 'Instruction':
    return Instruction(OpCode.LOAD_PARAM, [Word.FromUI64(idx)])

def LoadGlobal(name: str) -> 'Instruction':
    return Instruction(OpCode.LOAD_GLOBAL, [name])

def LoadMem(offset: int) -> 'Instruction':
    return Instruction(OpCode.LOAD_MEM, [Word.FromI64(offset)])

def StoreLocal(idx: int) -> 'Instruction':
    return Instruction(OpCode.STORE_LOCAL, [Word.FromUI64(idx)])

def StoreParam(idx: int) -> 'Instruction':
    return Instruction(OpCode.STORE_PARAM, [Word.FromUI64(idx)])

def StoreGlobal(name: str) -> 'Instruction':
    return Instruction(OpCode.STORE_GLOBAL, [name])

def StoreMem(offset: int) -> 'Instruction':
    return Instruction(OpCode.STORE_MEM, [Word.FromI64(offset)])

def Add(dt: DataType) -> 'Instruction':
    return Instruction(OpCode.ADD, [dt])

def Sub(dt: DataType) -> 'Instruction':
    return Instruction(OpCode.SUB, [dt])

def Mul(dt: DataType) -> 'Instruction':
    return Instruction(OpCode.MUL, [dt])

def DIV(dt: DataType) -> 'Instruction':
    return Instruction(OpCode.DIV, [dt])

def MOD(dt: DataType) -> 'Instruction':
    return Instruction(OpCode.MOD, [dt])

def NEG(dt: DataType) -> 'Instruction':
    return Instruction(OpCode.NEG, [dt])

def INC(dt: DataType) -> 'Instruction':
    return Instruction(OpCode.INC, [dt])

def DEC(dt: DataType) -> 'Instruction':
    return Instruction(OpCode.DEC, [dt])

def EQ(dt: DataType) -> 'Instruction':
    return Instruction(OpCode.EQ, [dt])

def NEQ(dt: DataType) -> 'Instruction':
    return Instruction(OpCode.NEQ, [dt])

def GT(dt: DataType) -> 'Instruction':
    return Instruction(OpCode.GT, [dt])

def LT(dt: DataType) -> 'Instruction':
    return Instruction(OpCode.LT, [dt])

def GTEQ(dt: DataType) -> 'Instruction':
    return Instruction(OpCode.GTEQ, [dt])

def LTEQ(dt: DataType) -> 'Instruction':
    return Instruction(OpCode.LTEQ, [dt])

def OR() -> 'Instruction':
    return Instruction(OpCode.OR, [])

def AND() -> 'Instruction':
    return Instruction(OpCode.AND, [])

def XOR() -> 'Instruction':
    return Instruction(OpCode.XOR, [])

def NOT() -> 'Instruction':
    return Instruction(OpCode.NOT, [])

def SHL(amt: int) -> 'Instruction':
    return Instruction(OpCode.SHL, [amt])

def SHR(amt: int) -> 'Instruction':
    return Instruction(OpCode.SHR, [amt])

def Jump(label: Label) -> 'Instruction':
    return Instruction(OpCode.JUMP, [label])

def JumpZ(label: Label) -> 'Instruction':
    return Instruction(OpCode.JUMPZ, [label])

def JumpNZ(label: Label) -> 'Instruction':
    return Instruction(OpCode.JUMPNZ, [label])

def SJump() -> 'Instruction':
    return Instruction(OpCode.SJUMP, [])

def SJumpZ() -> 'Instruction':
    return Instruction(OpCode.SJUMPZ, [])

def SJumpNZ() -> 'Instruction':
    return Instruction(OpCode.SJUMPNZ, [])

def Call(label: Label) -> 'Instruction':
    return Instruction(OpCode.CALL, [label])

def SCall() -> 'Instruction':
    return Instruction(OpCode.SCALL, [])

def Pop() -> 'Instruction':
    return Instruction(OpCode.POP, [])

def Ret() -> 'Instruction':
    return Instruction(OpCode.RET, [])

def InlineNasm(asm: str) -> 'Instruction':
    return Instruction(OpCode.INLINE_NASM, [asm])

def InlineLLVM(asm: ir.Value) -> 'Instruction':
    return Instruction(OpCode.INLINE_LLVM, [asm])
