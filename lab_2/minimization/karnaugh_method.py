from tables.truth_tables_row import TruthTableRow

from minimization.base import (
    Implicant,
    format_implicants,
    format_table,
    format_tuples,
    pick_minimal_cover,
    unique_implicants,
)


def gray_codes(length: int) -> list[str]:
    if length == 0:
        return [""]
    if length == 1:
        return ["0", "1"]

    previous = gray_codes(length - 1)
    return [f"0{code}" for code in previous] + [f"1{code}" for code in reversed(previous)]


def power_sizes(length: int) -> list[int]:
    size = 1
    sizes: list[int] = []

    while size <= length:
        sizes.append(size)
        size *= 2

    return sizes


def _split_variable_counts(variable_count: int) -> tuple[int, int, int]:
    """
    Возвращает:
    - layer_count_bits: число переменных, выделенных под слой карты
    - row_count_bits: число переменных по строкам
    - col_count_bits: число переменных по столбцам

    Для 2..4 переменных слой не нужен.
    Для 5 переменных делаем 2 слоя по первой переменной и 4x4 по оставшимся.
    """
    if variable_count == 2:
        return 0, 1, 1
    if variable_count == 3:
        return 0, 1, 2
    if variable_count == 4:
        return 0, 2, 2
    if variable_count == 5:
        return 1, 2, 2

    raise ValueError("Карта Карно поддерживается только для 2-5 переменных.")


def build_karnaugh_map(
    variable_names: list[str],
    rows: list[TruthTableRow],
) -> str:
    variable_count = len(variable_names)
    layer_bits, row_bits, col_bits = _split_variable_counts(variable_count)

    layer_codes = gray_codes(layer_bits)
    row_codes = gray_codes(row_bits)
    col_codes = gray_codes(col_bits)

    layer_index = {
        tuple(int(bit) for bit in code): position
        for position, code in enumerate(layer_codes)
    }
    row_index = {
        tuple(int(bit) for bit in code): position
        for position, code in enumerate(row_codes)
    }
    col_index = {
        tuple(int(bit) for bit in code): position
        for position, code in enumerate(col_codes)
    }

    values = [
        [["0"] * len(col_codes) for _ in row_codes]
        for _ in layer_codes
    ]

    for row in rows:
        bits = tuple(int(row.variable_values[name]) for name in variable_names)

        layer_part = bits[:layer_bits]
        row_part = bits[layer_bits:layer_bits + row_bits]
        col_part = bits[layer_bits + row_bits:]

        current_layer = layer_index[layer_part]
        current_row = row_index[row_part]
        current_col = col_index[col_part]

        values[current_layer][current_row][current_col] = str(int(row.result))

    if layer_bits == 0:
        headers = [f"{''.join(variable_names[:row_bits])}\\{''.join(variable_names[row_bits:])}"]
        headers.extend(col_codes)

        table_rows: list[list[str]] = []
        for code, row_values in zip(row_codes, values[0]):
            table_rows.append([code, *row_values])

        return format_table(headers, table_rows)

    # Для 5 переменных печатаем две карты
    layer_name = "".join(variable_names[:layer_bits])
    row_names = "".join(variable_names[layer_bits:layer_bits + row_bits])
    col_names = "".join(variable_names[layer_bits + row_bits:])

    parts: list[str] = []

    for layer_position, layer_code in enumerate(layer_codes):
        headers = [f"{row_names}\\{col_names}"] + col_codes
        table_rows: list[list[str]] = []

        for code, row_values in zip(row_codes, values[layer_position]):
            table_rows.append([code, *row_values])

        parts.append(f"{layer_name}={layer_code}")
        parts.append(format_table(headers, table_rows))

    return "\n\n".join(parts)


def covers_to_pattern(
    variable_names: list[str],
    rows: list[TruthTableRow],
    covers: tuple[int, ...],
) -> tuple[int | None, ...]:
    patterns = [
        tuple(int(rows[index].variable_values[name]) for name in variable_names)
        for index in covers
    ]

    merged: list[int | None] = []

    for position in range(len(variable_names)):
        bits = {pattern[position] for pattern in patterns}
        merged.append(bits.pop() if len(bits) == 1 else None)

    return tuple(merged)


def build_karnaugh_implicants(
    variable_names: list[str],
    rows: list[TruthTableRow],
    target_value: bool,
) -> list[Implicant]:
    variable_count = len(variable_names)
    layer_bits, row_bits, col_bits = _split_variable_counts(variable_count)

    layer_codes = gray_codes(layer_bits)
    row_codes = gray_codes(row_bits)
    col_codes = gray_codes(col_bits)

    layer_total = len(layer_codes)
    row_total = len(row_codes)
    col_total = len(col_codes)

    layer_index = {
        tuple(int(bit) for bit in code): position
        for position, code in enumerate(layer_codes)
    }
    row_index = {
        tuple(int(bit) for bit in code): position
        for position, code in enumerate(row_codes)
    }
    col_index = {
        tuple(int(bit) for bit in code): position
        for position, code in enumerate(col_codes)
    }

    values = [
        [[False] * col_total for _ in range(row_total)]
        for _ in range(layer_total)
    ]
    index_grid = [
        [[-1] * col_total for _ in range(row_total)]
        for _ in range(layer_total)
    ]

    for index, row in enumerate(rows):
        bits = tuple(int(row.variable_values[name]) for name in variable_names)

        layer_part = bits[:layer_bits]
        row_part = bits[layer_bits:layer_bits + row_bits]
        col_part = bits[layer_bits + row_bits:]

        current_layer = layer_index[layer_part]
        current_row = row_index[row_part]
        current_col = col_index[col_part]

        values[current_layer][current_row][current_col] = row.result == target_value
        index_grid[current_layer][current_row][current_col] = index

    groups: list[Implicant] = []

    for layer_size in power_sizes(layer_total):
        for row_size in power_sizes(row_total):
            for col_size in power_sizes(col_total):
                for start_layer in range(layer_total):
                    for start_row in range(row_total):
                        for start_col in range(col_total):
                            covers: set[int] = set()
                            is_valid = True

                            for layer_offset in range(layer_size):
                                for row_offset in range(row_size):
                                    for col_offset in range(col_size):
                                        current_layer = (start_layer + layer_offset) % layer_total
                                        current_row = (start_row + row_offset) % row_total
                                        current_col = (start_col + col_offset) % col_total

                                        if not values[current_layer][current_row][current_col]:
                                            is_valid = False
                                            break

                                        covers.add(index_grid[current_layer][current_row][current_col])

                                    if not is_valid:
                                        break
                                if not is_valid:
                                    break

                            if not is_valid or not covers:
                                continue

                            pattern = covers_to_pattern(
                                variable_names,
                                rows,
                                tuple(sorted(covers)),
                            )
                            groups.append(
                                Implicant(
                                    pattern=pattern,
                                    covers=tuple(sorted(covers)),
                                )
                            )

    unique_groups = unique_implicants(groups)

    return [
        implicant
        for implicant in unique_groups
        if not any(
            set(implicant.covers) < set(other.covers)
            for other in unique_groups
            if implicant != other
        )
    ]


class KarnaughMethodMinimizer:
    def minimize_both(
        self,
        variable_names: list[str],
        rows: list[TruthTableRow],
    ) -> str:
        if not 2 <= len(variable_names) <= 5:
            return "Карта Карно поддерживается только для 2-5 переменных."

        map_view = build_karnaugh_map(variable_names, rows)

        sdnf_implicants = build_karnaugh_implicants(
            variable_names,
            rows,
            target_value=True,
        )
        sknf_implicants = build_karnaugh_implicants(
            variable_names,
            rows,
            target_value=False,
        )

        sdnf_result = pick_minimal_cover(sdnf_implicants)
        sknf_result = pick_minimal_cover(sknf_implicants)

        return (
            "Карта Карно:\n"
            f"{map_view}\n\n"
            "МДНФ (табличный метод)\n"
            "Результат:\n"
            f"{format_implicants(sdnf_result, variable_names, is_sknf=False)}\n"
            f"{format_tuples(sdnf_result)}\n\n"
            "МКНФ (табличный метод)\n"
            "Результат:\n"
            f"{format_implicants(sknf_result, variable_names, is_sknf=True)}\n"
            f"{format_tuples(sknf_result)}"
        )


def minimize_karnaugh_method(
    variable_names: list[str],
    rows: list[TruthTableRow],
) -> str:
    return KarnaughMethodMinimizer().minimize_both(variable_names, rows)