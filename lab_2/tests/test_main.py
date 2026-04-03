import builtins

import main
from algebra.boolean_derivative import BooleanDerivative
from core.expression import LogicalExpression
from tables.normal_form_builder import NormalFormBuilder
from tables.post_class_checker import PostClassChecker
from tables.truth_table_generator import TruthTableGenerator
from tables.zhegalkin_builder import ZhegalkinBuilder


def test_main_print_helpers_emit_expected_text(sample_expression, sample_truth_table, capsys):
    intermediate_expressions, rows = sample_truth_table
    variable_names = sample_expression.variables()

    main.print_truth_table(variable_names, intermediate_expressions, rows)
    main.print_normal_forms(variable_names, rows, NormalFormBuilder())
    main.print_index_form(sample_expression)
    main.print_zhegalkin(variable_names, rows, ZhegalkinBuilder())
    main.print_post_classes(variable_names, rows, PostClassChecker())
    main.print_fictive_variables(variable_names, rows, ZhegalkinBuilder())
    main.print_calculation_minimization(variable_names, rows)
    main.print_calculation_tabular_minimization(variable_names, rows)
    main.print_karnaugh_minimization(variable_names, rows)

    output = capsys.readouterr().out
    assert "Полная таблица истинности" in output
    assert "СДНФ:" in output
    assert "Индексная форма:" in output
    assert "Полином Жегалкина:" in output
    assert "Принадлежность к классам Поста:" in output
    assert "Фиктивные переменные:" in output
    assert "Карта Карно:" in output


def test_read_expression_retries_until_valid(monkeypatch, capsys):
    answers = iter(["a?", "a"])
    monkeypatch.setattr(builtins, "input", lambda _: next(answers))

    expression = main.read_expression()

    assert isinstance(expression, LogicalExpression)
    assert expression.expression == "a"
    assert "Ошибка:" in capsys.readouterr().out


def test_read_derivative_variable_retries(monkeypatch, capsys):
    answers = iter(["x", "a"])
    monkeypatch.setattr(builtins, "input", lambda _: next(answers))

    assert main.read_derivative_variable(["a", "b"]) == "a"
    assert "Некорректная переменная" in capsys.readouterr().out


def test_read_mixed_derivative_variables_retries(monkeypatch, capsys):
    answers = iter(["", "x", "a b"])
    monkeypatch.setattr(builtins, "input", lambda _: next(answers))

    assert main.read_mixed_derivative_variables(["a", "b"]) == ["a", "b"]
    output = capsys.readouterr().out
    assert "Нужно ввести хотя бы одну переменную." in output
    assert "Обнаружена некорректная переменная." in output


def test_print_derivatives_handles_invalid_and_both_modes(monkeypatch, capsys):
    answers = iter(["3", "1", "a", "2", "a b", "0"])
    monkeypatch.setattr(builtins, "input", lambda _: next(answers))

    main.print_derivatives(LogicalExpression("(a&b)"), ["a", "b"], BooleanDerivative())

    output = capsys.readouterr().out
    assert "Некорректный пункт меню" in output
    assert "Частная производная по a" in output
    assert "Смешанная производная по a, b" in output


def test_handle_expression_routes_actions(monkeypatch, capsys):
    calls = []

    monkeypatch.setattr(main, "print_truth_table", lambda *args: calls.append("1"))
    monkeypatch.setattr(main, "print_calculation_minimization", lambda *args: calls.append("9"))
    monkeypatch.setattr(main, "print_menu", lambda: None)

    answers = iter(["1", "9", "oops", "8"])
    monkeypatch.setattr(builtins, "input", lambda _: next(answers))

    result = main.handle_expression(LogicalExpression("a"))

    assert result == "new_expression"
    assert calls == ["1", "9"]
    assert "Некорректный пункт меню" in capsys.readouterr().out


def test_handle_expression_exit(monkeypatch):
    monkeypatch.setattr(main, "print_menu", lambda: None)
    monkeypatch.setattr(builtins, "input", lambda _: "0")

    assert main.handle_expression(LogicalExpression("a")) == "exit"


def test_main_loops_until_exit(monkeypatch, capsys):
    expressions = iter([LogicalExpression("a"), LogicalExpression("b")])
    actions = iter(["new_expression", "exit"])

    monkeypatch.setattr(main, "read_expression", lambda: next(expressions))
    monkeypatch.setattr(main, "handle_expression", lambda expression: next(actions))

    main.main()

    output = capsys.readouterr().out
    assert "Программа для работы с логическими функциями" in output
    assert "Программа завершена." in output
