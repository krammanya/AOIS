from algebra.boolean_derivative import BooleanDerivative
from core.expression import LogicalExpression
from minimization.calculation_minimizer import (
    minimize_calculation_method,
    minimize_calculation_tabular_method,
    minimize_karnaugh_method,
)
from tables.normal_form_builder import NormalFormBuilder
from tables.post_class_checker import PostClassChecker
from tables.truth_table_generator import TruthTableGenerator
from tables.zhegalkin_builder import ZhegalkinBuilder


def print_table(
    variable_names: list[str],
    intermediate_expressions: list[str],
    rows: list,
) -> None:
    headers = ["i"] + variable_names + intermediate_expressions + ["F"]
    string_rows: list[list[str]] = []

    for index, row in enumerate(rows):
        current_row: list[str] = [str(index)]

        for variable_name in variable_names:
            current_row.append(str(int(row.variable_values[variable_name])))

        for expression_text in intermediate_expressions:
            current_row.append(str(int(row.intermediate_values[expression_text])))

        current_row.append(str(int(row.result)))
        string_rows.append(current_row)

    column_widths: list[int] = []

    for column_index, header in enumerate(headers):
        max_width = len(header)

        for string_row in string_rows:
            cell_width = len(string_row[column_index])
            if cell_width > max_width:
                max_width = cell_width

        column_widths.append(max_width)

    header_parts: list[str] = []
    for index, header in enumerate(headers):
        header_parts.append(header.ljust(column_widths[index]))
    header_line = " | ".join(header_parts)

    print(header_line)
    print("-" * len(header_line))

    for string_row in string_rows:
        row_parts: list[str] = []

        for index, cell_value in enumerate(string_row):
            row_parts.append(cell_value.ljust(column_widths[index]))

        print(" | ".join(row_parts))


def print_triangle(triangle: list[list[int]]) -> None:
    print("Треугольник XOR:")

    for index, triangle_row in enumerate(triangle):
        indent = " " * index
        row_text = " ".join(str(value) for value in triangle_row)
        print(f"{indent}{row_text}")


def print_truth_table(
    variable_names: list[str],
    intermediate_expressions: list[str],
    rows: list,
) -> None:
    print()
    print("Полная таблица истинности:")
    print_table(variable_names, intermediate_expressions, rows)


def print_normal_forms(
    variable_names: list[str],
    rows: list,
    normal_form_builder: NormalFormBuilder,
) -> None:
    sdnf = normal_form_builder.build_sdnf(variable_names, rows)
    sknf = normal_form_builder.build_sknf(variable_names, rows)
    numeric_sdnf = normal_form_builder.build_numeric_sdnf(rows)
    numeric_sknf = normal_form_builder.build_numeric_sknf(rows)

    print()
    print("СДНФ:")
    print(sdnf)

    print()
    print("СКНФ:")
    print(sknf)

    print()
    print("Числовая форма СДНФ:")
    print(numeric_sdnf)

    print()
    print("Числовая форма СКНФ:")
    print(numeric_sknf)


def print_index_form(expression: LogicalExpression) -> None:
    print()
    print("Индексная форма:")
    print(f"Вектор значений: {expression.truth_vector()}")
    print(f"Индекс функции: {expression.function_index()}")
    print(f"Индексы наборов, где f = 1: {expression.minterm_indices()}")
    print(f"Индексы наборов, где f = 0: {expression.maxterm_indices()}")


def print_zhegalkin(
    variable_names: list[str],
    rows: list,
    zhegalkin_builder: ZhegalkinBuilder,
) -> None:
    triangle = zhegalkin_builder.build_triangle(rows)

    print()
    print_triangle(triangle)

    print()
    print("Коэффициенты полинома Жегалкина:")
    print(zhegalkin_builder.build_coefficient_values(variable_names, rows))

    print()
    print("Форма с коэффициентами:")
    print(zhegalkin_builder.build_coefficient_form(variable_names, rows))

    print()
    print("Полином Жегалкина:")
    print(zhegalkin_builder.build_polynomial(variable_names, rows))


def print_post_classes(
    variable_names: list[str],
    rows: list,
    post_class_checker: PostClassChecker,
) -> None:
    print()
    print(post_class_checker.build_report(variable_names, rows))


def print_fictive_variables(
    variable_names: list[str],
    rows: list,
    zhegalkin_builder: ZhegalkinBuilder,
) -> None:
    print()
    print(zhegalkin_builder.build_fictive_variables_report(variable_names, rows))


def print_derivative_menu() -> None:
    print()
    print("Булева дифференциация:")
    print("1 - Частная производная")
    print("2 - Смешанная производная")
    print("0 - Назад")


def print_menu() -> None:
    print()
    print("Выберите действие:")
    print("1 - Показать таблицу истинности")
    print("2 - Показать СДНФ, СКНФ и числовые формы")
    print("3 - Показать индексную форму")
    print("4 - Показать полином Жегалкина")
    print("5 - Определить принадлежность к классам Поста")
    print("6 - Найти фиктивные переменные")
    print("7 - Булева дифференциация")
    print("8 - Ввести новую логическую функцию")
    print("9 - Минимизировать функцию расчетным методом")
    print("10 - Минимизировать функцию расчетно-табличным методом")
    print("11 - Минимизировать функцию табличным методом (карта Карно)")
    print("0 - Выход")


def read_expression() -> LogicalExpression:
    while True:
        print()
        print("Допустимые операции: &, |, !, ->, ~")
        print("Также поддерживается свободный формат: ∧, ∨, ¬, →, ↔")
        print("Допустимые переменные: a, b, c, d, e")
        print("Пример: !(!a→!b)∨c")
        print()

        expression_text = input("Введите логическую функцию: ").strip()

        try:
            return LogicalExpression(expression_text)
        except ValueError as error:
            print()
            print(f"Ошибка: {error}")
            print("Попробуйте ввести выражение ещё раз.")


def read_derivative_variable(variable_names: list[str]) -> str:
    while True:
        variable_name = input(
            f"Введите переменную для производной ({', '.join(variable_names)}): "
        ).strip()

        if variable_name in variable_names:
            return variable_name

        print("Некорректная переменная. Попробуйте снова.")


def read_mixed_derivative_variables(variable_names: list[str]) -> list[str]:
    while True:
        raw_input_text = input(
            "Введите переменные смешанной производной через пробел "
            f"({', '.join(variable_names)}): "
        ).strip()

        if not raw_input_text:
            print("Нужно ввести хотя бы одну переменную.")
            continue

        derivative_variables = raw_input_text.split()

        is_valid = True
        for variable_name in derivative_variables:
            if variable_name not in variable_names:
                is_valid = False
                break

        if not is_valid:
            print("Обнаружена некорректная переменная. Попробуйте снова.")
            continue

        return derivative_variables


def print_derivatives(
    expression: LogicalExpression,
    variable_names: list[str],
    derivative_builder: BooleanDerivative,
) -> None:
    while True:
        print_derivative_menu()
        user_choice = input("Введите номер действия: ").strip()

        if user_choice == "1":
            variable_name = read_derivative_variable(variable_names)
            derivative_sdnf = derivative_builder.build_partial_derivative_sdnf(
                expression,
                variable_name,
            )

            print()
            print(f"Частная производная по {variable_name} в СДНФ:")
            print(derivative_sdnf)

        elif user_choice == "2":
            derivative_variables = read_mixed_derivative_variables(variable_names)
            derivative_sdnf = derivative_builder.build_mixed_derivative_sdnf(
                expression,
                derivative_variables,
            )

            print()
            print(
                "Смешанная производная по "
                + ", ".join(derivative_variables)
                + " в СДНФ:"
            )
            print(derivative_sdnf)

        elif user_choice == "0":
            return

        else:
            print("Некорректный пункт меню. Попробуйте снова.")


def print_calculation_minimization(
    variable_names: list[str],
    rows: list,
) -> None:
    _print_report(minimize_calculation_method(variable_names, rows))


def print_calculation_tabular_minimization(
    variable_names: list[str],
    rows: list,
) -> None:
    _print_report(minimize_calculation_tabular_method(variable_names, rows))


def print_karnaugh_minimization(
    variable_names: list[str],
    rows: list,
) -> None:
    _print_report(minimize_karnaugh_method(variable_names, rows))


def _print_report(report: str) -> None:
    print()
    print(report)


def handle_expression(expression: LogicalExpression) -> str:
    table_generator = TruthTableGenerator()
    normal_form_builder = NormalFormBuilder()
    zhegalkin_builder = ZhegalkinBuilder()
    post_class_checker = PostClassChecker()
    derivative_builder = BooleanDerivative()

    intermediate_expressions, rows = table_generator.generate(expression)
    variable_names = expression.variables()
    actions = {
        "1": lambda: print_truth_table(variable_names, intermediate_expressions, rows),
        "2": lambda: print_normal_forms(variable_names, rows, normal_form_builder),
        "3": lambda: print_index_form(expression),
        "4": lambda: print_zhegalkin(variable_names, rows, zhegalkin_builder),
        "5": lambda: print_post_classes(variable_names, rows, post_class_checker),
        "6": lambda: print_fictive_variables(variable_names, rows, zhegalkin_builder),
        "7": lambda: print_derivatives(expression, variable_names, derivative_builder),
        "9": lambda: print_calculation_minimization(variable_names, rows),
        "10": lambda: print_calculation_tabular_minimization(variable_names, rows),
        "11": lambda: print_karnaugh_minimization(variable_names, rows),
    }

    while True:
        print()
        print(f"Текущая функция: {expression.expression}")
        print(f"Переменные: {', '.join(variable_names)}")
        print_menu()

        user_choice = input("Введите номер действия: ").strip()

        if user_choice == "8":
            return "new_expression"

        if user_choice == "0":
            return "exit"

        action = actions.get(user_choice)
        if action is None:
            print("Некорректный пункт меню. Попробуйте снова.")
            continue

        action()


def main() -> None:
    print("Программа для работы с логическими функциями")

    while True:
        expression = read_expression()
        action = handle_expression(expression)

        if action == "exit":
            print("Программа завершена.")
            break


if __name__ == "__main__":
    main()
