from enum import Enum, auto
from typing import Literal

from slate.utilities import i64, ui64


def VERSION() -> str:
    return "1.0"

class DataType(Enum):
    UNDEFINED = auto()
    I8 = auto()
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

    def as_i64(self) -> i64:
        return i64(int.from_bytes(self.bytes, 'little', signed=True))

    def as_ui64(self) -> int:
        return ui64.from_bytes(self.bytes, 'little', signed=False)

    @staticmethod
    def FromI64(value: i64) -> 'Word':
        return Word(value.to_bytes(8, 'little', signed=True))

    @staticmethod
    def FromUI64(value: ui64) -> 'Word':
        return Word(value.to_bytes(8, 'little', signed=False))

    @staticmethod
    def SIZE() -> int:
        return 8