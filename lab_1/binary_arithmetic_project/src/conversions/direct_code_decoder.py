from src.utils.word32 import Word32

class DirectCodeDecoder:
    def decode(self, word: Word32) -> int:
        bits = word.bits
        sign_bit = bits[0]
        magnitude_bits = bits[1:]
        
        magnitude_value =  self._unsigned_bits_to_int(magnitude_bits)
        
        if sign_bit == 1:
            return -magnitude_value
        
        return magnitude_value
    
    def _unsigned_bits_to_int(self, bits: list[int]) -> int:
        result = 0

        for bit in bits:
            result = result * 2 + bit

        return result