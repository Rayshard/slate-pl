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