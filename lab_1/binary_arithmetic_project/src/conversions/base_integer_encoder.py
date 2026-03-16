from abc import ABC
from typing import List

from src.config import (
    MAGNITUDE_BITS,
    MAX_MAGNITUDE,
    MAX_TWOS_COMPLEMENT,
    MIN_TWOS_COMPLEMENT,
    WORD_SIZE_BITS,
)
from src.conversions.unsigned_binary_converter import UnsignedBinaryConverter


class BaseIntegerEncoder(ABC):
    def _get_sign_bit(self, value: int) -> int:
        return 1 if value < 0 else 0

    def _get_magnitude_bits(self, value: int) -> List[int]:
        return UnsignedBinaryConverter.to_bits(abs(value), MAGNITUDE_BITS)

    def _get_absolute_value_bits_32(self, value: int) -> List[int]:
        return UnsignedBinaryConverter.to_bits(abs(value), WORD_SIZE_BITS)

    def _validate_direct_code_range(self, value: int) -> None:
        if abs(value) > MAX_MAGNITUDE:
            raise ValueError(
                "Value is out of range for direct code representation"
            )

    def _validate_ones_complement_range(self, value: int) -> None:
        if abs(value) > MAX_MAGNITUDE:
            raise ValueError(
                "Value is out of range for ones complement representation"
            )

    def _validate_twos_complement_range(self, value: int) -> None:
        if value < MIN_TWOS_COMPLEMENT or value > MAX_TWOS_COMPLEMENT:
            raise ValueError(
                "Value is out of range for twos complement representation"
            )