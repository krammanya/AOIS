from src.bcd.bcd2421_codec import Bcd2421Codec
from src.bcd.bcd2421_constants import BITS_PER_DIGIT
from src.bcd.bcd2421_number import Bcd2421Number


ZERO_TETRAD: list[int] = [0, 0, 0, 0]
ONE_TETRAD: list[int] = [0, 0, 0, 1]


class Bcd2421Adder:
    def __init__(self) -> None:
        self._codec = Bcd2421Codec()

    def add(self, left_value: str | int, right_value: str | int) -> tuple[Bcd2421Number, str]:
        left_number = self._codec.encode(left_value)
        right_number = self._codec.encode(right_value)
        result_number = self.add_numbers(left_number, right_number)
        result_decimal = self._codec.decode(result_number)
        return result_number, result_decimal

    def add_numbers(
        self,
        left_number: Bcd2421Number,
        right_number: Bcd2421Number,
    ) -> Bcd2421Number:
        aligned_left_tetrads, aligned_right_tetrads = self._align_tetrad_counts(
            left_number.tetrads,
            right_number.tetrads,
        )

        result_tetrads = self._add_aligned_tetrads(
            aligned_left_tetrads,
            aligned_right_tetrads,
        )
        return Bcd2421Number(self._flatten_tetrads(result_tetrads))

    def _align_tetrad_counts(
        self,
        left_tetrads: list[list[int]],
        right_tetrads: list[list[int]],
    ) -> tuple[list[list[int]], list[list[int]]]:
        max_length = max(len(left_tetrads), len(right_tetrads))
        return (
            self._pad_tetrads(left_tetrads, max_length),
            self._pad_tetrads(right_tetrads, max_length),3
        )

    def _pad_tetrads(
        self,
        tetrads: list[list[int]],
        size: int,
    ) -> list[list[int]]:
        padding_size = size - len(tetrads)
        zero_tetrads = [ZERO_TETRAD[:] for _ in range(padding_size)]
        return zero_tetrads + tetrads

    def _add_aligned_tetrads(
        self,
        left_tetrads: list[list[int]],
        right_tetrads: list[list[int]],
    ) -> list[list[int]]:
        carry = 0
        result_tetrads: list[list[int]] = []

        for index in range(len(left_tetrads) - 1, -1, -1):
            carry, result_tetrad = self._add_tetrad(
                left_tetrads[index],
                right_tetrads[index],
                carry,
            )
            result_tetrads.insert(0, result_tetrad)

        if carry != 0:
            result_tetrads.insert(0, ONE_TETRAD[:])

        return result_tetrads

    def _add_tetrad(
        self,
        left_tetrad: list[int],
        right_tetrad: list[int],
        carry_in: int,
    ) -> tuple[int, list[int]]:
        raw_sum = self._sum_tetrad_bits(left_tetrad, right_tetrad, carry_in)
        carry_out, corrected_value = self._correct_raw_sum(raw_sum)
        return carry_out, self._value_to_tetrad(corrected_value)

    def _sum_tetrad_bits(
        self,
        left_tetrad: list[int],
        right_tetrad: list[int],
        carry_in: int,
    ) -> int:
        result = carry_in

        for index in range(BITS_PER_DIGIT):
            result += (left_tetrad[index] << (BITS_PER_DIGIT - 1 - index))
            result += (right_tetrad[index] << (BITS_PER_DIGIT - 1 - index))

        return result

    def _correct_raw_sum(self, raw_sum: int) -> tuple[int, int]:
        if self._is_valid_digit_value(raw_sum):
            return 0, raw_sum

        if self._requires_low_range_correction(raw_sum):
            return 0, raw_sum + 6

        if self._requires_high_range_correction(raw_sum):
            return 1, raw_sum - 6

        if self._is_valid_carry_value(raw_sum):
            return 1, raw_sum - 16

        raise ValueError("Invalid raw sum for BCD 2421 addition")

    def _is_valid_digit_value(self, raw_sum: int) -> bool:
        return 0 <= raw_sum <= 4 or 11 <= raw_sum <= 15

    def _requires_low_range_correction(self, raw_sum: int) -> bool:
        return 5 <= raw_sum <= 9

    def _requires_high_range_correction(self, raw_sum: int) -> bool:
        return 22 <= raw_sum <= 26

    def _is_valid_carry_value(self, raw_sum: int) -> bool:
        return 16 <= raw_sum <= 20 or 27 <= raw_sum <= 31

    def _value_to_tetrad(self, value: int) -> list[int]:
        return [
            (value >> 3) & 1,
            (value >> 2) & 1,
            (value >> 1) & 1,
            value & 1,
        ]

    def _flatten_tetrads(self, tetrads: list[list[int]]) -> list[int]:
        bits: list[int] = []

        for tetrad in tetrads:
            bits.extend(tetrad)

        return bits
