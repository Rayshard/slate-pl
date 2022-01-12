from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List
from pylpc.pylpc import Location, ParseError, Parser, Regex, StringStream
from pylpc.lexer import Lexeme, Lexer, Pattern
from pylpc.parsers import Map, Seq3

from slate.slate_ast import ASTIntegerLiteral, ASTModule

@dataclass
class Context:
    modules : Dict[str, ASTModule] = field(default_factory=dict)

LEXER = Lexer([
    Pattern("WS", Regex("\\s+")),
    Pattern("INTEGER", Regex("0|[1-9][0-9]*")),
    Pattern("ID", Regex("[a-zA-Z_][a-zA-Z0-9_]*[']*"))
])

T_WS = Lexeme(LEXER, "WS")
T_INTEGER = Lexeme(LEXER, "INTEGER")

INTEGER = Map(T_INTEGER, lambda result: ASTIntegerLiteral(int(result.value), result.location.position))

def Module(path: str) -> Parser[ASTModule]:
    return Map(Seq3(INTEGER, T_WS, INTEGER), lambda result: ASTModule(path, [result.value[0].value, result.value[2].value]))

def parse_file(path: Path, context: Context):
    posix_path = path.as_posix()

    if path.suffix != ".slt":
        raise ParseError(Location(posix_path), msg=f"Unable to parse non-slate file '{posix_path}'. File must has extension '.slt'!")
    elif posix_path not in context.modules:
        with path.open() as file:
            stream = StringStream(file.read(), posix_path)
            context.modules[posix_path] = Module(posix_path).parse(stream).value