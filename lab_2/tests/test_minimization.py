from minimization import (
    minimize_calculation_method,
    minimize_calculation_tabular_method,
    minimize_karnaugh_method,
)


def test_calculation_method_builds_both_reports(minimization_rows):
    report = minimize_calculation_method(["a", "b", "c"], minimization_rows)

    assert "МДНФ (расчетный метод)" in report
    assert "МКНФ (расчетный метод)" in report
    assert "Стадия склеивания:" in report
    assert "Результат:" in report

    assert "(X,1,1)" in report
    assert "(1,X,X)" in report

    assert "(b&c)|(a)" in report or "(a)|(b&c)" in report
    assert "(a|b)&(a|c)" in report or "(a|c)&(a|b)" in report


def test_calculation_tabular_method_builds_both_reports(minimization_rows):
    report = minimize_calculation_tabular_method(["a", "b", "c"], minimization_rows)

    assert "МДНФ (расчетно-табличный метод)" in report
    assert "МКНФ (расчетно-табличный метод)" in report
    assert "Стадия склеивания:" in report
    assert "Таблица покрытия:" in report
    assert "Импликанта" in report

    assert "(b&c)|(a)" in report or "(a)|(b&c)" in report
    assert "(a|b)&(a|c)" in report or "(a|c)&(a|b)" in report


def test_calculation_method_handles_all_zero_function():
    rows = [
        type(
            "Row",
            (),
            {
                "variable_values": {"a": False},
                "intermediate_values": {},
                "result": False,
            },
        )(),
        type(
            "Row",
            (),
            {
                "variable_values": {"a": True},
                "intermediate_values": {},
                "result": False,
            },
        )(),
    ]

    report = minimize_calculation_method(["a"], rows)

    assert "МДНФ (расчетный метод)" in report
    assert "Результат:\n0\n-" in report
    assert "МКНФ (расчетный метод)" in report
    assert "(0,X)" not in report


def test_calculation_method_handles_all_one_function():
    rows = [
        type(
            "Row",
            (),
            {
                "variable_values": {"a": False},
                "intermediate_values": {},
                "result": True,
            },
        )(),
        type(
            "Row",
            (),
            {
                "variable_values": {"a": True},
                "intermediate_values": {},
                "result": True,
            },
        )(),
    ]

    report = minimize_calculation_method(["a"], rows)

    assert "МДНФ (расчетный метод)" in report
    assert "Результат:\n(1)\n(X)" in report or "Результат:\n1\n(X)" in report
    assert "МКНФ (расчетный метод)" in report
    assert "Результат:\n1\n-" in report


def test_karnaugh_method_builds_map_and_both_results(minimization_rows):
    report = minimize_karnaugh_method(["a", "b", "c"], minimization_rows)

    assert "Карта Карно:" in report
    assert "a\\bc | 00 | 01 | 11 | 10" in report

    assert "МДНФ (табличный метод)" in report
    assert "МКНФ (табличный метод)" in report

    assert "(1,X,X)" in report
    assert "(X,1,1)" in report or "(0,X,0)" in report


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
                        for shift, name in enumerate(
                            reversed(["a", "b", "c", "d", "e"])
                        )
                    },
                    "intermediate_values": {},
                    "result": False,
                },
            )()
        )

    assert minimize_karnaugh_method(["a", "b", "c", "d", "e"], rows) == (
        "Карта Карно поддерживается только для 2-4 переменных."
    )


def test_new_example_a_or_not_b_and_c():
    rows = [
        type(
            "Row",
            (),
            {
                "variable_values": {"a": False, "b": False, "c": False},
                "intermediate_values": {},
                "result": False,
            },
        )(),
        type(
            "Row",
            (),
            {
                "variable_values": {"a": False, "b": False, "c": True},
                "intermediate_values": {},
                "result": True,
            },
        )(),
        type(
            "Row",
            (),
            {
                "variable_values": {"a": False, "b": True, "c": False},
                "intermediate_values": {},
                "result": False,
            },
        )(),
        type(
            "Row",
            (),
            {
                "variable_values": {"a": False, "b": True, "c": True},
                "intermediate_values": {},
                "result": False,
            },
        )(),
        type(
            "Row",
            (),
            {
                "variable_values": {"a": True, "b": False, "c": False},
                "intermediate_values": {},
                "result": True,
            },
        )(),
        type(
            "Row",
            (),
            {
                "variable_values": {"a": True, "b": False, "c": True},
                "intermediate_values": {},
                "result": True,
            },
        )(),
        type(
            "Row",
            (),
            {
                "variable_values": {"a": True, "b": True, "c": False},
                "intermediate_values": {},
                "result": True,
            },
        )(),
        type(
            "Row",
            (),
            {
                "variable_values": {"a": True, "b": True, "c": True},
                "intermediate_values": {},
                "result": True,
            },
        )(),
    ]

    calc_report = minimize_calculation_method(["a", "b", "c"], rows)
    tabular_report = minimize_calculation_tabular_method(["a", "b", "c"], rows)
    karnaugh_report = minimize_karnaugh_method(["a", "b", "c"], rows)

    expected_mdnf_variants = {
        "(a)|(!b&c)",
        "(!b&c)|(a)",
    }
    expected_mknf_variants = {
        "(a|c)&(a|!b)",
        "(a|!b)&(a|c)",
    }

    assert any(variant in calc_report for variant in expected_mdnf_variants)
    assert any(variant in calc_report for variant in expected_mknf_variants)

    assert any(variant in tabular_report for variant in expected_mdnf_variants)
    assert any(variant in tabular_report for variant in expected_mknf_variants)

    assert any(variant in karnaugh_report for variant in expected_mdnf_variants)
    assert any(variant in karnaugh_report for variant in expected_mknf_variants)