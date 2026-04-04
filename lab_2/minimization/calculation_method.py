from tables.truth_tables_row import TruthTableRow

from minimization.base import (
    BaseMinimizer,
    format_implicants,
    format_tuples,
)


class CalculationMethodMinimizer:
    def __init__(self) -> None:
        self.minimizer = BaseMinimizer()

    def minimize_both(
        self,
        variable_names: list[str],
        rows: list[TruthTableRow],
    ) -> str:
        sdnf_result = self.minimizer.minimize(variable_names, rows, target_value=True)
        sknf_result = self.minimizer.minimize(variable_names, rows, target_value=False)

        return (
            "МДНФ (расчетный метод)\n"
            "Стадия склеивания:\n"
            f"{format_tuples(sdnf_result.gluing_stage)}\n"
            "Результат:\n"
            f"{format_implicants(sdnf_result.minimized_implicants, variable_names, is_sknf=False)}\n"
            f"{format_tuples(sdnf_result.minimized_implicants)}\n\n"
            "МКНФ (расчетный метод)\n"
            "Стадия склеивания:\n"
            f"{format_tuples(sknf_result.gluing_stage)}\n"
            "Результат:\n"
            f"{format_implicants(sknf_result.minimized_implicants, variable_names, is_sknf=True)}\n"
            f"{format_tuples(sknf_result.minimized_implicants)}"
        )


def minimize_calculation_method(
    variable_names: list[str],
    rows: list[TruthTableRow],
) -> str:
    return CalculationMethodMinimizer().minimize_both(variable_names, rows)