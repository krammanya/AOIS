from itertools import product
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.expression import LogicalExpression
from tables.truth_table_generator import TruthTableGenerator
from tables.truth_tables_row import TruthTableRow


def build_rows_from_truths(variable_names: list[str], truthy_sets: set[tuple[int, ...]]) -> list[TruthTableRow]:
    rows: list[TruthTableRow] = []

    for values in product([0, 1], repeat=len(variable_names)):
        variable_values = {
            name: bool(bit)
            for name, bit in zip(variable_names, values)
        }
        rows.append(
            TruthTableRow(
                variable_values=variable_values,
                intermediate_values={},
                result=values in truthy_sets,
            )
        )

    return rows


@pytest.fixture
def sample_expression() -> LogicalExpression:
    return LogicalExpression("((a&b)|(!a&c))")


@pytest.fixture
def sample_truth_table(sample_expression: LogicalExpression):
    return TruthTableGenerator().generate(sample_expression)


@pytest.fixture
def minimization_rows() -> list[TruthTableRow]:
    return build_rows_from_truths(
        ["a", "b", "c"],
        {(0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)},
    )
