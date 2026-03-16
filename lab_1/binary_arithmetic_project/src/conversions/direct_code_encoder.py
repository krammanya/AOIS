from src.conversions.base_integer_encoder import BaseIntegerEncoder
from src.conversions.integer_encoder import IntegerEncoder
from src.utils.word32 import Word32

class DirectCodeEncoder(BaseIntegerEncoder, IntegerEncoder):
    def encode(self, value: int) -> Word32:
        self._validate_direct_code_range(value)
        
        sign_bit = self._get_sign_bit(value)
        magnitude_bits = self._get_magnitude_bits(value)
        result_bits = [sign_bit] + magnitude_bits
        
        return Word32(result_bits)