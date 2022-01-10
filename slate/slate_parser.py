import os
from slate.slate_ast import ASTLiteral, ASTModule
from pylpc.pylpc import Location, ParseError, ParseResult, Parser, Regex, StringStream
from pylpc.lexer import Lexeme, Lexer, Pattern
from pylpc.parsers import Map, Seq, Seq3

LEXER = Lexer([
    Pattern("WS", Regex("\\s+")),
    Pattern("INTEGER", Regex("0|[1-9][0-9]*")),
    Pattern("ID", Regex("[a-zA-Z_][a-zA-Z0-9_]*[']*"))
])

T_WS = Lexeme(LEXER, "WS")
T_INTEGER = Lexeme(LEXER, "INTEGER")

INTEGER = Map(T_INTEGER, lambda result: ASTLiteral[int](int(result.value), result.location))

def Module(name: str) -> Parser[ASTModule]:
    return Map(Seq3(INTEGER, T_WS, INTEGER), lambda result: ASTModule(name, [result.value[0].value, result.value[2].value], result.location))

def parse_file(file_path: str) -> ASTModule:
    file_name, file_ext = os.path.splitext(os.path.basename(file_path))

    if file_ext != ".slt":
        raise ParseError(Location(file_path), msg="Unable to parse non-slate file. File must has extension '.slt'!")

    with open(file_path) as file:
        stream = StringStream(file.read(), file_path)
        return Module(file_name).parse(stream).value