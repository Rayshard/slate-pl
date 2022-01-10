from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict, Generic, List, TypeVar
from pylpc.pylpc import Location

class ASTNodeType(Enum):
    MODULE = auto()
    LITERAL = auto()

class ASTNode(ABC):
    def __init__(self, node_type: ASTNodeType, loc: Location) -> None:
        super().__init__()

        self.__node_type = node_type
        self.__location = loc

    def get_node_type(self) -> ASTNodeType:
        return self.__node_type

    def get_location(self) -> Location:
        return self.__location

    @abstractmethod
    def _on_serialize(self) -> Dict[str, Any]:
        pass

    def serialize(self) -> Dict[str, Any]:
        data = self._on_serialize()
        assert 'node_type' not in data
        assert 'location' not in data

        data['node_type'] = self.__node_type.name
        data['location'] = {
            "name": self.__location.name,
            "line": self.__location.position.line,
            "column": self.__location.position.column
        }
        return data

class ASTModule(ASTNode):
    def __init__(self, name: str, stmts: List[ASTNode], loc: Location) -> None:
        super().__init__(ASTNodeType.MODULE, loc)

        self.__name = name
        self.__stmts = stmts

    def get_name(self) -> str:
        return self.__name

    def get_stmts(self) -> List[ASTNode]:
        return self.__stmts

    def _on_serialize(self) -> Dict[str, Any]:
        return {
            "name": self.__name,
            "statements": [stmt.serialize() for stmt in self.__stmts]
        }

T = TypeVar('T', int, bool)

class ASTLiteral(ASTNode, Generic[T]):
    def __init__(self, value: T, loc: Location) -> None:
        super().__init__(ASTNodeType.LITERAL, loc)

        self.__value : T = value

    def get_value(self) -> T:
        return self.__value

    def _on_serialize(self) -> Dict[str, Any]:
        return { "value": self.__value }

