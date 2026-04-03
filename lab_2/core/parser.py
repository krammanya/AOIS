from core.tokens import Token, TokenType


class Parser:
    PRIORITY = {
        "!": 5,
        "&": 4,
        "|": 3,
        "->": 2,
        "~": 1,
    }

    RIGHT_ASSOCIATIVE = {"!", "->"}
    BINARY_OPERATORS = {"&", "|", "->", "~"}

    def to_postfix(self, tokens: list[Token]) -> list[Token]:
        self._validate_token_sequence(tokens)

        output: list[Token] = []
        stack: list[Token] = []

        for token in tokens:
            if token.type == TokenType.VARIABLE:
                output.append(token)

            elif token.type == TokenType.OPERATOR:
                while stack and stack[-1].type == TokenType.OPERATOR:
                    top = stack[-1]
                    if self._should_pop(token, top):
                        output.append(stack.pop())
                    else:
                        break
                stack.append(token)

            elif token.type == TokenType.LPAREN:
                stack.append(token)

            elif token.type == TokenType.RPAREN:
                while stack and stack[-1].type != TokenType.LPAREN:
                    output.append(stack.pop())

                if not stack:
                    raise ValueError("Несогласованные скобки")

                stack.pop()

        while stack:
            if stack[-1].type in {TokenType.LPAREN, TokenType.RPAREN}:
                raise ValueError("Несогласованные скобки")
            output.append(stack.pop())

        return output

    def _validate_token_sequence(self, tokens: list[Token]) -> None:
        if not tokens:
            raise ValueError("Пустое выражение")

        self._validate_first_token(tokens[0])
        self._validate_last_token(tokens[-1])

        balance = 0

        for index in range(len(tokens)):
            current_token = tokens[index]

            if current_token.type == TokenType.LPAREN:
                balance += 1
            elif current_token.type == TokenType.RPAREN:
                balance -= 1

            if balance < 0:
                raise ValueError("Несогласованные скобки")

            if index < len(tokens) - 1:
                next_token = tokens[index + 1]
                self._validate_pair(current_token, next_token)

        if balance != 0:
            raise ValueError("Несогласованные скобки")

    def _validate_first_token(self, token: Token) -> None:
        if token.type == TokenType.OPERATOR and token.value in self.BINARY_OPERATORS:
            raise ValueError("Выражение не может начинаться с бинарного оператора")

        if token.type == TokenType.RPAREN:
            raise ValueError("Выражение не может начинаться с ')'")

    def _validate_last_token(self, token: Token) -> None:
        if token.type == TokenType.OPERATOR:
            raise ValueError("Выражение не может заканчиваться оператором")

        if token.type == TokenType.LPAREN:
            raise ValueError("Выражение не может заканчиваться '('")

    def _validate_pair(self, current_token: Token, next_token: Token) -> None:
        if self._is_variable(current_token):
            self._validate_after_variable(next_token)
            return

        if self._is_not_operator(current_token):
            self._validate_after_not(next_token)
            return

        if self._is_binary_operator(current_token):
            self._validate_after_binary_operator(next_token)
            return

        if current_token.type == TokenType.LPAREN:
            self._validate_after_left_parenthesis(next_token)
            return

        if current_token.type == TokenType.RPAREN:
            self._validate_after_right_parenthesis(next_token)

    def _validate_after_variable(self, token: Token) -> None:
        if token.type == TokenType.VARIABLE:
            raise ValueError("После переменной должен идти оператор или ')'")

        if token.type == TokenType.LPAREN:
            raise ValueError("После переменной не может идти '('")

        if self._is_not_operator(token):
            raise ValueError("После переменной не может идти '!'")

    def _validate_after_not(self, token: Token) -> None:
        if self._is_binary_operator(token):
            raise ValueError("После '!' должно идти выражение, а не бинарный оператор")

        if token.type == TokenType.RPAREN:
            raise ValueError("После '!' не может идти ')'")

    def _validate_after_binary_operator(self, token: Token) -> None:
        if self._is_binary_operator(token):
            raise ValueError("После бинарного оператора должно идти выражение")

        if token.type == TokenType.RPAREN:
            raise ValueError("После бинарного оператора не может идти ')'")

    def _validate_after_left_parenthesis(self, token: Token) -> None:
        if self._is_binary_operator(token):
            raise ValueError("После '(' должно идти выражение")

        if token.type == TokenType.RPAREN:
            raise ValueError("Пустые скобки недопустимы")

    def _validate_after_right_parenthesis(self, token: Token) -> None:
        if token.type == TokenType.VARIABLE:
            raise ValueError("После ')' должен идти оператор или ')'")

        if token.type == TokenType.LPAREN:
            raise ValueError("После ')' не может идти '('")

        if self._is_not_operator(token):
            raise ValueError("После ')' не может идти '!'")

    def _is_variable(self, token: Token) -> bool:
        return token.type == TokenType.VARIABLE

    def _is_binary_operator(self, token: Token) -> bool:
        return token.type == TokenType.OPERATOR and token.value in self.BINARY_OPERATORS

    def _is_not_operator(self, token: Token) -> bool:
        return token.type == TokenType.OPERATOR and token.value == "!"

    def _should_pop(self, current: Token, top: Token) -> bool:
        current_priority = self.PRIORITY[current.value]
        top_priority = self.PRIORITY[top.value]

        if current.value in self.RIGHT_ASSOCIATIVE:
            return current_priority < top_priority
        return current_priority <= top_priority