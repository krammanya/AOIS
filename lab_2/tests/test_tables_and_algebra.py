from algebra.boolean_derivative import BooleanDerivative
from core.expression import LogicalExpression
from tables.normal_form_builder import NormalFormBuilder
from tables.post_class_checker import PostClassChecker
from tables.truth_table_generator import TruthTableGenerator
from tables.truth_tables_row import TruthTableRow
from tables.zhegalkin_builder import ZhegalkinBuilder


def test_truth_table_generator_builds_rows_and_intermediate_values(sample_expression, sample_truth_table):
    intermediate_expressions, rows = sample_truth_table

    assert intermediate_expressions == ["(a&b)", "(!a)", "((!a)&c)"]
    assert len(rows) == 8
    assert rows[0].result is False
    assert rows[-1].result is True
    assert rows[1].intermediate_values["(!a)"] is True


def test_truth_table_generator_handles_expression_without_operators():
    expression = LogicalExpression("a")
    intermediate_expressions, rows = TruthTableGenerator().generate(expression)

    assert intermediate_expressions == []
    assert [row.result for row in rows] == [False, True]


def test_truth_table_generator_rejects_unknown_operator():
    generator = TruthTableGenerator()
    try:
        generator._apply_binary_operator("^", True, False)
    except ValueError as error:
        assert "Неизвестный оператор" in str(error)
    else:
        raise AssertionError("Expected ValueError for unsupported operator")


def test_normal_form_builder_builds_all_forms(sample_truth_table):
    _, rows = sample_truth_table
    builder = NormalFormBuilder()

    assert builder.build_sdnf(["a", "b", "c"], rows) == "(!a&!b&c)|(!a&b&c)|(a&b&!c)|(a&b&c)"
    assert builder.build_sknf(["a", "b", "c"], rows) == "(a|b|c)&(a|!b|c)&(!a|b|c)&(!a|b|!c)"
    assert builder.build_numeric_sdnf(rows) == "Σ(1,3,6,7)"
    assert builder.build_numeric_sknf(rows) == "Π(0,2,4,5)"


def test_normal_form_builder_handles_constant_results():
    builder = NormalFormBuilder()
    false_rows = [TruthTableRow({"a": False}, {}, False), TruthTableRow({"a": True}, {}, False)]
    true_rows = [TruthTableRow({"a": False}, {}, True), TruthTableRow({"a": True}, {}, True)]

    assert builder.build_sdnf(["a"], false_rows) == "0"
    assert builder.build_sknf(["a"], true_rows) == "1"
    assert builder.build_numeric_sdnf(false_rows) == "Σ()"
    assert builder.build_numeric_sknf(true_rows) == "Π()"


def test_zhegalkin_builder_builds_polynomial_and_reports(sample_truth_table):
    _, rows = sample_truth_table
    builder = ZhegalkinBuilder()

    assert builder.build_truth_vector(rows) == [0, 1, 0, 1, 0, 0, 1, 1]
    assert builder.build_triangle([]) == []
    assert builder.build_coefficients(rows) == [0, 1, 0, 0, 0, 1, 1, 0]
    assert builder.build_polynomial(["a", "b", "c"], rows) == "c⊕ac⊕ab"
    assert "a000 = 0" in builder.build_coefficient_values(["a", "b", "c"], rows)
    assert builder.build_coefficient_form(["a", "b"], [TruthTableRow({"a": False, "b": False}, {}, False)]) == "f = a00 ⊕ a01·b ⊕ a10·a ⊕ a11·ab"
    fictive, essential = builder.find_fictive_variables(["a", "b", "c"], rows)
    assert fictive == []
    assert essential == ["a", "b", "c"]
    report = builder.build_fictive_variables_report(["a", "b", "c"], rows)
    assert "Существенные переменные" in report


def test_post_class_checker_reports_membership(sample_truth_table):
    _, rows = sample_truth_table
    checker = PostClassChecker()

    assert checker.check_t0([]) is False
    assert checker.check_t1([]) is False
    assert checker.check_t0(rows) is True
    assert checker.check_t1(rows) is True
    assert checker.check_s(rows) is False
    assert checker.check_m(["a", "b", "c"], rows) is False
    assert checker.check_l(rows) is False
    all_checks = checker.check_all(["a", "b", "c"], rows)
    assert all_checks == {"T0": True, "T1": True, "S": False, "M": False, "L": False}
    report = checker.build_report(["a", "b", "c"], rows)
    assert "T0: Да" in report and "L: Нет" in report


def test_post_class_checker_positive_cases():
    expression = LogicalExpression("a")
    _, rows = TruthTableGenerator().generate(expression)
    checker = PostClassChecker()

    assert checker.check_s(rows) is True
    assert checker.check_m(["a"], rows) is True
    assert checker.check_l(rows) is True


def test_boolean_derivative_builds_partial_and_mixed_sdnf():
    derivative = BooleanDerivative()
    expression = LogicalExpression("(a&b)")

    assert derivative.build_partial_derivative_sdnf(expression, "a") == "(b)"
    assert derivative.build_mixed_derivative_sdnf(expression, ["a", "b"]) == "1"


def test_boolean_derivative_validation_and_constant_rows():
    derivative = BooleanDerivative()
    expression = LogicalExpression("a")

    try:
        derivative.build_mixed_derivative_sdnf(expression, [])
    except ValueError as error:
        assert "Не заданы переменные дифференцирования" in str(error)
    else:
        raise AssertionError("Expected validation error for empty derivative variables")

    try:
        derivative.build_partial_derivative_sdnf(expression, "b")
    except ValueError as error:
        assert "отсутствует в выражении" in str(error)
    else:
        raise AssertionError("Expected validation error for unknown variable")

    assert derivative.build_partial_derivative_sdnf(expression, "a") == "1"
