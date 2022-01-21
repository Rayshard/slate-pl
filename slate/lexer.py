from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, OrderedDict
import re

from slate.utilities import Location, Position

class TokenID(Enum):
    WS = auto()
    INTEGER = auto()
    KEYWORD = auto()
    ID = auto()
    SYMBOL = auto()
    EOS = auto()
    UNKNOWN = auto()

@dataclass(frozen=True)
class Token:
    id: TokenID
    position: Position
    value: str

_PATTERNS : OrderedDict[TokenID, re.Pattern[str]] = OrderedDict([
    (TokenID.WS, re.compile("\\s+")),
    (TokenID.INTEGER, re.compile("0|[1-9][0-9]*")),
    (TokenID.KEYWORD, re.compile("let")),
    (TokenID.ID, re.compile("[a-zA-Z_][a-zA-Z0-9_]*[']*")),
    (TokenID.SYMBOL, re.compile("\\+|\\-|\\*|\\/|\\(|\\)|=|;")),
    (TokenID.EOS, re.compile("$")),
    (TokenID.UNKNOWN, re.compile("[\\S\\s]")),
])

assert len(_PATTERNS) == len(TokenID) and all([id in TokenID for id in _PATTERNS])

class TokenStream:
    def __init__(self, name: str, data: str) -> None:
        self.__name = name
        self.__offset = int(0)
        self.__tokens = list[Token]()

        # Store offsets of beginnings of lines for position calculations
        line_starts : List[int] = [0]

        for i, c in enumerate(data):
            if c == '\n':
                line_starts.append(i + 1)

        # Generate tokens
        offset = int(0)

        while True:
            # Calculate position
            line : int = 0
            closest_line_start : int = 0

            for line_start in line_starts:
                if line_start > offset:
                    break

                closest_line_start = line_start
                line += 1

            position = Position(line, offset - closest_line_start + 1)

            # Match first-longest pattern
            longest : Optional[Token] = None

            for id, regex in _PATTERNS.items():
                regex_match : Optional[re.Match] = regex.match(data, offset)

                if regex_match is None:
                    continue
                        
                value = regex_match[0]

                if longest is None or len(value) > len(longest.value):
                    longest = Token(id, position, value)

            assert longest is not None

            offset += len(longest.value)
            self.__tokens.append(longest)
            
            if longest.id == TokenID.EOS:
                break

    def get_offset(self) -> int:
        return self.__offset

    def set_offset(self, value: int) -> None:
        self.__offset = max(0, min(value, len(self.__tokens) - 1))

    def peek(self) -> Token:
        return self.__tokens[self.__offset]

    def get(self) -> Token:
        token = self.peek()
        self.set_offset(self.__offset + 1)

        return token

    def get_location(self) -> Location:
        return Location(self.__name, self.peek().position)