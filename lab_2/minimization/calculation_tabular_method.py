from tables.truth_tables_row import TruthTableRow

from minimization.base import (
    BaseMinimizer,
    build_cover_table,
    build_initial_implicants,
    format_implicants,
    format_tuples,
)


class CalculationTabularMethodMinimizer:
    def __init__(self) -> None:
        self.minimizer = BaseMinimizer()

    def minimize_both(
        self,
        variable_names: list[str],
        rows: list[TruthTableRow],
    ) -> str:
        sdnf_result = self.minimizer.minimize(variable_names, rows, target_value=True)
        sknf_result = self.minimizer.minimize(variable_names, rows, target_value=False)

        sdnf_terms = build_initial_implicants(variable_names, rows, target_value=True)
        sknf_terms = build_initial_implicants(variable_names, rows, target_value=False)

        return (
            "МДНФ (расчетно-табличный метод)\n"
            "Стадия склеивания:\n"
            f"{format_tuples(sdnf_result.gluing_stage)}\n"
            "Таблица покрытия:\n"
            f"{build_cover_table(sdnf_result.prime_implicants, sdnf_terms, variable_names, is_sknf=False)}\n"
            "Результат:\n"
            f"{format_implicants(sdnf_result.minimized_implicants, variable_names, is_sknf=False)}\n"
            f"{format_tuples(sdnf_result.minimized_implicants)}\n\n"
            "МКНФ (расчетно-табличный метод)\n"
            "Стадия склеивания:\n"
            f"{format_tuples(sknf_result.gluing_stage)}\n"
            "Таблица покрытия:\n"
            f"{build_cover_table(sknf_result.prime_implicants, sknf_terms, variable_names, is_sknf=True)}\n"
            "Результат:\n"
            f"{format_implicants(sknf_result.minimized_implicants, variable_names, is_sknf=True)}\n"
            f"{format_tuples(sknf_result.minimized_implicants)}"
        )


def minimize_calculation_tabular_method(
    variable_names: list[str],
    rows: list[TruthTableRow],
) -> str:
    return CalculationTabularMethodMinimizer().minimize_both(variable_names, rows)