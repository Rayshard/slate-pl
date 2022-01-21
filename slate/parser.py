from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

from slate.ast import ASTBinopExpr, ASTExpr, ASTIntegerLiteral, ASTModule, ASTVarDecl, Binop
from slate.lexer import Token, TokenID, TokenStream
from slate.utilities import Location, Position

@dataclass
class Context:
    modules : Dict[str, ASTModule] = field(default_factory=dict)

class ParseError(Exception):
    def __init__(self, loc: Location, msg: str = "", trace: Optional[List['ParseError']] = None) -> None:
        super().__init__(f"{loc} [Error] {msg}")
        
        self.__location = loc
        self.__message = msg
        self.__trace = [] if trace is None else trace
        
    def get_location(self) -> Location:
        return self.__location

    def get_message(self) -> str:
        return self.__message

    def get_trace(self) -> List['ParseError']:
        return self.__trace

    def get_message_with_trace(self) -> str:
        trace_message : str = ""

        for e in self.__trace:
            trace_message += "\n\t" + e.get_message_with_trace().replace("\n", "\n\t")

        return str(self) + trace_message

    @staticmethod
    def Combine(e1: 'ParseError', e2: 'ParseError') -> 'ParseError':
        return ParseError(e1.__location, e1.__message, e1.__trace + [e2])

    @staticmethod
    def Expectation(expected: str, found: str, loc: Location) -> 'ParseError':
        return ParseError(loc, f"Expected {expected}, but found {found}")

    @staticmethod
    def Unexpected(found: str, loc: Location) -> 'ParseError':
        return ParseError(loc, f"Encounted unexpected {found}")

# __LEXER = Lexer([
#     Pattern("WS", Regex("\\s+")),
#     Pattern("INTEGER", Regex("0|[1-9][0-9]*")),
#     Pattern("KEYWORD", Regex("let")),
#     Pattern("ID", Regex("[a-zA-Z_][a-zA-Z0-9_]*[']*")),
#     Pattern("SYMBOL", Regex("\\+|\\-|\\*|\\/|\\(|\\)|="))
# ])

# __T_WS = Lexeme(__LEXER, "WS")
# __OPT_WS = Maybe(__T_WS)

# __T_KW_LET = __OPT_WS >> Lexeme(__LEXER, "SYMBOL", "let")
# __T_INTEGER = __OPT_WS >> Lexeme(__LEXER, "INTEGER")
# __T_ID = __OPT_WS >> Lexeme(__LEXER, "ID")
# __T_SYMBOL = __OPT_WS >> Lexeme(__LEXER, "SYMBOL")
# __T_LPAREN = __OPT_WS >> Lexeme(__LEXER, "SYMBOL", "(")
# __T_RPAREN = __OPT_WS >> Lexeme(__LEXER, "SYMBOL", ")")
# __T_EQUALS = __OPT_WS >> Lexeme(__LEXER, "SYMBOL", "=")

# __INT_LIT = Map(__T_INTEGER, lambda result: ASTIntegerLiteral(int(result.value), result.location.position))
# __VAR_DECL = Map(__T_KW_LET >> __T_ID << __T_EQUALS, lambda result: ASTIntegerLiteral(int(result.value), result.location.position))

@dataclass
class __BinopToken:
    precedence : int
    op : Binop
    is_right_assoc : bool
    position : Position

def __OptWS(stream: TokenStream) -> None:
    while stream.peek().id == TokenID.WS:
        stream.get()

def __TOKEN(stream: TokenStream, id: TokenID, value: Optional[str] = None) -> Token:
    location = stream.get_location()
    token = stream.get()

    if token.id != id or (value is not None and token.value != value):
        raise ParseError.Expectation(f"{id.name}({value})", f"{token.id.name}({token.value})", location)

    return token

def __BINOP(stream: TokenStream) -> __BinopToken:
    location = stream.get_location()
    token = __TOKEN(stream, TokenID.SYMBOL)

    if token.value == "+":
        return __BinopToken(0, Binop.ADD, False, token.position)
    elif token.value == "-":
        return __BinopToken(0, Binop.SUB, False, token.position)
    elif token.value == "*":
        return __BinopToken(1, Binop.MULTIPLY, False, token.position)
    elif token.value == "/":
        return __BinopToken(1, Binop.DIVIDE, False, token.position)

    raise ParseError.Expectation("Binary Operator", f"{token.id.name}({token.value})", location)

def __LPAREN(stream: TokenStream) -> None:
    return __TOKEN(stream, TokenID.SYMBOL, "(")

def __RPAREN(stream: TokenStream) -> None:
    return __TOKEN(stream, TokenID.SYMBOL, ")")

def __EQUALS(stream: TokenStream) -> None:
    return __TOKEN(stream, TokenID.SYMBOL, "=")

def __SEMICOLON(stream: TokenStream) -> None:
    return __TOKEN(stream, TokenID.SYMBOL, ";")

def __KW_LET(stream: TokenStream) -> None:
    return __TOKEN(stream, TokenID.KEYWORD, "let")

def __ID(stream: TokenStream) -> Token:
    return __TOKEN(stream, TokenID.ID)

def __INT_LIT(stream: TokenStream) -> ASTIntegerLiteral:
    token = __TOKEN(stream, TokenID.INTEGER)    
    return ASTIntegerLiteral(int(token.value), token.position)

def __Atom(stream: TokenStream) -> ASTExpr:
    stream_start = stream.get_offset()

    try:
        return __INT_LIT(stream)
    except ParseError:
        stream.set_offset(stream_start)

    try:
        __LPAREN(stream)
        __OptWS(stream)
        expr = __Expr(stream)
        __OptWS(stream)
        __RPAREN(stream)

        return expr
    except ParseError:
        stream.set_offset(stream_start)

    raise ParseError.Unexpected(stream.peek().id.name, stream.get_location())

def __Expr(stream: TokenStream, cur_precedence: int = 0) -> ASTExpr:
    expr = __Atom(stream)

    while True:
        stream_start = stream.get_offset()

        try:
            __OptWS(stream)
            op = __BINOP(stream)

            if op.precedence < cur_precedence:
                stream.set_offset(stream_start)
                break

            __OptWS(stream)
            rhs = __Expr(stream, cur_precedence if op.is_right_assoc else (cur_precedence + 1))
            expr = ASTBinopExpr(expr, op.op, rhs, op.position)
        except ParseError:
            stream.set_offset(stream_start)
            break

    return expr

def __VarDecl(stream: TokenStream) -> ASTVarDecl:
    position = stream.get_location().position

    __KW_LET(stream)
    __OptWS(stream)
    id = __ID(stream)
    __OptWS(stream)
    __EQUALS(stream)
    __OptWS(stream)
    expr = __Expr(stream)
    __OptWS(stream)
    __SEMICOLON(stream)

    return ASTVarDecl(id.value, None, expr, position)

def __Module(stream: TokenStream, path: str) -> ASTModule:
    __OptWS(stream)
    return ASTModule(path, [__VarDecl(stream)])

def parse_file(path: Path, context: Context):
    posix_path = path.as_posix()

    if path.suffix != ".slt":
        raise ParseError(Location(posix_path), msg=f"Unable to parse non-slate file '{posix_path}'. File must has extension '.slt'!")
    elif posix_path not in context.modules:
        with path.open() as file:
            stream = TokenStream(posix_path, file.read())
            context.modules[posix_path] = __Module(stream, posix_path)