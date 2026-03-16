from src.config import MAGNITUDE_BITS
from src.conversions.direct_code_decoder import DirectCodeDecoder
from src.conversions.direct_code_encoder import DirectCodeEncoder
from src.utils.word32 import Word32


class DirectCodeMultiplier:
    def __init__(self) -> None:
        self._encoder = DirectCodeEncoder()
        self._decoder = DirectCodeDecoder()

    def multiply(self, left_value: int, right_value: int) -> tuple[Word32, int]:
        left_word = self._encoder.encode(left_value)
        right_word = self._encoder.encode(right_value)

        result_word = self._multiply_words(left_word, right_word)
        result_value = self._decoder.decode(result_word)

        return result_word, result_value

    def _multiply_words(self, left_word: Word32, right_word: Word32) -> Word32:
        left_bits = left_word.bits
        right_bits = right_word.bits

        left_sign = left_bits[0]
        right_sign = right_bits[0]
        result_sign = 1 if left_sign != right_sign else 0

        left_magnitude = left_bits[1:]
        right_magnitude = right_bits[1:]

        result_magnitude = self._multiply_magnitudes(left_magnitude, right_magnitude)

        if self._is_zero(result_magnitude):
            result_sign = 0

        return Word32([result_sign] + result_magnitude)

    def _multiply_magnitudes(
        self,
        left_magnitude: list[int],
        right_magnitude: list[int],
    ) -> list[int]:
        result = [0] * MAGNITUDE_BITS

        for shift in range(MAGNITUDE_BITS):
            right_index = MAGNITUDE_BITS - 1 - shift

            if right_magnitude[right_index] == 1:
                shifted_left = self._shift_left(left_magnitude, shift)
                result = self._add_bit_arrays(result, shifted_left)

        return result

    def _shift_left(self, bits: list[int], shift: int) -> list[int]:
        if shift == 0:
            return bits[:]

        if shift >= len(bits):
            return [0] * len(bits)

        return bits[shift:] + [0] * shift

    def _add_bit_arrays(
        self,
        left_bits: list[int],
        right_bits: list[int],
    ) -> list[int]:
        result = [0] * len(left_bits)
        carry = 0

        for index in range(len(left_bits) - 1, -1, -1):
            current_sum = left_bits[index] + right_bits[index] + carry
            result[index] = current_sum % 2
            carry = current_sum // 2

        if carry != 0:
            raise ValueError("Multiplication result is out of range for direct code")

        return result

    def _is_zero(self, bits: list[int]) -> bool:
        return all(bit == 0 for bit in bits)