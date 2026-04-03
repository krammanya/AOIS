from core.expression import LogicalExpression
from core.tokens import Token, TokenType
from tables.truth_tables_row import TruthTableRow


class TruthTableGenerator:
    def generate(self, expression: LogicalExpression) -> tuple[list[str], list[TruthTableRow]]:
        variable_names = expression.variables()
        all_intermediate_expressions = self._build_intermediate_expressions(
            expression.postfix_tokens
        )
        intermediate_expressions = all_intermediate_expressions[:-1]

        rows: list[TruthTableRow] = []
        value_sets = self._generate_value_sets(variable_names)

        for variable_values in value_sets:
            row = self._build_row(
                expression.postfix_tokens,
                variable_values,
                intermediate_expressions,
            )
            rows.append(row)

        return intermediate_expressions, rows

    def _generate_value_sets(self, variable_names: list[str]) -> list[dict[str, bool]]:
        if not variable_names:
            return [{}]

        value_sets: list[dict[str, bool]] = []
        rows_count = 2 ** len(variable_names)

        for number in range(rows_count):
            variable_values: dict[str, bool] = {}

            for index, variable_name in enumerate(variable_names):
                bit_index = len(variable_names) - index - 1
                bit_value = (number >> bit_index) & 1
                variable_values[variable_name] = bool(bit_value)

            value_sets.append(variable_values)

        return value_sets

    def _build_intermediate_expressions(self, postfix_tokens: list[Token]) -> list[str]:
        expression_stack: list[str] = []
        intermediate_expressions: list[str] = []

        for token in postfix_tokens:
            if token.type == TokenType.VARIABLE:
                expression_stack.append(token.value)
                continue

            if token.type != TokenType.OPERATOR:
                continue

            if token.value == "!":
                operand_expression = expression_stack.pop()
                current_expression = f"(!{operand_expression})"
                expression_stack.append(current_expression)
                intermediate_expressions.append(current_expression)
                continue

            right_expression = expression_stack.pop()
            left_expression = expression_stack.pop()
            current_expression = f"({left_expression}{token.value}{right_expression})"

            expression_stack.append(current_expression)
            intermediate_expressions.append(current_expression)

        return intermediate_expressions

    def _build_row(
        self,
        postfix_tokens: list[Token],
        variable_values: dict[str, bool],
        intermediate_expressions: list[str],
    ) -> TruthTableRow:
        value_stack: list[bool] = []
        expression_stack: list[str] = []
        intermediate_values: dict[str, bool] = {}

        for token in postfix_tokens:
            if token.type == TokenType.VARIABLE:
                variable_value = variable_values[token.value]
                value_stack.append(variable_value)
                expression_stack.append(token.value)
                continue

            if token.value == "!":
                operand_value = value_stack.pop()
                operand_expression = expression_stack.pop()

                current_value = not operand_value
                current_expression = f"(!{operand_expression})"

                value_stack.append(current_value)
                expression_stack.append(current_expression)
                intermediate_values[current_expression] = current_value
                continue

            right_value = value_stack.pop()
            left_value = value_stack.pop()

            right_expression = expression_stack.pop()
            left_expression = expression_stack.pop()

            current_value = self._apply_binary_operator(
                token.value,
                left_value,
                right_value,
            )
            current_expression = f"({left_expression}{token.value}{right_expression})"

            value_stack.append(current_value)
            expression_stack.append(current_expression)
            intermediate_values[current_expression] = current_value

        result = value_stack[0]

        ordered_intermediate_values: dict[str, bool] = {}
        for intermediate_expression in intermediate_expressions:
            ordered_intermediate_values[intermediate_expression] = (
                intermediate_values[intermediate_expression]
            )

        return TruthTableRow(
            variable_values=variable_values,
            intermediate_values=ordered_intermediate_values,
            result=result,
        )

    def _apply_binary_operator(
        self,
        operator: str,
        left_value: bool,
        right_value: bool,
    ) -> bool:
        if operator == "&":
            return left_value and right_value

        if operator == "|":
            return left_value or right_value

        if operator == "->":
            return (not left_value) or right_value

        if operator == "~":
            return left_value == right_value

        raise ValueError(f"Неизвестный оператор '{operator}'")