from tables.truth_tables_row import TruthTableRow


class NormalFormBuilder:
    def build_sdnf(
        self,
        variable_names: list[str],
        rows: list[TruthTableRow],
    ) -> str:
        if not variable_names:
            return "1" if any(row.result for row in rows) else "0"

        terms: list[str] = []

        for row in rows:
            if not row.result:
                continue

            term_parts: list[str] = []

            for variable_name in variable_names:
                variable_value = row.variable_values[variable_name]

                if variable_value:
                    term_parts.append(variable_name)
                else:
                    term_parts.append(f"!{variable_name}")

            terms.append(f"({'&'.join(term_parts)})")

        if not terms:
            return "0"

        return "|".join(terms)

    def build_sknf(
        self,
        variable_names: list[str],
        rows: list[TruthTableRow],
    ) -> str:
        if not variable_names:
            return "0" if any(not row.result for row in rows) else "1"

        terms: list[str] = []

        for row in rows:
            if row.result:
                continue

            term_parts: list[str] = []

            for variable_name in variable_names:
                variable_value = row.variable_values[variable_name]

                if variable_value:
                    term_parts.append(f"!{variable_name}")
                else:
                    term_parts.append(variable_name)

            terms.append(f"({'|'.join(term_parts)})")

        if not terms:
            return "1"

        return "&".join(terms)

    def build_numeric_sdnf(self, rows: list[TruthTableRow]) -> str:
        indices: list[str] = []

        for index, row in enumerate(rows):
            if row.result:
                indices.append(str(index))

        if not indices:
            return "Σ()"

        return f"Σ({','.join(indices)})"

    def build_numeric_sknf(self, rows: list[TruthTableRow]) -> str:
        indices: list[str] = []

        for index, row in enumerate(rows):
            if not row.result:
                indices.append(str(index))

        if not indices:
            return "Π()"

        return f"Π({','.join(indices)})"
