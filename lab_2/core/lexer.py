import unicodedata

from core.tokens import Token, TokenType


class Lexer:
    VALID_VARIABLES = {"a", "b", "c", "d", "e"}

    def tokenize(self, expression: str) -> list[Token]:
        normalized_expression = self._normalize_expression(expression)
        tokens: list[Token] = []
        position = 0

        while position < len(normalized_expression):
            current_char = normalized_expression[position]

            if current_char in self.VALID_VARIABLES:
                tokens.append(Token(TokenType.VARIABLE, current_char))
                position += 1

            elif current_char == "(":
                tokens.append(Token(TokenType.LPAREN, current_char))
                position += 1

            elif current_char == ")":
                tokens.append(Token(TokenType.RPAREN, current_char))
                position += 1

            elif current_char in {"&", "|", "!", "~"}:
                tokens.append(Token(TokenType.OPERATOR, current_char))
                position += 1

            elif normalized_expression[position:position + 2] == "->":
                tokens.append(Token(TokenType.OPERATOR, "->"))
                position += 2

            else:
                raise ValueError(f"Недопустимый символ: '{current_char}'")

        return tokens

    def _normalize_expression(self, expression: str) -> str:
        replacements = {
            "∨": "|",
            "∧": "&",
            "¬": "!",
            "→": "->",
            "↔": "~",
        }
        normalized_parts: list[str] = []

        for char in expression:
            if char.isspace() or unicodedata.category(char) == "Cf":
                continue

            normalized_parts.append(replacements.get(char, char))

        return "".join(normalized_parts)
