from __future__ import annotations

from dataclasses import dataclass

from src.utils.word32 import Word32


BINARY32_WORD_SIZE: int = 32
SIGN_BITS_COUNT: int = 1
EXPONENT_BITS_COUNT: int = 8
FRACTION_BITS_COUNT: int = 23

EXPONENT_BIAS: int = 127
MAX_EXPONENT_VALUE: int = 255
MIN_NORMAL_UNBIASED_EXPONENT: int = -126
MIN_SUBNORMAL_UNBIASED_EXPONENT: int = -149
HIDDEN_BIT_VALUE: int = 1 << FRACTION_BITS_COUNT
QUIET_NAN_FRACTION: int = 1 << (FRACTION_BITS_COUNT - 1)


def bits_to_int(bits: list[int]) -> int:
    result = 0

    for bit in bits:
        result = (result << 1) | bit

    return result


def int_to_bits(value: int, size: int) -> list[int]:
    bits = [0] * size
    current_value = value

    for index in range(size - 1, -1, -1):
        bits[index] = current_value & 1
        current_value >>= 1

    if current_value != 0:
        raise ValueError("Value does not fit in the specified bit size")

    return bits


def build_word(sign: int, exponent_value: int, fraction_value: int) -> Word32:
    sign_bits = [sign]
    exponent_bits = int_to_bits(exponent_value, EXPONENT_BITS_COUNT)
    fraction_bits = int_to_bits(fraction_value, FRACTION_BITS_COUNT)
    return Word32(sign_bits + exponent_bits + fraction_bits)


@dataclass(frozen=True)
class Binary32Number:
    word: Word32

    @property
    def bits(self) -> list[int]:
        return self.word.bits

    @property
    def sign(self) -> int:
        return self.bits[0]

    @property
    def exponent_bits(self) -> list[int]:
        start_index = SIGN_BITS_COUNT
        end_index = start_index + EXPONENT_BITS_COUNT
        return self.bits[start_index:end_index]

    @property
    def fraction_bits(self) -> list[int]:
        start_index = SIGN_BITS_COUNT + EXPONENT_BITS_COUNT
        return self.bits[start_index:]

    @property
    def exponent_value(self) -> int:
        return bits_to_int(self.exponent_bits)

    @property
    def fraction_value(self) -> int:
        return bits_to_int(self.fraction_bits)

    @property
    def is_zero(self) -> bool:
        return self.exponent_value == 0 and self.fraction_value == 0

    @property
    def is_subnormal(self) -> bool:
        return self.exponent_value == 0 and self.fraction_value != 0

    @property
    def is_normal(self) -> bool:
        return 0 < self.exponent_value < MAX_EXPONENT_VALUE

    @property
    def is_infinity(self) -> bool:
        return self.exponent_value == MAX_EXPONENT_VALUE and self.fraction_value == 0

    @property
    def is_nan(self) -> bool:
        return self.exponent_value == MAX_EXPONENT_VALUE and self.fraction_value != 0

    @property
    def significand_value(self) -> int:
        if self.is_normal:
            return HIDDEN_BIT_VALUE | self.fraction_value
        return self.fraction_value

    @property
    def unbiased_exponent(self) -> int:
        if self.is_normal:
            return self.exponent_value - EXPONENT_BIAS
        if self.is_subnormal or self.is_zero:
            return MIN_NORMAL_UNBIASED_EXPONENT
        raise ValueError("NaN and infinity do not have an unbiased exponent")

    def negate(self) -> "Binary32Number":
        return self.from_components(
            1 - self.sign,
            self.exponent_value,
            self.fraction_value,
        )

    @classmethod
    def from_components(
        cls,
        sign: int,
        exponent_value: int,
        fraction_value: int,
    ) -> "Binary32Number":
        cls._validate_sign(sign)
        cls._validate_exponent_value(exponent_value)
        cls._validate_fraction_value(fraction_value)
        return cls(build_word(sign, exponent_value, fraction_value))

    @classmethod
    def zero_with_sign(cls, sign: int) -> "Binary32Number":
        return cls.from_components(sign, 0, 0)

    @classmethod
    def infinity_with_sign(cls, sign: int) -> "Binary32Number":
        return cls.from_components(sign, MAX_EXPONENT_VALUE, 0)

    @classmethod
    def quiet_nan(cls) -> "Binary32Number":
        return cls.from_components(0, MAX_EXPONENT_VALUE, QUIET_NAN_FRACTION)

    @staticmethod
    def _validate_sign(sign: int) -> None:
        if sign not in (0, 1):
            raise ValueError("Binary32 sign must be 0 or 1")

    @staticmethod
    def _validate_exponent_value(exponent_value: int) -> None:
        if exponent_value < 0 or exponent_value > MAX_EXPONENT_VALUE:
            raise ValueError("Binary32 exponent must be in range 0..255")

    @staticmethod
    def _validate_fraction_value(fraction_value: int) -> None:
        max_fraction = (1 << FRACTION_BITS_COUNT) - 1

        if fraction_value < 0 or fraction_value > max_fraction:
            raise ValueError("Binary32 fraction must be in range 0..8388607")
