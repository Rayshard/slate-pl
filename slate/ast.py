from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pylpc.pylpc import Position
from slate import typesystem

from slate.typesystem import ModuleContext, SlateType

_T = TypeVar('_T')

class ASTNode(ABC):
    def __init__(self, pos: Position, type_checked: bool = False) -> None:
        super().__init__()

        self.__position = pos
        self.__type_checked = type_checked

    def get_position(self) -> Position:
        return self.__position

    def is_type_checked(self) -> bool:
        return self.__type_checked

class ASTModule:
    def __init__(self, path: str, nodes: List[ASTNode], ctx: Optional[ModuleContext] = None) -> None:
        self.__path = path
        self.__nodes = nodes
        self.__ctx = ctx

    def get_path(self) -> str:
        return self.__path

    def get_nodes(self) -> List[ASTNode]:
        return self.__nodes

    def get_ctx(self) -> ModuleContext:
        assert self.__ctx is not None, "ASTModule is not type checked"
        return self.__ctx

class ASTExport(ASTNode):
    def __init__(self, node: ASTNode, pos: Position) -> None:
        super().__init__(pos, node.is_type_checked())

        self.__node = node

    def get_node(self) -> ASTNode:
        return self.__node

class ASTStmt(ASTNode, ABC):
    def __init__(self, pos: Position, type_checked: bool) -> None:
        super().__init__(pos, type_checked)

class ASTExpr(ASTStmt, ABC):
    def __init__(self, pos: Position, slate_type: Optional[SlateType]) -> None:
        super().__init__(pos, slate_type is not None)

        self.__slate_type = slate_type

    def get_slate_type(self) -> SlateType:
        assert self.__slate_type is not None, "Not type checked!"
        return self.__slate_type

class Binop(Enum):
    ADD = auto()
    SUB = auto()
    MULTIPLY = auto()
    DIVIDE = auto()

class ASTBinopExpr(ASTExpr):
    def __init__(self, lhs: ASTExpr, op: Binop, rhs: ASTExpr, pos: Position, slate_type: Optional[SlateType] = None) -> None:
        super().__init__(pos, slate_type)

        self.__lhs = lhs
        self.__rhs = rhs
        self.__op = op

    def get_op(self) -> Binop:
        return self.__op

    def get_lhs(self) -> ASTExpr:
        return self.__lhs

    def get_rhs(self) -> ASTExpr:
        return self.__rhs

class ASTLiteral(ASTExpr, Generic[_T], ABC):
    def __init__(self, value: _T, pos: Position, slate_type: Optional[SlateType]) -> None:
        super().__init__(pos, slate_type)

        self.__value = value

    def get_value(self) -> _T:
        return self.__value

class ASTIntegerLiteral(ASTLiteral[int]):
    def __init__(self, value: int, pos: Position) -> None:
        super().__init__(value, pos, typesystem.I64())

class ASTVarDecl(ASTStmt):
    def __init__(self, id: str, constraint: Optional[SlateType], expr: ASTExpr, pos: Position, type_checked: bool = False) -> None:
        super().__init__(pos, type_checked)

        self.__id = id
        self.__constraint = constraint
        self.__expr = expr

    def get_id(self) -> str:
        return self.__id

    def get_constraint(self) -> Optional[SlateType]:
        return self.__constraint

    def get_expr(self) -> ASTExpr:
        return self.__expr
