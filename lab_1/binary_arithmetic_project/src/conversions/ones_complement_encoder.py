from src.conversions.base_integer_encoder import BaseIntegerEncoder
from src.conversions.integer_encoder import IntegerEncoder
from src.utils.bit_operations import BitOperations
from src.utils.word32 import Word32


class OnesComplementEncoder(BaseIntegerEncoder, IntegerEncoder):
    def encode(self, value: int) -> Word32:
        self._validate_ones_complement_range(value)

        if value >= 0:
            return Word32(self._get_absolute_value_bits_32(value))

        absolute_bits = self._get_absolute_value_bits_32(value)
        inverted_bits = BitOperations.invert_bits(absolute_bits)

        return Word32(inverted_bits)