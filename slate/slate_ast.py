from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict, List, Type, cast
from pylpc.pylpc import Position

Serialization = Dict[str, Any]

class ASTNodeType(Enum):
    EXPR = auto()

class ASTNode(ABC):
    def __init__(self, node_type: ASTNodeType, pos: Position) -> None:
        super().__init__()

        self.__node_type = node_type
        self.__position = pos

    def get_node_type(self) -> ASTNodeType:
        return self.__node_type

    def get_position(self) -> Position:
        return self.__position

class ASTModule:
    def __init__(self, path: str, nodes: List[ASTNode]) -> None:
        self.__path = path
        self.__nodes = nodes

    def get_path(self) -> str:
        return self.__path

    def get_nodes(self) -> List[ASTNode]:
        return self.__nodes

class ASTExprType(Enum):
    LITERAL = auto()
    BINOP = auto()

class ASTExpr(ASTNode, ABC):
    def __init__(self, expr_type: ASTExprType, pos: Position) -> None:
        super().__init__(ASTNodeType.EXPR, pos)

        self.__expr_type = expr_type

    def get_expr_type(self) -> ASTExprType:
        return self.__expr_type

class ASTLiteralType(Enum):
    INTEGER = auto()

class Binop(Enum):
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()

class ASTBinopExpr(ASTExpr):
    def __init__(self, lhs: ASTExpr, op: Binop, rhs: ASTExpr, pos: Position) -> None:
        super().__init__(ASTExprType.BINOP, pos)

        self.__lhs = lhs
        self.__rhs = rhs
        self.__op = op

    def get_op(self) -> Binop:
        return self.__op

    def get_lhs(self) -> ASTExpr:
        return self.__lhs

    def get_rhs(self) -> ASTExpr:
        return self.__rhs

class ASTLiteral(ASTExpr, ABC):
    def __init__(self, lit_type: ASTLiteralType, pos: Position) -> None:
        super().__init__(ASTExprType.LITERAL, pos)

        self.__lit_type = lit_type

    def get_lit_type(self) -> ASTLiteralType:
        return self.__lit_type

class ASTIntegerLiteral(ASTLiteral):
    def __init__(self, value: int, pos: Position) -> None:
        super().__init__(ASTLiteralType.INTEGER, pos)

        self.__value = value

    def get_value(self) -> int:
        return self.__value
