BITS_PER_DIGIT: int = 4
DECIMAL_BASE: int = 10

DECIMAL_TO_BCD2421: dict[int, list[int]] = {
    0: [0, 0, 0, 0],
    1: [0, 0, 0, 1],
    2: [0, 0, 1, 0],
    3: [0, 0, 1, 1],
    4: [0, 1, 0, 0],
    5: [1, 0, 1, 1],
    6: [1, 1, 0, 0],
    7: [1, 1, 0, 1],
    8: [1, 1, 1, 0],
    9: [1, 1, 1, 1],
}

BCD2421_TO_DECIMAL: dict[tuple[int, int, int, int], int] = {
    tuple(bits): digit for digit, bits in DECIMAL_TO_BCD2421.items()
}
