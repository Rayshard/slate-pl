from dataclasses import dataclass
from pylpc.pylpc import Position

@dataclass
class Location:
    file_path: str
    position: Position

    def __str__(self) -> str:
        return f"{self.file_path}:{self.position.line}:{self.position.column}"