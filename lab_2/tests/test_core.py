import pytest

from core.evaluator import Evaluator
from core.expression import LogicalExpression
from core.lexer import Lexer
from core.parser import Parser
from core.tokens import Token, TokenType


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("!(!a→!b)∨c", ["!", "(", "!", "a", "->", "!", "b", ")", "|", "c"]),
        (" ¬ a ∧ b \u200b", ["!", "a", "&", "b"]),
    ],
)
def test_lexer_supports_free_format(source, expected):
    tokens = Lexer().tokenize(source)
    assert [token.value for token in tokens] == expected


def test_lexer_rejects_unknown_symbol():
    with pytest.raises(ValueError, match="Недопустимый символ"):
        Lexer().tokenize("a?")


@pytest.mark.parametrize(
    ("expression", "message"),
    [
        ("", "Пустое выражение"),
        ("&a", "начинаться с бинарного оператора"),
        ("a|", "заканчиваться оператором"),
        ("a(", "заканчиваться '('"),
        ("ab", "После переменной должен идти оператор"),
        ("a!", "заканчиваться оператором"),
        ("!|a", "После '!' должно идти выражение"),
        ("!)", "После '!' не может идти ')'"),
        ("a||b", "После бинарного оператора должно идти выражение"),
        ("a|)", "После бинарного оператора не может идти ')'"),
        ("()", "Пустые скобки недопустимы"),
        ("(|a)", "После '(' должно идти выражение"),
        ("(a)b", "После ')' должен идти оператор"),
        ("(a)(", "заканчиваться '('"),
        ("(a)!", "заканчиваться оператором"),
        ("(a", "Несогласованные скобки"),
        ("a)", "Несогласованные скобки"),
    ],
)
def test_parser_validation_errors(expression, message):
    lexer = Lexer()
    parser = Parser()

    with pytest.raises(ValueError) as error:
        parser.to_postfix(lexer.tokenize(expression))
    assert message in str(error.value)


def test_parser_builds_expected_postfix_for_operator_priority():
    postfix = Parser().to_postfix(Lexer().tokenize("a|b&!c"))
    assert [token.value for token in postfix] == ["a", "b", "c", "!", "&", "|"]


def test_evaluator_handles_all_supported_operators():
    expression = LogicalExpression("((a&b)|((a->c)~(!b)))")
    result = expression.evaluate({"a": True, "b": False, "c": True})
    assert result is True


def test_evaluator_requires_variable_value():
    postfix = [Token(TokenType.VARIABLE, "a")]
    with pytest.raises(ValueError, match="Не задано значение переменной 'a'"):
        Evaluator().evaluate_postfix(postfix, {})


def test_evaluator_rejects_invalid_postfix_shapes():
    with pytest.raises(ValueError, match="Некорректное выражение"):
        Evaluator().evaluate_postfix([Token(TokenType.OPERATOR, "!")], {})

    with pytest.raises(ValueError, match="Некорректное выражение"):
        Evaluator().evaluate_postfix(
            [Token(TokenType.VARIABLE, "a"), Token(TokenType.VARIABLE, "a")],
            {"a": True},
        )


def test_evaluator_rejects_unknown_operator():
    postfix = [
        Token(TokenType.VARIABLE, "a"),
        Token(TokenType.VARIABLE, "b"),
        Token(TokenType.OPERATOR, "^"),
    ]
    with pytest.raises(ValueError, match="Неизвестный оператор"):
        Evaluator().evaluate_postfix(postfix, {"a": True, "b": False})


def test_logical_expression_builds_truth_vector_and_indices():
    expression = LogicalExpression("a->b")

    assert expression.variables() == ["a", "b"]
    assert expression.truth_vector() == "1101"
    assert expression.function_index() == 13
    assert expression.minterm_indices() == [0, 1, 3]
    assert expression.maxterm_indices() == [2]
