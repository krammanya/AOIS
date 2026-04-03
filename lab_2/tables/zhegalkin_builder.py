from tables.truth_tables_row import TruthTableRow


class ZhegalkinBuilder:
    def build_truth_vector(self, rows: list[TruthTableRow]) -> list[int]:
        return [int(row.result) for row in rows]

    def build_triangle(self, rows: list[TruthTableRow]) -> list[list[int]]:
        truth_vector = self.build_truth_vector(rows)

        if not truth_vector:
            return []

        triangle: list[list[int]] = [truth_vector]

        current_row = truth_vector
        while len(current_row) > 1:
            next_row: list[int] = []

            for index in range(len(current_row) - 1):
                next_value = current_row[index] ^ current_row[index + 1]
                next_row.append(next_value)

            triangle.append(next_row)
            current_row = next_row

        return triangle

    def build_coefficients(self, rows: list[TruthTableRow]) -> list[int]:
        triangle = self.build_triangle(rows)
        return [row[0] for row in triangle]

    def build_polynomial(
        self,
        variable_names: list[str],
        rows: list[TruthTableRow],
    ) -> str:
        coefficients = self.build_coefficients(rows)
        terms: list[str] = []

        for index, coefficient in enumerate(coefficients):
            if coefficient == 0:
                continue

            monomial = self._build_monomial(variable_names, index)
            terms.append(monomial)

        if not terms:
            return "0"

        return "⊕".join(terms)

    def build_coefficient_values(
        self,
        variable_names: list[str],
        rows: list[TruthTableRow],
    ) -> str:
        coefficients = self.build_coefficients(rows)
        parts: list[str] = []

        for index, coefficient in enumerate(coefficients):
            binary_index = format(index, f"0{len(variable_names)}b")
            parts.append(f"a{binary_index} = {coefficient}")

        return "\n".join(parts)

    def build_coefficient_form(
        self,
        variable_names: list[str],
        rows: list[TruthTableRow],
    ) -> str:
        parts: list[str] = []

        for index in range(2 ** len(variable_names)):
            binary_index = format(index, f"0{len(variable_names)}b")
            monomial = self._build_monomial(variable_names, index)

            if monomial == "1":
                parts.append(f"a{binary_index}")
            else:
                parts.append(f"a{binary_index}·{monomial}")

        if not parts:
            return "f = 0"

        return "f = " + " ⊕ ".join(parts)

    def find_fictive_variables(
        self,
        variable_names: list[str],
        rows: list[TruthTableRow],
    ) -> tuple[list[str], list[str]]:
        coefficients = self.build_coefficients(rows)
        fictive_variables: list[str] = []
        essential_variables: list[str] = []

        for variable_index, variable_name in enumerate(variable_names):
            variable_found = False

            for coefficient_index, coefficient in enumerate(coefficients):
                if coefficient == 0:
                    continue

                binary_index = format(coefficient_index, f"0{len(variable_names)}b")
                if binary_index[variable_index] == "1":
                    variable_found = True
                    break

            if variable_found:
                essential_variables.append(variable_name)
            else:
                fictive_variables.append(variable_name)

        return fictive_variables, essential_variables

    def build_fictive_variables_report(
        self,
        variable_names: list[str],
        rows: list[TruthTableRow],
    ) -> str:
        fictive_variables, essential_variables = self.find_fictive_variables(
            variable_names,
            rows,
        )
        return (
            "Фиктивные переменные:\n"
            f"{', '.join(fictive_variables) if fictive_variables else 'Фиктивных переменных нет'}\n\n"
            "Существенные переменные:\n"
            f"{', '.join(essential_variables) if essential_variables else 'Существенных переменных нет'}"
        )

    def _build_monomial(self, variable_names: list[str], index: int) -> str:
        if index == 0:
            return "1"

        binary_index = format(index, f"0{len(variable_names)}b")
        monomial_parts: list[str] = []

        for bit, variable_name in zip(binary_index, variable_names):
            if bit == "1":
                monomial_parts.append(variable_name)

        return "".join(monomial_parts)
