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


def build_initial_implicants(
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


def merge_patterns(left: Pattern, right: Pattern) -> Pattern | None:
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

    if differences != 1:
        return None

    return tuple(merged)


def unique_implicants(items: list[Implicant]) -> list[Implicant]:
    result: list[Implicant] = []
    seen: set[Pattern] = set()

    for item in items:
        if item.pattern in seen:
            continue

        result.append(item)
        seen.add(item.pattern)

    return result


def glue_round(implicants: list[Implicant]) -> tuple[list[Implicant], list[Implicant]]:
    glued: list[Implicant] = []
    used: set[Implicant] = set()

    for left, right in combinations(implicants, 2):
        merged_pattern = merge_patterns(left.pattern, right.pattern)
        if merged_pattern is None:
            continue

        glued.append(
            Implicant(
                pattern=merged_pattern,
                covers=tuple(sorted(set(left.covers + right.covers))),
            )
        )
        used.add(left)
        used.add(right)

    glued = unique_implicants(glued)
    unused = [item for item in implicants if item not in used]
    return glued, unused


def cover_score(items: tuple[Implicant, ...]) -> tuple[int, int, tuple[Pattern, ...]]:
    literal_count = sum(sum(bit is not None for bit in item.pattern) for item in items)
    patterns = tuple(item.pattern for item in items)
    return len(items), literal_count, patterns


def pick_minimal_cover(prime_implicants: list[Implicant]) -> list[Implicant]:
    if not prime_implicants:
        return []

    required = set().union(*(item.covers for item in prime_implicants))
    best_cover: tuple[Implicant, ...] | None = None

    for size in range(1, len(prime_implicants) + 1):
        for subset in combinations(prime_implicants, size):
            covered = set().union(*(item.covers for item in subset))
            if covered != required:
                continue

            if best_cover is None or cover_score(subset) < cover_score(best_cover):
                best_cover = subset

        if best_cover is not None:
            return list(best_cover)

    return prime_implicants


def pattern_to_tuple(pattern: Pattern) -> str:
    values = ("X" if bit is None else str(bit) for bit in pattern)
    return f"({','.join(values)})"


def format_tuples(implicants: list[Implicant]) -> str:
    return " ".join(pattern_to_tuple(item.pattern) for item in implicants) or "-"


def pattern_to_expression(
    pattern: Pattern,
    variable_names: list[str],
    is_sknf: bool,
) -> str:
    parts: list[str] = []

    for name, bit in zip(variable_names, pattern):
        if bit is None:
            continue

        if is_sknf:
            parts.append(f"!{name}" if bit == 1 else name)
        else:
            parts.append(name if bit == 1 else f"!{name}")

    if not parts:
        return "0" if is_sknf else "1"

    separator = "|" if is_sknf else "&"
    return separator.join(parts)


def format_implicants(
    implicants: list[Implicant],
    variable_names: list[str],
    is_sknf: bool,
) -> str:
    if not implicants:
        return "1" if is_sknf else "0"

    parts = [f"({pattern_to_expression(item.pattern, variable_names, is_sknf)})" for item in implicants]
    return "&".join(parts) if is_sknf else "|".join(parts)


def format_table(headers: list[str], rows: list[list[str]]) -> str:
    widths = [len(header) for header in headers]

    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    lines = [" | ".join(header.ljust(widths[i]) for i, header in enumerate(headers))]
    lines.append("-" * len(lines[0]))

    for row in rows:
        lines.append(" | ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))

    return "\n".join(lines)


def build_cover_table(
    prime_implicants: list[Implicant],
    initial_terms: list[Implicant],
    variable_names: list[str],
    is_sknf: bool,
) -> str:
    if not prime_implicants:
        return "-"

    headers = ["Импликанта"] + [str(item.covers[0]) for item in initial_terms]
    table_rows: list[list[str]] = []

    for implicant in prime_implicants:
        row = [f"({pattern_to_expression(implicant.pattern, variable_names, is_sknf)})"]

        for term in initial_terms:
            row.append("X" if term.covers[0] in implicant.covers else "")

        table_rows.append(row)

    return format_table(headers, table_rows)


class BaseMinimizer:
    def minimize(
        self,
        variable_names: list[str],
        rows: list[TruthTableRow],
        target_value: bool,
    ) -> MinimizationResult:
        current = build_initial_implicants(variable_names, rows, target_value)
        first_glued, _ = glue_round(current)
        gluing_stage = first_glued

        prime_implicants: list[Implicant] = []

        while current:
            next_round, unused = glue_round(current)
            prime_implicants.extend(unused)
            current = next_round

        prime_implicants = unique_implicants(prime_implicants)
        minimized = pick_minimal_cover(prime_implicants)

        return MinimizationResult(
            gluing_stage=gluing_stage,
            prime_implicants=prime_implicants,
            minimized_implicants=minimized,
        )