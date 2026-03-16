import pytest

from src.bcd.bcd2421_adder import Bcd2421Adder
from src.bcd.bcd2421_codec import Bcd2421Codec
from src.bcd.bcd2421_number import Bcd2421Number


def test_encode_single_digit():
    encoded_number = Bcd2421Codec().encode("5")
    assert encoded_number.to_string() == "1011"


def test_encode_multi_digit_number():
    encoded_number = Bcd2421Codec().encode("249")
    assert encoded_number.to_string() == "001001001111"


def test_decode_multi_digit_number():
    number = Bcd2421Number([0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1])
    assert Bcd2421Codec().decode(number) == "259"


def test_invalid_tetrad_raises_error():
    with pytest.raises(ValueError):
        Bcd2421Codec().decode_tetrad([0, 1, 0, 1])


def test_encode_rejects_negative_numbers():
    with pytest.raises(ValueError):
        Bcd2421Codec().encode("-5")


def test_encode_rejects_non_digit_text():
    with pytest.raises(ValueError):
        Bcd2421Codec().encode("12a")


def test_encode_strips_leading_zeros():
    encoded_number = Bcd2421Codec().encode("0007")
    assert encoded_number.to_string() == "1101"


def test_encode_digit_rejects_invalid_digit():
    with pytest.raises(ValueError):
        Bcd2421Codec().encode_digit(10)


def test_add_without_carry():
    result_number, result_decimal = Bcd2421Adder().add("12", "25")
    assert result_decimal == "37"
    assert result_number.to_string() == "00111101"


def test_add_numbers_uses_bcd_operands():
    codec = Bcd2421Codec()
    left_number = codec.encode("12")
    right_number = codec.encode("25")
    result_number = Bcd2421Adder().add_numbers(left_number, right_number)
    assert result_number.to_string() == "00111101"
    assert codec.decode(result_number) == "37"


def test_add_with_carry():
    result_number, result_decimal = Bcd2421Adder().add("59", "68")
    assert result_decimal == "127"
    assert result_number.to_string() == "000100101101"


def test_add_zero():
    result_number, result_decimal = Bcd2421Adder().add("0", "0")
    assert result_decimal == "0"
    assert result_number.to_string() == "0000"


def test_add_numbers_with_different_length():
    result_number, result_decimal = Bcd2421Adder().add("999", "1")
    assert result_decimal == "1000"
    assert result_number.to_string() == "0001000000000000"


def test_add_single_tetrad_with_low_range_correction():
    carry_out, result_tetrad = Bcd2421Adder()._add_tetrad([0, 1, 0, 0], [0, 0, 0, 1], 0)
    assert (carry_out, result_tetrad) == (0, [1, 0, 1, 1])


def test_add_single_tetrad_with_high_range_correction():
    carry_out, result_tetrad = Bcd2421Adder()._add_tetrad([1, 0, 1, 1], [1, 0, 1, 1], 0)
    assert (carry_out, result_tetrad) == (1, [0, 0, 0, 0])


def test_bcd_number_rejects_empty_bits():
    with pytest.raises(ValueError):
        Bcd2421Number([])


def test_bcd_number_rejects_invalid_length():
    with pytest.raises(ValueError):
        Bcd2421Number([0, 0, 0])


def test_bcd_number_rejects_invalid_bit_value():
    with pytest.raises(ValueError):
        Bcd2421Number([0, 0, 0, 2])
