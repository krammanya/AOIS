from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    VARIABLE = "VARIABLE"
    OPERATOR = "OPERATOR"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str