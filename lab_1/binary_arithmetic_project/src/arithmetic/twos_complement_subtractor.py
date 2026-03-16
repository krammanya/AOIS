from src.arithmetic.twos_complement_adder import TwosComplementAdder
from src.conversions.twos_complement_decoder import TwosComplementDecoder
from src.conversions.twos_complement_encoder import TwosComplementEncoder
from src.utils.bit_operations import BitOperations
from src.utils.word32 import Word32


class TwosComplementSubtractor:
    def __init__(self) -> None:
        self._encoder = TwosComplementEncoder()
        self._decoder = TwosComplementDecoder()
        self._adder = TwosComplementAdder()

    def subtract(
        self,
        minuend: int,
        subtrahend: int,
    ) -> tuple[Word32, int, bool]:
        minuend_word = self._encoder.encode(minuend)
        subtrahend_word = self._encoder.encode(subtrahend)

        negated_subtrahend_word = self.negate_word(subtrahend_word)
        result_word, overflow = self._adder.add_words(
            minuend_word,
            negated_subtrahend_word,
        )
        result_value = self._decoder.decode(result_word)

        return result_word, result_value, overflow

    def negate(self, value: int) -> Word32:
        word = self._encoder.encode(value)
        return self.negate_word(word)

    def negate_word(self, word: Word32) -> Word32:
        inverted_bits = BitOperations.invert_bits(word.bits)
        negated_bits = BitOperations.add_one(inverted_bits)

        return Word32(negated_bits)