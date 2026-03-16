from src.floating_point.binary32_number import (
    Binary32Number,
    EXPONENT_BIAS,
    FRACTION_BITS_COUNT,
    HIDDEN_BIT_VALUE,
    MIN_NORMAL_UNBIASED_EXPONENT,
    MIN_SUBNORMAL_UNBIASED_EXPONENT,
)


class Binary32Rounding:
    def round_fraction(
        self,
        sign: int,
        numerator: int,
        denominator: int,
    ) -> Binary32Number:
        if numerator == 0:
            return Binary32Number.zero_with_sign(sign)

        exponent = self._find_exponent(numerator, denominator)

        if exponent > EXPONENT_BIAS:
            return Binary32Number.infinity_with_sign(sign)

        if exponent < MIN_NORMAL_UNBIASED_EXPONENT:
            return self._build_subnormal(sign, numerator, denominator)

        return self._build_normal(sign, numerator, denominator, exponent)

    def _find_exponent(self, numerator: int, denominator: int) -> int:
        exponent = numerator.bit_length() - denominator.bit_length()

        while self._is_less_than_power(numerator, denominator, exponent):
            exponent -= 1

        while self._is_greater_or_equal_next_power(
            numerator,
            denominator,
            exponent,
        ):
            exponent += 1

        return exponent

    def _build_normal(
        self,
        sign: int,
        numerator: int,
        denominator: int,
        exponent: int,
    ) -> Binary32Number:
        significand = self._rounded_quotient(
            numerator,
            denominator,
            FRACTION_BITS_COUNT - exponent,
        )

        if significand == (HIDDEN_BIT_VALUE << 1):
            exponent += 1
            significand >>= 1

        if exponent > EXPONENT_BIAS:
            return Binary32Number.infinity_with_sign(sign)

        stored_exponent = exponent + EXPONENT_BIAS
        stored_fraction = significand - HIDDEN_BIT_VALUE

        return Binary32Number.from_components(
            sign,
            stored_exponent,
            stored_fraction,
        )

    def _build_subnormal(
        self,
        sign: int,
        numerator: int,
        denominator: int,
    ) -> Binary32Number:
        fraction = self._rounded_quotient(
            numerator,
            denominator,
            -MIN_SUBNORMAL_UNBIASED_EXPONENT,
        )

        if fraction >= HIDDEN_BIT_VALUE:
            return Binary32Number.from_components(
                sign,
                1,
                0,
            )

        return Binary32Number.from_components(sign, 0, fraction)

    def _rounded_quotient(
        self,
        numerator: int,
        denominator: int,
        shift: int,
    ) -> int:
        shifted_numerator, shifted_denominator = self._apply_shift(
            numerator,
            denominator,
            shift,
        )
        quotient = shifted_numerator // shifted_denominator
        remainder = shifted_numerator % shifted_denominator

        if self._should_round_up(quotient, remainder, shifted_denominator):
            return quotient + 1

        return quotient

    def _apply_shift(
        self,
        numerator: int,
        denominator: int,
        shift: int,
    ) -> tuple[int, int]:
        if shift >= 0:
            return numerator << shift, denominator

        return numerator, denominator << (-shift)

    def _should_round_up(
        self,
        quotient: int,
        remainder: int,
        denominator: int,
    ) -> bool:
        doubled_remainder = remainder << 1

        if doubled_remainder > denominator:
            return True

        if doubled_remainder < denominator:
            return False

        return quotient % 2 == 1

    def _is_less_than_power(
        self,
        numerator: int,
        denominator: int,
        exponent: int,
    ) -> bool:
        left_value, right_value = self._scaled_pair(
            numerator,
            denominator,
            exponent,
        )
        return left_value < right_value

    def _is_greater_or_equal_next_power(
        self,
        numerator: int,
        denominator: int,
        exponent: int,
    ) -> bool:
        left_value, right_value = self._scaled_pair(
            numerator,
            denominator,
            exponent + 1,
        )
        return left_value >= right_value

    def _scaled_pair(
        self,
        numerator: int,
        denominator: int,
        exponent: int,
    ) -> tuple[int, int]:
        if exponent >= 0:
            return numerator, denominator << exponent

        return numerator << (-exponent), denominator
