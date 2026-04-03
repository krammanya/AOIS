from minimization.calculation_minimizer import (
    CalculationMinimizer,
    minimize_calculation_method,
    minimize_calculation_tabular_method,
    minimize_karnaugh_method,
)


def test_calculation_minimizer_builds_expected_reports(minimization_rows):
    minimizer = CalculationMinimizer()
    result = minimizer.minimize_sdnf(["a", "b", "c"], minimization_rows)

    assert result.gluing_as_tuples() == "(X,1,1) (1,0,X) (1,X,0) (1,X,1) (1,1,X)"
    assert result.result_as_expression(["a", "b", "c"]) in {
        "(bc)1 ∨ (a)2",
        "(a)1 ∨ (bc)2",
    }
    assert result.result_as_tuples() in {
        "(X,1,1) (1,X,X)",
        "(1,X,X) (X,1,1)",
    }

    report = minimize_calculation_method(["a", "b", "c"], minimization_rows)
    assert "Стадия склеивания" in report
    assert "Результат" in report

    tabular = minimize_calculation_tabular_method(["a", "b", "c"], minimization_rows)
    assert "Таблица покрытия" in tabular
    assert "Импликанта | 3 | 4 | 5 | 6 | 7" in tabular


def test_calculation_minimizer_handles_all_zero_function():
    rows = [
        type("Row", (), {"variable_values": {"a": False}, "intermediate_values": {}, "result": False})(),
        type("Row", (), {"variable_values": {"a": True}, "intermediate_values": {}, "result": False})(),
    ]

    report = minimize_calculation_method(["a"], rows)
    assert report.endswith("0\n-")


def test_karnaugh_method_builds_map_and_result(minimization_rows):
    report = minimize_karnaugh_method(["a", "b", "c"], minimization_rows)

    assert "Карта Карно:" in report
    assert "a\\bc | 00 | 01 | 11 | 10" in report
    assert "Результат:" in report
    assert "(1,X,X)" in report


def test_karnaugh_method_rejects_unsupported_variable_count():
    rows = []
    for number in range(32):
        rows.append(
            type(
                "Row",
                (),
                {
                    "variable_values": {
                        name: bool((number >> shift) & 1)
                        for shift, name in enumerate(reversed(["a", "b", "c", "d", "e"]))
                    },
                    "intermediate_values": {},
                    "result": False,
                },
            )()
        )

    assert minimize_karnaugh_method(["a", "b", "c", "d", "e"], rows) == (
        "Карта Карно поддерживается для 2-4 переменных."
    )
