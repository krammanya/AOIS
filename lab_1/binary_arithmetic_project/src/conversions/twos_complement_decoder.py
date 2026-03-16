from src.config import WORD_SIZE_BITS
from src.utils.bit_operations import BitOperations
from src.utils.word32 import Word32


class TwosComplementDecoder:
    def decode(self, word: Word32) -> int:
        bits = word.bits

        if bits[0] == 0:
            return self._unsigned_bits_to_int(bits)

        inverted_bits = BitOperations.invert_bits(bits)
        magnitude_bits = BitOperations.add_one(inverted_bits)
        magnitude_value = self._unsigned_bits_to_int(magnitude_bits)

        return -magnitude_value

    def _unsigned_bits_to_int(self, bits: list[int]) -> int:
        result = 0

        for bit in bits:
            result = result * 2 + bit

        return result