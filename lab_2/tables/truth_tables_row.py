from dataclasses import dataclass


@dataclass
class TruthTableRow:
    variable_values: dict[str, bool]
    intermediate_values: dict[str, bool]
    result: bool