from __future__ import annotations

from dataclasses import dataclass

from src.bcd.bcd2421_constants import BITS_PER_DIGIT


@dataclass(frozen=True)
class Bcd2421Number:
    bits: list[int]

    def __post_init__(self) -> None:
        self._validate_bits(self.bits)

    @property
    def tetrads(self) -> list[list[int]]:
        return [
            self.bits[index:index + BITS_PER_DIGIT]
            for index in range(0, len(self.bits), BITS_PER_DIGIT)
        ]

    def to_string(self) -> str:
        return "".join(str(bit) for bit in self.bits)

    @staticmethod
    def _validate_bits(bits: list[int]) -> None:
        if len(bits) == 0:
            raise ValueError("BCD 2421 number must contain at least one tetrad")

        if len(bits) % BITS_PER_DIGIT != 0:
            raise ValueError("BCD 2421 number length must be divisible by 4")

        if any(bit not in (0, 1) for bit in bits):
            raise ValueError("BCD 2421 bits must be only 0 or 1")
