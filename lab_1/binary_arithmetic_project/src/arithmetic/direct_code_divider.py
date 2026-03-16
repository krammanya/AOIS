from src.conversions.direct_code_encoder import DirectCodeEncoder
from src.utils.word32 import Word32


# Внутренняя двоичная точность для корректного decimal-вывода
FRACTIONAL_PRECISION_BITS: int = 24

# Количество знаков после запятой в десятичном результате
DECIMAL_RESULT_PRECISION: int = 5


class DirectCodeDivider:
    def __init__(self) -> None:
        self._encoder = DirectCodeEncoder()

    def divide(self, dividend: int, divisor: int) -> tuple[Word32, str, str]:
        if divisor == 0:
            raise ValueError("Division by zero is not allowed")

        result_sign = self._get_result_sign(dividend, divisor)
        dividend_magnitude = abs(dividend)
        divisor_magnitude = abs(divisor)

        integer_part, remainder = self._divide_integer_part_binary(
            dividend_magnitude,
            divisor_magnitude,
        )

        fractional_part = self._divide_fractional_part_binary(
            remainder,
            divisor_magnitude,
            FRACTIONAL_PRECISION_BITS,
        )

        # Word32 хранит только целую часть результата в прямом коде
        signed_integer_part = integer_part
        if result_sign == 1 and integer_part != 0:
            signed_integer_part = -integer_part

        quotient_word = self._encoder.encode(signed_integer_part)

        binary_result = self._build_binary_result(
            result_sign,
            integer_part,
            fractional_part,
        )

        decimal_result = self._build_decimal_result(
            result_sign,
            integer_part,
            fractional_part,
        )

        return quotient_word, binary_result, decimal_result

    def _get_result_sign(self, dividend: int, divisor: int) -> int:
        return 1 if (dividend < 0) != (divisor < 0) else 0

    def _divide_integer_part_binary(
        self,
        dividend: int,
        divisor: int,
    ) -> tuple[int, int]:
        if dividend < divisor:
            return 0, dividend

        dividend_bits = self._to_binary_bits(dividend)

        quotient = 0
        remainder = 0

        for current_bit in dividend_bits:
            remainder = (remainder << 1) | current_bit
            quotient <<= 1

            if remainder >= divisor:
                remainder -= divisor
                quotient |= 1

        return quotient, remainder

    def _divide_fractional_part_binary(
        self,
        remainder: int,
        divisor: int,
        precision: int,
    ) -> str:
        fractional_bits: list[str] = []
        current_remainder = remainder

        for _ in range(precision):
            current_remainder <<= 1

            if current_remainder >= divisor:
                current_remainder -= divisor
                fractional_bits.append("1")
            else:
                fractional_bits.append("0")

        return "".join(fractional_bits)

    def _to_binary_bits(self, value: int) -> list[int]:
        if value == 0:
            return [0]

        reversed_bits: list[int] = []
        current_value = value

        while current_value > 0:
            reversed_bits.append(current_value & 1)
            current_value >>= 1

        return list(reversed(reversed_bits))

    def _integer_to_binary_string(self, value: int) -> str:
        bits = self._to_binary_bits(value)
        return "".join(str(bit) for bit in bits)

    def _build_binary_result(
        self,
        result_sign: int,
        integer_part: int,
        fractional_part: str,
    ) -> str:
        sign_prefix = ""
        if result_sign == 1 and (
            integer_part != 0 or self._has_non_zero_fraction(fractional_part)
        ):
            sign_prefix = "-"

        integer_binary = self._integer_to_binary_string(integer_part)
        return f"{sign_prefix}{integer_binary}.{fractional_part}"

    def _build_decimal_result(
        self,
        result_sign: int,
        integer_part: int,
        fractional_part: str,
    ) -> str:
        integer_decimal = float(integer_part)
        fractional_decimal = self._fraction_bits_to_decimal_value(fractional_part)
        total_value = integer_decimal + fractional_decimal

        if result_sign == 1 and total_value != 0:
            total_value = -total_value

        return f"{total_value:.{DECIMAL_RESULT_PRECISION}f}"

    def _fraction_bits_to_decimal_value(self, bits: str) -> float:
        result = 0.0
        weight = 0.5

        for bit in bits:
            if bit == "1":
                result += weight
            weight /= 2

        return result

    def _has_non_zero_fraction(self, fractional_part: str) -> bool:
        return any(bit == "1" for bit in fractional_part)