from dataclasses import dataclass
from itertools import combinations

from tables.truth_tables_row import TruthTableRow

Pattern = tuple[int | None, ...]


@dataclass(frozen=True)
class Implicant:
    pattern: Pattern
    covers: tuple[int, ...]


@dataclass(frozen=True)
class MinimizationResult:
    gluing_stage: list[Implicant]
    prime_implicants: list[Implicant]
    minimized_implicants: list[Implicant]

    def gluing_as_expression(self, variable_names: list[str]) -> str:
        return _format_implicants(self.gluing_stage, variable_names, empty_value="0")

    def gluing_as_tuples(self) -> str:
        return " ".join(_pattern_to_tuple(item.pattern) for item in self.gluing_stage) or "-"

    def result_as_tuples(self) -> str:
        return " ".join(_pattern_to_tuple(item.pattern) for item in self.minimized_implicants) or "-"

    def result_as_expression(self, variable_names: list[str]) -> str:
        return _format_implicants(self.minimized_implicants, variable_names, empty_value="0")


class CalculationMinimizer:
    def minimize_sdnf(
        self,
        variable_names: list[str],
        rows: list[TruthTableRow],
    ) -> MinimizationResult:
        current = _build_initial_implicants(variable_names, rows, target_value=True)
        gluing_stage: list[Implicant] = self._glue_round(current)[0]

        prime_implicants: list[Implicant] = []
        while current:
            next_round, unused = self._glue_round(current)
            prime_implicants.extend(unused)
            current = next_round

        minimized = self._pick_minimal_cover(prime_implicants)
        return MinimizationResult(gluing_stage, prime_implicants, minimized)

    def build_report(
        self,
        variable_names: list[str],
        rows: list[TruthTableRow],
    ) -> str:
        result = self.minimize_sdnf(variable_names, rows)
        return (
            "Стадия склеивания:\n"
            f"{result.gluing_as_tuples()}\n"
            "Результат:\n"
            f"{result.result_as_expression(variable_names)}\n"
            f"{result.result_as_tuples()}"
        )

    def build_tabular_report(
        self,
        variable_names: list[str],
        rows: list[TruthTableRow],
    ) -> str:
        result = self.minimize_sdnf(variable_names, rows)
        minterms = _build_initial_implicants(variable_names, rows, target_value=True)
        labels = _build_implicant_labels(result.prime_implicants, variable_names)

        return (
            "Стадия склеивания:\n"
            f"{result.gluing_as_tuples()}\n"
            "Таблица покрытия:\n"
            f"{_build_cover_table(result.prime_implicants, minterms, labels)}\n"
            "Результат:\n"
            f"{_format_implicants(result.minimized_implicants, labels, empty_value='0')}\n"
            f"{_format_tuples(result.minimized_implicants)}"
        )

    def _glue_round(self, implicants: list[Implicant]) -> tuple[list[Implicant], list[Implicant]]:
        glued: list[Implicant] = []
        used: set[Implicant] = set()

        for left, right in combinations(implicants, 2):
            merged_pattern = _merge_patterns(left.pattern, right.pattern)
            if merged_pattern is None:
                continue

            glued.append(
                Implicant(
                    merged_pattern,
                    tuple(sorted(set(left.covers + right.covers))),
                )
            )
            used.add(left)
            used.add(right)

        return _unique_implicants(glued), [item for item in implicants if item not in used]

    def _pick_minimal_cover(self, prime_implicants: list[Implicant]) -> list[Implicant]:
        if not prime_implicants:
            return []

        required = set().union(*(item.covers for item in prime_implicants))
        best_cover: tuple[Implicant, ...] | None = None

        for size in range(1, len(prime_implicants) + 1):
            for subset in combinations(prime_implicants, size):
                covered = set().union(*(item.covers for item in subset))
                if covered != required:
                    continue

                if best_cover is None or _cover_score(subset) < _cover_score(best_cover):
                    best_cover = subset

            if best_cover is not None:
                return list(best_cover)

        return prime_implicants


def _merge_patterns(left: Pattern, right: Pattern) -> Pattern | None:
    differences = 0
    merged: list[int | None] = []

    for left_bit, right_bit in zip(left, right):
        if left_bit == right_bit:
            merged.append(left_bit)
            continue

        if left_bit is None or right_bit is None:
            return None

        differences += 1
        merged.append(None)

        if differences > 1:
            return None

    return tuple(merged) if differences == 1 else None


def _unique_implicants(items: list[Implicant]) -> list[Implicant]:
    unique: list[Implicant] = []
    seen: set[Pattern] = set()

    for item in items:
        if item.pattern in seen:
            continue

        unique.append(item)
        seen.add(item.pattern)

    return unique


def _cover_score(items: tuple[Implicant, ...]) -> tuple[int, int, tuple[Pattern, ...]]:
    literal_count = sum(sum(bit is not None for bit in item.pattern) for item in items)
    patterns = tuple(item.pattern for item in items)
    return len(items), literal_count, patterns


def _pattern_to_term(pattern: Pattern, variable_names: list[str]) -> str:
    parts = []

    for name, bit in zip(variable_names, pattern):
        if bit is None:
            continue
        parts.append(name if bit == 1 else f"\u00ac{name}")

    return "".join(parts) or "1"


def _pattern_to_tuple(pattern: Pattern) -> str:
    values = ("X" if bit is None else str(bit) for bit in pattern)
    return f"({','.join(values)})"


def _format_implicants(
    implicants: list[Implicant],
    labels: dict[Implicant, str] | list[str],
    empty_value: str,
) -> str:
    if not implicants:
        return empty_value

    if isinstance(labels, dict):
        parts = [labels[item] for item in implicants]
    else:
        parts = [
            f"({_pattern_to_term(item.pattern, labels)}){index}"
            for index, item in enumerate(implicants, start=1)
        ]

    return " \u2228 ".join(parts)


def _format_tuples(implicants: list[Implicant]) -> str:
    return " ".join(_pattern_to_tuple(item.pattern) for item in implicants) or "-"


def _build_initial_implicants(
    variable_names: list[str],
    rows: list[TruthTableRow],
    target_value: bool,
) -> list[Implicant]:
    implicants: list[Implicant] = []

    for index, row in enumerate(rows):
        if row.result != target_value:
            continue

        pattern = tuple(int(row.variable_values[name]) for name in variable_names)
        implicants.append(Implicant(pattern, (index,)))

    return implicants


def _build_cover_table(
    prime_implicants: list[Implicant],
    minterms: list[Implicant],
    labels: dict[Implicant, str],
) -> str:
    if not prime_implicants:
        return "-"

    headers = ["Импликанта"] + [str(item.covers[0]) for item in minterms]
    rows: list[list[str]] = []

    for implicant in prime_implicants:
        row = [labels[implicant]]

        for minterm in minterms:
            row.append("X" if minterm.covers[0] in implicant.covers else "")

        rows.append(row)

    return _format_table(headers, rows)


def _build_implicant_labels(
    implicants: list[Implicant],
    variable_names: list[str],
) -> dict[Implicant, str]:
    return {
        implicant: f"({_pattern_to_term(implicant.pattern, variable_names)}){index}"
        for index, implicant in enumerate(implicants, start=1)
    }


def minimize_calculation_method(
    variable_names: list[str],
    rows: list[TruthTableRow],
) -> str:
    return CalculationMinimizer().build_report(variable_names, rows)


def minimize_calculation_tabular_method(
    variable_names: list[str],
    rows: list[TruthTableRow],
) -> str:
    return CalculationMinimizer().build_tabular_report(variable_names, rows)


def minimize_karnaugh_method(
    variable_names: list[str],
    rows: list[TruthTableRow],
) -> str:
    if not 2 <= len(variable_names) <= 4:
        return "Карта Карно поддерживается для 2-4 переменных."

    implicants = _build_karnaugh_implicants(variable_names, rows)
    minimized = CalculationMinimizer()._pick_minimal_cover(implicants)
    return (
        "Карта Карно:\n"
        f"{_build_karnaugh_map(variable_names, rows)}\n"
        "Результат:\n"
        f"{_format_implicants(minimized, variable_names, empty_value='0')}\n"
        f"{_format_tuples(minimized)}"
    )


def _build_karnaugh_map(
    variable_names: list[str],
    rows: list[TruthTableRow],
) -> str:
    row_count = len(variable_names) // 2
    col_count = len(variable_names) - row_count
    row_codes = _gray_codes(row_count)
    col_codes = _gray_codes(col_count)
    headers = [f"{''.join(variable_names[:row_count])}\\{''.join(variable_names[row_count:])}"]
    headers.extend(col_codes)
    table_rows: list[list[str]] = []

    row_index = {
        tuple(int(bit) for bit in code): position
        for position, code in enumerate(row_codes)
    }
    col_index = {
        tuple(int(bit) for bit in code): position
        for position, code in enumerate(col_codes)
    }
    values = [["0"] * len(col_codes) for _ in row_codes]

    for row in rows:
        bits = tuple(int(row.variable_values[name]) for name in variable_names)
        left_bits = bits[:row_count]
        right_bits = bits[row_count:]
        values[row_index[left_bits]][col_index[right_bits]] = str(int(row.result))

    for label, row_values in zip(row_codes, values):
        table_rows.append([label, *row_values])

    return _format_table(headers, table_rows)


def _build_karnaugh_implicants(
    variable_names: list[str],
    rows: list[TruthTableRow],
) -> list[Implicant]:
    row_count = len(variable_names) // 2
    col_count = len(variable_names) - row_count
    row_codes = _gray_codes(row_count)
    col_codes = _gray_codes(col_count)
    row_total = len(row_codes)
    col_total = len(col_codes)
    row_index = {
        tuple(int(bit) for bit in code): position
        for position, code in enumerate(row_codes)
    }
    col_index = {
        tuple(int(bit) for bit in code): position
        for position, code in enumerate(col_codes)
    }
    values = [[False] * col_total for _ in range(row_total)]
    index_grid = [[-1] * col_total for _ in range(row_total)]

    for index, row in enumerate(rows):
        bits = tuple(int(row.variable_values[name]) for name in variable_names)
        row_bits = bits[:row_count]
        col_bits = bits[row_count:]
        current_row = row_index[row_bits]
        current_col = col_index[col_bits]
        values[current_row][current_col] = row.result
        index_grid[current_row][current_col] = index

    groups: list[Implicant] = []
    for row_size in _power_sizes(row_total):
        for col_size in _power_sizes(col_total):
            for start_row in range(row_total):
                for start_col in range(col_total):
                    covers: set[int] = set()
                    is_valid = True

                    for row_offset in range(row_size):
                        for col_offset in range(col_size):
                            current_row = (start_row + row_offset) % row_total
                            current_col = (start_col + col_offset) % col_total

                            if not values[current_row][current_col]:
                                is_valid = False
                                break

                            covers.add(index_grid[current_row][current_col])

                        if not is_valid:
                            break

                    if not is_valid or not covers:
                        continue

                    pattern = _covers_to_pattern(variable_names, rows, tuple(sorted(covers)))
                    if pattern is None:
                        continue

                    groups.append(Implicant(pattern, tuple(sorted(covers))))

    unique_groups = _unique_implicants(groups)
    return [
        implicant
        for implicant in unique_groups
        if not any(
            set(implicant.covers) < set(other.covers)
            for other in unique_groups
            if implicant != other
        )
    ]


def _gray_codes(length: int) -> list[str]:
    if length == 0:
        return [""]
    if length == 1:
        return ["0", "1"]

    previous = _gray_codes(length - 1)
    return [f"0{code}" for code in previous] + [f"1{code}" for code in reversed(previous)]


def _power_sizes(length: int) -> list[int]:
    size = 1
    sizes: list[int] = []

    while size <= length:
        sizes.append(size)
        size *= 2

    return sizes


def _covers_to_pattern(
    variable_names: list[str],
    rows: list[TruthTableRow],
    covers: tuple[int, ...],
) -> Pattern | None:
    patterns = [
        tuple(int(rows[index].variable_values[name]) for name in variable_names)
        for index in covers
    ]
    merged: list[int | None] = []

    for position in range(len(variable_names)):
        bits = {pattern[position] for pattern in patterns}
        merged.append(bits.pop() if len(bits) == 1 else None)

    return tuple(merged)


def _format_table(headers: list[str], rows: list[list[str]]) -> str:
    widths = [len(header) for header in headers]

    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    lines = [" | ".join(header.ljust(widths[i]) for i, header in enumerate(headers))]
    lines.append("-" * len(lines[0]))

    for row in rows:
        lines.append(" | ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))

    return "\n".join(lines)
