from itertools import product

from core.evaluator import Evaluator
from core.lexer import Lexer
from core.parser import Parser
from core.tokens import TokenType


class LogicalExpression:
    def __init__(self, expression: str):
        self.expression = expression
        self.lexer = Lexer()
        self.parser = Parser()
        self.evaluator = Evaluator()

        self.tokens = self.lexer.tokenize(expression)
        self.postfix_tokens = self.parser.to_postfix(self.tokens)

    def variables(self) -> list[str]:
        vars_set = {
            token.value
            for token in self.tokens
            if token.type == TokenType.VARIABLE
        }
        return sorted(vars_set)

    def evaluate(self, values: dict[str, bool]) -> bool:
        return self.evaluator.evaluate_postfix(self.postfix_tokens, values)

    def truth_table_rows(self) -> list[tuple[int, dict[str, bool], bool]]:
        variables = self.variables()
        rows = []

        for index, combination in enumerate(product([False, True], repeat=len(variables))):
            values = dict(zip(variables, combination))
            result = self.evaluate(values)
            rows.append((index, values, result))

        return rows

    def truth_vector(self) -> str:
        return "".join("1" if result else "0" for _, _, result in self.truth_table_rows())

    def function_index(self) -> int:
        return int(self.truth_vector(), 2)

    def minterm_indices(self) -> list[int]:
        return [index for index, _, result in self.truth_table_rows() if result]

    def maxterm_indices(self) -> list[int]:
        return [index for index, _, result in self.truth_table_rows() if not result]
