from tables.truth_tables_row import TruthTableRow
from tables.zhegalkin_builder import ZhegalkinBuilder


class PostClassChecker:
    def __init__(self) -> None:
        self.zhegalkin_builder = ZhegalkinBuilder()

    def check_t0(self, rows: list[TruthTableRow]) -> bool:
        if not rows:
            return False
        return not rows[0].result

    def check_t1(self, rows: list[TruthTableRow]) -> bool:
        if not rows:
            return False
        return rows[-1].result

    def check_s(self, rows: list[TruthTableRow]) -> bool:
        rows_count = len(rows)

        for index in range(rows_count):
            opposite_index = rows_count - 1 - index

            if rows[index].result == rows[opposite_index].result:
                return False

        return True

    def check_m(self, variable_names: list[str], rows: list[TruthTableRow]) -> bool:
        row_values = [row.variable_values for row in rows]
        row_results = [row.result for row in rows]

        for i in range(len(rows)):
            for j in range(len(rows)):
                if self._is_less_or_equal(row_values[i], row_values[j], variable_names):
                    if row_results[i] and not row_results[j]:
                        return False

        return True

    def check_l(self, rows: list[TruthTableRow]) -> bool:
        coefficients = self.zhegalkin_builder.build_coefficients(rows)

        for index, coefficient in enumerate(coefficients):
            if coefficient == 0:
                continue

            if self._bit_count(index) > 1:
                return False

        return True

    def check_all(
        self,
        variable_names: list[str],
        rows: list[TruthTableRow],
    ) -> dict[str, bool]:
        return {
            "T0": self.check_t0(rows),
            "T1": self.check_t1(rows),
            "S": self.check_s(rows),
            "M": self.check_m(variable_names, rows),
            "L": self.check_l(rows),
        }

    def build_report(
        self,
        variable_names: list[str],
        rows: list[TruthTableRow],
    ) -> str:
        results = self.check_all(variable_names, rows)

        belonging = [name for name, value in results.items() if value]
        not_belonging = [name for name, value in results.items() if not value]

        lines: list[str] = []

        lines.append("Принадлежность к классам Поста:")
        for class_name, value in results.items():
            lines.append(f"{class_name}: {'Да' if value else 'Нет'}")

        lines.append("")
        lines.append(
            "Функция принадлежит классам: "
            + (", ".join(belonging) if belonging else "не принадлежит ни одному")
        )
        lines.append(
            "Функция не принадлежит классам: "
            + (", ".join(not_belonging) if not_belonging else "нет таких")
        )

        return "\n".join(lines)

    def _is_less_or_equal(
        self,
        left_values: dict[str, bool],
        right_values: dict[str, bool],
        variable_names: list[str],
    ) -> bool:
        for variable_name in variable_names:
            if left_values[variable_name] and not right_values[variable_name]:
                return False

        return True

    def _bit_count(self, number: int) -> int:
        return bin(number).count("1")