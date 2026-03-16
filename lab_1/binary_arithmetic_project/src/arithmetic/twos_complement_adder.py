from src.conversions.twos_complement_decoder import TwosComplementDecoder
from src.conversions.twos_complement_encoder import TwosComplementEncoder
from src.utils.word32 import Word32


class TwosComplementAdder:
    def __init__(self) -> None:
        self._encoder = TwosComplementEncoder()
        self._decoder = TwosComplementDecoder()

    def add(self, left_value: int, right_value: int) -> tuple[Word32, int, bool]:
        left_word = self._encoder.encode(left_value)
        right_word = self._encoder.encode(right_value)

        result_word, overflow = self.add_words(left_word, right_word)
        result_value = self._decoder.decode(result_word)

        return result_word, result_value, overflow

    def add_words(self, left_word: Word32, right_word: Word32) -> tuple[Word32, bool]:
        left_bits = left_word.bits
        right_bits = right_word.bits

        result_bits = [0] * len(left_bits)
        carry = 0

        for index in range(len(left_bits) - 1, -1, -1):
            current_sum = left_bits[index] + right_bits[index] + carry
            result_bits[index] = current_sum % 2
            carry = current_sum // 2

        result_word = Word32(result_bits)
        overflow = self._has_overflow(left_word, right_word, result_word)

        return result_word, overflow

    def _has_overflow(
        self,
        left_word: Word32,
        right_word: Word32,
        result_word: Word32,
    ) -> bool:
        left_sign = left_word.bits[0]
        right_sign = right_word.bits[0]
        result_sign = result_word.bits[0]

        same_input_signs = left_sign == right_sign
        different_result_sign = result_sign != left_sign

        return same_input_signs and different_result_sign