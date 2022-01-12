from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, cast
from pylpc.pylpc import Location, ParseError, ParseResult, Parser, Regex, StringStream
from pylpc.lexer import Lexeme, Lexer, Pattern
from pylpc.parsers import Map, FirstSuccess, Maybe, Satisfy, Between

from slate.ast import ASTBinopExpr, ASTExpr, ASTIntegerLiteral, ASTModule, Binop

@dataclass
class Context:
    modules : Dict[str, ASTModule] = field(default_factory=dict)

__LEXER = Lexer([
    Pattern("WS", Regex("\\s+")),
    Pattern("INTEGER", Regex("0|[1-9][0-9]*")),
    Pattern("ID", Regex("[a-zA-Z_][a-zA-Z0-9_]*[']*")),
    Pattern("SYMBOL", Regex("\\+|\\-|\\*|\\/|\\(|\\)"))
])

__T_WS = Lexeme(__LEXER, "WS")
__OPT_WS = Maybe(__T_WS)

__T_INTEGER = __OPT_WS >> Lexeme(__LEXER, "INTEGER")
__T_SYMBOL = __OPT_WS >> Lexeme(__LEXER, "SYMBOL")
__T_LPAREN = __OPT_WS >> Lexeme(__LEXER, "SYMBOL", "(")
__T_RPAREN = __OPT_WS >> Lexeme(__LEXER, "SYMBOL", ")")

__INT_LIT = Map(__T_INTEGER, lambda result: ASTIntegerLiteral(int(result.value), result.location.position))

@dataclass
class __BinopToken:
    precedence : int
    op : Binop
    is_right_assoc : bool

__BINOP_MAP = {
    "+": __BinopToken(0, Binop.ADD, False),
    "-": __BinopToken(0, Binop.SUB, False),
    "*": __BinopToken(1, Binop.MULTIPLY, False),
    "/": __BinopToken(1, Binop.DIVIDE, False)
}
__BINOP = Map(Satisfy(__T_SYMBOL, lambda result: result.value in __BINOP_MAP), lambda result: __BINOP_MAP[result.value])

def __Atom() -> Parser[ASTExpr]:
    return FirstSuccess([
            cast(Parser[ASTExpr], __INT_LIT),
            Between(__T_LPAREN, __Expr(), __T_RPAREN)
        ])

def __Expr() -> Parser[ASTExpr]:
    def function(stream: StringStream, cur_precedence: int) -> ParseResult[ASTExpr]:
        atom = __Atom().parse(stream)
        expr = atom.value

        while True:
            try:
                stream_start = stream.get_offset()
                op = __BINOP.parse(stream)

                if op.value.precedence < cur_precedence:
                    stream.set_offset(stream_start)
                    break

                rhs = function(stream, cur_precedence if op.value.is_right_assoc else (cur_precedence + 1)).value
                expr = ASTBinopExpr(expr, op.value.op, rhs, op.location.position)
            except ParseError as e:
                break

        return ParseResult(atom.location, expr)

    return Parser(lambda _, stream: function(stream, 0))

def __Module(path: str) -> Parser[ASTModule]:
    return Map(__Expr(), lambda result: ASTModule(path, [result.value]))

def parse_file(path: Path, context: Context):
    posix_path = path.as_posix()

    if path.suffix != ".slt":
        raise ParseError(Location(posix_path), msg=f"Unable to parse non-slate file '{posix_path}'. File must has extension '.slt'!")
    elif posix_path not in context.modules:
        with path.open() as file:
            stream = StringStream(file.read(), posix_path)
            context.modules[posix_path] = __Module(posix_path).parse(stream).value