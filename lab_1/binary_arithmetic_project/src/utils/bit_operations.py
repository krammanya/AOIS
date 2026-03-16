from typing import List

BitArray = List[int]


class BitOperations:
    @staticmethod
    def invert_bits(bits: BitArray) -> BitArray:
        result: BitArray = []

        for bit in bits:
            if bit == 0:
                result.append(1)
            else:
                result.append(0)

        return result

    @staticmethod
    def add_one(bits: BitArray) -> BitArray:
        result = bits[:]
        carry = 1

        for index in range(len(result) - 1, -1, -1):
            current_sum = result[index] + carry

            if current_sum == 2:
                result[index] = 0
                carry = 1
            else:
                result[index] = current_sum
                carry = 0
                break

        return result