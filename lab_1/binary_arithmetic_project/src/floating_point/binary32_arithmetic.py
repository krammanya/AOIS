from collections.abc import Callable

from src.utils.word32 import Word32
from src.floating_point.binary32_codec import Binary32Codec
from src.floating_point.binary32_number import Binary32Number
from src.floating_point.binary32_rounding import Binary32Rounding


class Binary32Arithmetic:
    def __init__(self) -> None:
        self._codec = Binary32Codec()
        self._rounding = Binary32Rounding()

    def add(self, left_word: Word32, right_word: Word32) -> Word32:
        return self._binary_operation(
            left_word,
            right_word,
            self._special_addition_result,
            lambda left_num, left_den, right_num, right_den: (
                left_num * right_den + right_num * left_den,
                left_den * right_den,
            ),
        )

    def subtract(self, left_word: Word32, right_word: Word32) -> Word32:
        right_number = self._codec.decode(right_word)
        negated_right_word = self._codec.encode(right_number.negate())
        return self.add(left_word, negated_right_word)

    def multiply(self, left_word: Word32, right_word: Word32) -> Word32:
        return self._binary_operation(
            left_word,
            right_word,
            self._special_multiplication_result,
            lambda left_num, left_den, right_num, right_den: (
                left_num * right_num,
                left_den * right_den,
            ),
        )

    def divide(self, left_word: Word32, right_word: Word32) -> Word32:
        return self._binary_operation(
            left_word,
            right_word,
            self._special_division_result,
            lambda left_num, left_den, right_num, right_den: (
                left_num * right_den,
                left_den * right_num,
            ),
        )

    def _binary_operation(
        self,
        left_word: Word32,
        right_word: Word32,
        special_handler: Callable[
            [Binary32Number, Binary32Number],
            Binary32Number | None,
        ],
        operation: Callable[[int, int, int, int], tuple[int, int]],
    ) -> Word32:
        left_number = self._codec.decode(left_word)
        right_number = self._codec.decode(right_word)

        special_result = special_handler(left_number, right_number)
        if special_result is not None:
            return self._codec.encode(special_result)

        left_numerator, left_denominator = self._codec.to_rational(left_number)
        right_numerator, right_denominator = self._codec.to_rational(right_number)

        numerator, denominator = operation(
            left_numerator,
            left_denominator,
            right_numerator,
            right_denominator,
        )

        if denominator < 0:
            numerator = -numerator
            denominator = -denominator

        sign = 1 if numerator < 0 else 0
        absolute_numerator = abs(numerator)
        result_number = self._rounding.round_fraction(
            sign,
            absolute_numerator,
            denominator,
        )
        return self._codec.encode(result_number)

    def _special_addition_result(
        self,
        left_number: Binary32Number,
        right_number: Binary32Number,
    ) -> Binary32Number | None:
        if left_number.is_nan or right_number.is_nan:
            return Binary32Number.quiet_nan()

        if left_number.is_infinity and right_number.is_infinity:
            if left_number.sign != right_number.sign:
                return Binary32Number.quiet_nan()
            return left_number

        if left_number.is_infinity:
            return left_number

        if right_number.is_infinity:
            return right_number

        return None

    def _special_multiplication_result(
        self,
        left_number: Binary32Number,
        right_number: Binary32Number,
    ) -> Binary32Number | None:
        if left_number.is_nan or right_number.is_nan:
            return Binary32Number.quiet_nan()

        if self._is_infinity_zero_pair(left_number, right_number):
            return Binary32Number.quiet_nan()

        if left_number.is_infinity or right_number.is_infinity:
            result_sign = left_number.sign ^ right_number.sign
            return Binary32Number.infinity_with_sign(result_sign)

        return None

    def _special_division_result(
        self,
        left_number: Binary32Number,
        right_number: Binary32Number,
    ) -> Binary32Number | None:
        if left_number.is_nan or right_number.is_nan:
            return Binary32Number.quiet_nan()

        if left_number.is_infinity and right_number.is_infinity:
            return Binary32Number.quiet_nan()

        if left_number.is_zero and right_number.is_zero:
            return Binary32Number.quiet_nan()

        result_sign = left_number.sign ^ right_number.sign

        if left_number.is_infinity:
            return Binary32Number.infinity_with_sign(result_sign)

        if right_number.is_infinity:
            return Binary32Number.zero_with_sign(result_sign)

        if right_number.is_zero:
            return Binary32Number.infinity_with_sign(result_sign)

        if left_number.is_zero:
            return Binary32Number.zero_with_sign(result_sign)

        return None

    def _is_infinity_zero_pair(
        self,
        left_number: Binary32Number,
        right_number: Binary32Number,
    ) -> bool:
        left_is_infinite_zero = left_number.is_infinity and right_number.is_zero
        right_is_infinite_zero = right_number.is_infinity and left_number.is_zero
        return left_is_infinite_zero or right_is_infinite_zero
