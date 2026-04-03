from core.tokens import Token, TokenType


class Evaluator:
    def evaluate_postfix(self, postfix_tokens: list[Token], values: dict[str, bool]) -> bool:
        stack: list[bool] = []

        for token in postfix_tokens:
            if token.type == TokenType.VARIABLE:
                if token.value not in values:
                    raise ValueError(f"Не задано значение переменной '{token.value}'")
                stack.append(values[token.value])

            elif token.type == TokenType.OPERATOR:
                if token.value == "!":
                    if not stack:
                        raise ValueError("Некорректное выражение")
                    operand = stack.pop()
                    stack.append(not operand)

                else:
                    if len(stack) < 2:
                        raise ValueError("Некорректное выражение")

                    right = stack.pop()
                    left = stack.pop()

                    if token.value == "&":
                        stack.append(left and right)
                    elif token.value == "|":
                        stack.append(left or right)
                    elif token.value == "->":
                        stack.append((not left) or right)
                    elif token.value == "~":
                        stack.append(left == right)
                    else:
                        raise ValueError(f"Неизвестный оператор '{token.value}'")

        if len(stack) != 1:
            raise ValueError("Некорректное выражение")

        return stack[0]