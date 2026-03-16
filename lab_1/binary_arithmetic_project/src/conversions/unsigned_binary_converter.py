from typing import List

class UnsignedBinaryConverter:
    @staticmethod
    def to_bits(value: int, size: int) -> List[int]:
        if value < 0:
            raise ValueError("Value must be non-negative")
        bits: List[int] = [0] * size
        current_value = value
        bit_index = size - 1
        
        while current_value > 0 and bit_index >= 0:
            bits[bit_index] = current_value % 2
            current_value //= 2
            bit_index -= 1
            
        if current_value != 0:
            raise ValueError ("Value does not fit in the specified bit size")
        
        return bits