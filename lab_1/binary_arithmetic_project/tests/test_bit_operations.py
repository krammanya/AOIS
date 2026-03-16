from src.utils.bit_operations import BitOperations


def test_invert_bits_flips_every_bit():
    bits = [0, 1, 0, 1]
    assert BitOperations.invert_bits(bits) == [1, 0, 1, 0]


def test_add_one_updates_last_bit_without_carry_chain():
    bits = [0, 0, 0, 1]
    assert BitOperations.add_one(bits) == [0, 0, 1, 0]


def test_add_one_propagates_carry_through_multiple_bits():
    bits = [0, 1, 1, 1]
    assert BitOperations.add_one(bits) == [1, 0, 0, 0]


def test_add_one_wraps_all_ones_to_zeroes():
    bits = [1, 1, 1, 1]
    assert BitOperations.add_one(bits) == [0, 0, 0, 0]
