from itertools import product

from core.expression import LogicalExpression
from tables.normal_form_builder import NormalFormBuilder
from tables.truth_tables_row import TruthTableRow


class BooleanDerivative:
    def __init__(self) -> None:
        self.normal_form_builder = NormalFormBuilder()

    def build_partial_derivative_sdnf(
        self,
        expression: LogicalExpression,
        variable_name: str,
    ) -> str:
        return self.build_mixed_derivative_sdnf(expression, [variable_name])

    def build_mixed_derivative_sdnf(
        self,
        expression: LogicalExpression,
        derivative_variables: list[str],
    ) -> str:
        all_variables = expression.variables()

        self._validate_derivative_variables(all_variables, derivative_variables)

        remaining_variables = [
            variable_name
            for variable_name in all_variables
            if variable_name not in derivative_variables
        ]

        derivative_function = self._build_derivative_function(
            expression,
            derivative_variables,
        )

        rows = self._build_rows(
            remaining_variables,
            derivative_function,
        )

        return self.normal_form_builder.build_sdnf(remaining_variables, rows)

    def _validate_derivative_variables(
        self,
        all_variables: list[str],
        derivative_variables: list[str],
    ) -> None:
        if not derivative_variables:
            raise ValueError("Не заданы переменные дифференцирования")

        for variable_name in derivative_variables:
            if variable_name not in all_variables:
                raise ValueError(
                    f"Переменная '{variable_name}' отсутствует в выражении"
                )

    def _build_derivative_function(
        self,
        expression: LogicalExpression,
        derivative_variables: list[str],
    ):
        def current_function(values: dict[str, bool]) -> bool:
            return expression.evaluate(values)

        for derivative_variable in derivative_variables:
            previous_function = current_function

            def next_function(
                values: dict[str, bool],
                variable_name: str = derivative_variable,
                function=previous_function,
            ) -> bool:
                values_with_zero = dict(values)
                values_with_one = dict(values)

                values_with_zero[variable_name] = False
                values_with_one[variable_name] = True

                left_result = function(values_with_zero)
                right_result = function(values_with_one)

                return left_result ^ right_result

            current_function = next_function

        return current_function

    def _build_rows(
        self,
        variable_names: list[str],
        derivative_function,
    ) -> list[TruthTableRow]:
        rows: list[TruthTableRow] = []

        if not variable_names:
            result = derivative_function({})
            rows.append(
                TruthTableRow(
                    variable_values={},
                    intermediate_values={},
                    result=result,
                )
            )
            return rows

        for combination in product([False, True], repeat=len(variable_names)):
            variable_values = dict(zip(variable_names, combination))
            result = derivative_function(variable_values)

            rows.append(
                TruthTableRow(
                    variable_values=variable_values,
                    intermediate_values={},
                    result=result,
                )
            )

        return rows