from src.utils.word32 import Word32
from src.floating_point.binary32_number import (
    Binary32Number,
    FRACTION_BITS_COUNT,
    MIN_NORMAL_UNBIASED_EXPONENT,
    MIN_SUBNORMAL_UNBIASED_EXPONENT,
)
from src.floating_point.binary32_rounding import Binary32Rounding


SPECIAL_NAN_TEXT: str = "nan"
SPECIAL_INFINITY_TEXT: str = "inf"
DECIMAL_PRECISION_DIGITS: int = 12


class Binary32Codec:
    def __init__(self) -> None:
        self._rounding = Binary32Rounding()

    def decode(self, word: Word32) -> Binary32Number:
        return Binary32Number(word)

    def encode(self, number: Binary32Number) -> Word32:
        return number.word

    def from_decimal_string(self, value: str) -> Word32:
        normalized_value = value.strip().lower()

        if normalized_value == SPECIAL_NAN_TEXT:
            return self.encode(Binary32Number.quiet_nan())

        if normalized_value in (SPECIAL_INFINITY_TEXT, f"+{SPECIAL_INFINITY_TEXT}"):
            return self.encode(Binary32Number.infinity_with_sign(0))

        if normalized_value == f"-{SPECIAL_INFINITY_TEXT}":
            return self.encode(Binary32Number.infinity_with_sign(1))

        sign, numerator, denominator = self._parse_decimal_rational(normalized_value)
        number = self._rounding.round_fraction(sign, numerator, denominator)
        return self.encode(number)

    def to_decimal_string(self, word: Word32) -> str:
        number = self.decode(word)

        if number.is_nan:
            return SPECIAL_NAN_TEXT

        if number.is_infinity:
            return self._signed_text(number.sign, SPECIAL_INFINITY_TEXT)

        numerator, denominator = self.to_rational(number)
        sign = number.sign if numerator == 0 else 1 if numerator < 0 else 0
        absolute_numerator = abs(numerator)

        return self._format_decimal(sign, absolute_numerator, denominator)

    def to_rational(self, number: Binary32Number) -> tuple[int, int]:
        if number.is_nan or number.is_infinity:
            raise ValueError("NaN and infinity cannot be converted to a rational value")

        if number.is_zero:
            return 0, 1

        significand = number.significand_value

        if number.is_normal:
            shift = number.unbiased_exponent - FRACTION_BITS_COUNT
        else:
            shift = MIN_SUBNORMAL_UNBIASED_EXPONENT

        numerator, denominator = self._scaled_fraction(significand, shift)

        if number.sign == 1:
            numerator = -numerator

        return numerator, denominator

    def _parse_decimal_rational(self, value: str) -> tuple[int, int, int]:
        sign = self._extract_sign(value)
        unsigned_value = value[1:] if value[:1] in ("+", "-") else value
        mantissa_text, exponent_value = self._split_decimal_exponent(unsigned_value)
        integer_part, fraction_part = self._split_decimal_point(mantissa_text)

        digits_text = integer_part + fraction_part
        digits_value = int(digits_text) if digits_text else 0
        decimal_scale = len(fraction_part) - exponent_value

        if decimal_scale >= 0:
            return sign, digits_value, 10 ** decimal_scale

        return sign, digits_value * (10 ** (-decimal_scale)), 1

    def _extract_sign(self, value: str) -> int:
        if value.startswith("-"):
            return 1
        return 0

    def _split_decimal_exponent(self, value: str) -> tuple[str, int]:
        if "e" not in value:
            return value, 0

        mantissa_text, exponent_text = value.split("e", 1)
        return mantissa_text, int(exponent_text)

    def _split_decimal_point(self, value: str) -> tuple[str, str]:
        if "." not in value:
            return value, ""

        return tuple(value.split(".", 1))

    def _scaled_fraction(self, significand: int, shift: int) -> tuple[int, int]:
        if shift >= 0:
            return significand << shift, 1

        return significand, 1 << (-shift)

    def _format_decimal(
        self,
        sign: int,
        numerator: int,
        denominator: int,
    ) -> str:
        integer_part = numerator // denominator
        remainder = numerator % denominator
        prefix = "-" if sign == 1 and numerator != 0 else ""

        if remainder == 0:
            return f"{prefix}{integer_part}"

        fraction_text = self._fraction_to_decimal(remainder, denominator)
        return f"{prefix}{integer_part}.{fraction_text}"

    def _fraction_to_decimal(self, remainder: int, denominator: int) -> str:
        digits: list[str] = []
        current_remainder = remainder

        for _ in range(DECIMAL_PRECISION_DIGITS):
            current_remainder *= 10
            digit = current_remainder // denominator
            current_remainder %= denominator
            digits.append(str(digit))

            if current_remainder == 0:
                break

        return self._trim_trailing_zeros("".join(digits))

    def _trim_trailing_zeros(self, digits_text: str) -> str:
        trimmed_text = digits_text.rstrip("0")

        if trimmed_text == "":
            return "0"

        return trimmed_text

    def _signed_text(self, sign: int, base_text: str) -> str:
        if sign == 1:
            return f"-{base_text}"
        return base_text
