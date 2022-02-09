from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Literal, Union

from slate.slasm.slasm import DataType, Word
from slate.utilities import i64, ui64, uint


class OpCode(Enum):
    NOOP = 0

    LOAD_CONST = auto()
    LOAD_LOCAL = auto()
    LOAD_PARAM = auto()
    LOAD_GLOBAL = auto()
    LOAD_MEM = auto()
    LOAD_FUNC_ADDR = auto()

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
    COND_JUMP = auto()
    CALL = auto()
    INDIRECT_CALL = auto()
    NATIVE_CALL = auto()
    RET = auto()

class _Instruction(ABC):
    @property
    @abstractmethod
    def opcode(self) -> OpCode:
        pass

@dataclass(frozen=True)
class NOOP(_Instruction):
    @property
    def opcode(self) -> OpCode:
        return OpCode.NOOP

@dataclass(frozen=True)
class LOAD_CONST(_Instruction):
    value : Word

    @property
    def opcode(self) -> OpCode:
        return OpCode.LOAD_CONST

@dataclass(frozen=True)
class LOAD_FUNC_ADDR(_Instruction):
    name : str

    @property
    def opcode(self) -> OpCode:
        return OpCode.LOAD_FUNC_ADDR

@dataclass(frozen=True)
class LOAD_LOCAL(_Instruction):
    idx : ui64

    @property
    def opcode(self) -> OpCode:
        return OpCode.LOAD_LOCAL

@dataclass(frozen=True)
class LOAD_PARAM(_Instruction):
    idx : ui64

    @property
    def opcode(self) -> OpCode:
        return OpCode.LOAD_PARAM

@dataclass(frozen=True)
class LOAD_GLOBAL(_Instruction):
    name : str

    @property
    def opcode(self) -> OpCode:
        return OpCode.LOAD_GLOBAL

@dataclass(frozen=True)
class LOAD_MEM(_Instruction):
    offset : i64

    @property
    def opcode(self) -> OpCode:
        return OpCode.LOAD_MEM

@dataclass(frozen=True)
class STORE_LOCAL(_Instruction):
    idx : ui64

    @property
    def opcode(self) -> OpCode:
        return OpCode.STORE_LOCAL

@dataclass(frozen=True)
class STORE_PARAM(_Instruction):
    idx : ui64

    @property
    def opcode(self) -> OpCode:
        return OpCode.STORE_PARAM

@dataclass(frozen=True)
class STORE_GLOBAL(_Instruction):
    name : str

    @property
    def opcode(self) -> OpCode:
        return OpCode.STORE_GLOBAL

@dataclass(frozen=True)
class STORE_MEM(_Instruction):
    offset : i64

    @property
    def opcode(self) -> OpCode:
        return OpCode.STORE_MEM

@dataclass(frozen=True)
class POP(_Instruction):
    @property
    def opcode(self) -> OpCode:
        return OpCode.POP

@dataclass(frozen=True)
class ADD(_Instruction):
    data_type: DataType

    @property
    def opcode(self) -> OpCode:
        return OpCode.ADD

@dataclass(frozen=True)
class SUB(_Instruction):
    data_type: DataType
    
    @property
    def opcode(self) -> OpCode:
        return OpCode.SUB

@dataclass(frozen=True)
class MUL(_Instruction):
    data_type: DataType
    
    @property
    def opcode(self) -> OpCode:
        return OpCode.MUL

@dataclass(frozen=True)
class DIV(_Instruction):
    data_type: DataType
    
    @property
    def opcode(self) -> OpCode:
        return OpCode.DIV

@dataclass(frozen=True)
class MOD(_Instruction):
    data_type: DataType
    
    @property
    def opcode(self) -> OpCode:
        return OpCode.MOD

@dataclass(frozen=True)
class INC(_Instruction):
    data_type: DataType
    
    @property
    def opcode(self) -> OpCode:
        return OpCode.INC

@dataclass(frozen=True)
class DEC(_Instruction):
    data_type: DataType
    
    @property
    def opcode(self) -> OpCode:
        return OpCode.DEC

@dataclass(frozen=True)
class EQ(_Instruction):
    data_type: DataType
    
    @property
    def opcode(self) -> OpCode:
        return OpCode.EQ

@dataclass(frozen=True)
class NEQ(_Instruction):
    data_type: DataType
    
    @property
    def opcode(self) -> OpCode:
        return OpCode.NEQ

@dataclass(frozen=True)
class GT(_Instruction):
    data_type: DataType
    
    @property
    def opcode(self) -> OpCode:
        return OpCode.GT

@dataclass(frozen=True)
class LT(_Instruction):
    data_type: DataType
    
    @property
    def opcode(self) -> OpCode:
        return OpCode.LT

@dataclass(frozen=True)
class LTEQ(_Instruction):
    data_type: DataType
    
    @property
    def opcode(self) -> OpCode:
        return OpCode.LTEQ

@dataclass(frozen=True)
class GTEQ(_Instruction):
    data_type: DataType
    
    @property
    def opcode(self) -> OpCode:
        return OpCode.GTEQ

@dataclass(frozen=True)
class NEG(_Instruction):
    data_type: Literal[DataType.I8, DataType.I16, DataType.I32, DataType.I64, DataType.F32, DataType.F64]
    
    @property
    def opcode(self) -> OpCode:
        return OpCode.NEG

@dataclass(frozen=True)
class OR(_Instruction):
    @property
    def opcode(self) -> OpCode:
        return OpCode.OR

@dataclass(frozen=True)
class AND(_Instruction):
    @property
    def opcode(self) -> OpCode:
        return OpCode.AND

@dataclass(frozen=True)
class XOR(_Instruction):
    @property
    def opcode(self) -> OpCode:
        return OpCode.XOR

@dataclass(frozen=True)
class NOT(_Instruction):
    @property
    def opcode(self) -> OpCode:
        return OpCode.NOT

@dataclass(frozen=True)
class SHL(_Instruction):
    amt : Literal[0, 1, 2, 3, 4, 5, 6, 7, 8]

    @property
    def opcode(self) -> OpCode:
        return OpCode.SHL

@dataclass(frozen=True)
class SHR(_Instruction):
    amt : Literal[0, 1, 2, 3, 4, 5, 6, 7, 8]
    
    @property
    def opcode(self) -> OpCode:
        return OpCode.SHR

@dataclass(frozen=True)
class CONVERT(_Instruction):
    from_dt: DataType
    to_dt: DataType
    
    @property
    def opcode(self) -> OpCode:
        return OpCode.CONVERT

@dataclass(frozen=True)
class JUMP(_Instruction):
    target : str
    
    @property
    def opcode(self) -> OpCode:
        return OpCode.JUMP

@dataclass(frozen=True)
class COND_JUMP(_Instruction):
    true_target : str
    false_target : str
    
    @property
    def opcode(self) -> OpCode:
        return OpCode.COND_JUMP

@dataclass(frozen=True)
class CALL(_Instruction):
    target : str
    
    @property
    def opcode(self) -> OpCode:
        return OpCode.CALL

@dataclass(frozen=True)
class INDIRECT_CALL(_Instruction):
    @property
    def opcode(self) -> OpCode:
        return OpCode.INDIRECT_CALL

@dataclass(frozen=True)
class NATIVE_CALL(_Instruction):
    target : str
    num_params : uint
    returns_value : bool
    
    @property
    def opcode(self) -> OpCode:
        return OpCode.CALL

@dataclass(frozen=True)
class RET(_Instruction):
    @property
    def opcode(self) -> OpCode:
        return OpCode.RET

Instruction = Union[
    NOOP,
    LOAD_CONST,
    LOAD_LOCAL,
    LOAD_PARAM,
    LOAD_GLOBAL,
    LOAD_MEM,
    LOAD_FUNC_ADDR,
    POP,
    STORE_LOCAL,
    STORE_PARAM,
    STORE_GLOBAL,
    STORE_MEM,
    ADD,
    SUB,
    MUL,
    DIV,
    MOD,
    INC,
    DEC,
    EQ,
    NEQ,
    GT,
    LT,
    GTEQ,
    LTEQ,
    NEG,
    OR,
    AND,
    XOR,
    NOT,
    SHL,
    SHR,
    CONVERT,
    JUMP,
    COND_JUMP,
    CALL,
    INDIRECT_CALL,
    NATIVE_CALL,
    RET
]