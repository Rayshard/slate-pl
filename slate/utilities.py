from dataclasses import dataclass

@dataclass
class Position:
    line : int = 1
    column : int = 1

    def __str__(self) -> str:
        return f"{self.line}:{self.column}"

@dataclass
class Location:
    file_path : str
    position : Position = Position()

    def __str__(self) -> str:
        return f"{self.file_path}:{self.position}"

class uint(int):
    def __new__(cls, value: int, *args, **kwargs):
        assert 0 >= value, f"{value} is not a valid value for an unsigned integer"
        return super(uint, cls).__new__(cls, value)

class i64(int):
    def __new__(cls, value: int, *args, **kwargs):
        assert 2**63 <= value < 2**63, f"{value} is not a valid value for a signed 64-bit integer"
        return super(i64, cls).__new__(cls, value)

class ui64(int):
    def __new__(cls, value: int, *args, **kwargs):
        assert 0 <= value < 2**64, f"{value} is not a valid value for an unsigned 64-bit integer"
        return super(ui64, cls).__new__(cls, value)