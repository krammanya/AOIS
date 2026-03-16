import pytest

from src.floating_point.binary32_arithmetic import Binary32Arithmetic
from src.floating_point.binary32_codec import Binary32Codec
from src.floating_point.binary32_number import Binary32Number
from src.floating_point.binary32_rounding import Binary32Rounding


def test_zero_encoding():
    word = Binary32Codec().from_decimal_string("0")
    assert word.to_string() == "00000000000000000000000000000000"


def test_negative_zero_encoding():
    word = Binary32Codec().from_decimal_string("-0")
    assert word.to_string() == "10000000000000000000000000000000"


def test_one_encoding():
    word = Binary32Codec().from_decimal_string("1")
    assert word.to_string() == "00111111100000000000000000000000"


def test_two_point_five_encoding():
    word = Binary32Codec().from_decimal_string("2.5")
    assert word.to_string() == "01000000001000000000000000000000"


def test_nan_encoding():
    codec = Binary32Codec()
    word = codec.from_decimal_string("nan")
    assert codec.to_decimal_string(word) == "nan"


def test_negative_infinity_encoding():
    word = Binary32Codec().from_decimal_string("-inf")
    assert word.to_string() == "11111111100000000000000000000000"


def test_scientific_notation_encoding():
    codec = Binary32Codec()
    word = codec.from_decimal_string("1.25e1")
    assert codec.to_decimal_string(word) == "12.5"


def test_invalid_rational_conversion_for_infinity():
    codec = Binary32Codec()
    infinity = codec.decode(codec.from_decimal_string("inf"))

    with pytest.raises(ValueError):
        codec.to_rational(infinity)


def test_negative_zero_to_decimal_string():
    codec = Binary32Codec()
    word = codec.from_decimal_string("-0")
    assert codec.to_decimal_string(word) == "0"


def test_addition():
    codec = Binary32Codec()
    arithmetic = Binary32Arithmetic()
    left_word = codec.from_decimal_string("1")
    right_word = codec.from_decimal_string("2")
    result_word = arithmetic.add(left_word, right_word)
    assert result_word.to_string() == "01000000010000000000000000000000"


def test_subtraction_of_equal_infinities_returns_nan():
    codec = Binary32Codec()
    arithmetic = Binary32Arithmetic()
    left_word = codec.from_decimal_string("inf")
    right_word = codec.from_decimal_string("inf")
    result_word = arithmetic.subtract(left_word, right_word)
    assert result_word.to_string() == "01111111110000000000000000000000"


def test_multiplication():
    codec = Binary32Codec()
    arithmetic = Binary32Arithmetic()
    left_word = codec.from_decimal_string("1.5")
    right_word = codec.from_decimal_string("2")
    result_word = arithmetic.multiply(left_word, right_word)
    assert result_word.to_string() == "01000000010000000000000000000000"


def test_division():
    codec = Binary32Codec()
    arithmetic = Binary32Arithmetic()
    left_word = codec.from_decimal_string("7")
    right_word = codec.from_decimal_string("2")
    result_word = arithmetic.divide(left_word, right_word)
    assert result_word.to_string() == "01000000011000000000000000000000"


def test_addition_with_positive_infinity():
    codec = Binary32Codec()
    arithmetic = Binary32Arithmetic()
    left_word = codec.from_decimal_string("inf")
    right_word = codec.from_decimal_string("1")
    result_word = arithmetic.add(left_word, right_word)
    assert codec.to_decimal_string(result_word) == "inf"


def test_addition_of_opposite_infinities_returns_nan():
    codec = Binary32Codec()
    arithmetic = Binary32Arithmetic()
    left_word = codec.from_decimal_string("inf")
    right_word = codec.from_decimal_string("-inf")
    result_word = arithmetic.add(left_word, right_word)
    assert codec.to_decimal_string(result_word) == "nan"


def test_multiplication_of_zero_and_infinity_returns_nan():
    codec = Binary32Codec()
    arithmetic = Binary32Arithmetic()
    left_word = codec.from_decimal_string("0")
    right_word = codec.from_decimal_string("inf")
    result_word = arithmetic.multiply(left_word, right_word)
    assert codec.to_decimal_string(result_word) == "nan"


def test_division_by_zero_returns_infinity():
    codec = Binary32Codec()
    arithmetic = Binary32Arithmetic()
    left_word = codec.from_decimal_string("5")
    right_word = codec.from_decimal_string("0")
    result_word = arithmetic.divide(left_word, right_word)
    assert codec.to_decimal_string(result_word) == "inf"


def test_zero_divided_by_zero_returns_nan():
    codec = Binary32Codec()
    arithmetic = Binary32Arithmetic()
    left_word = codec.from_decimal_string("0")
    right_word = codec.from_decimal_string("0")
    result_word = arithmetic.divide(left_word, right_word)
    assert codec.to_decimal_string(result_word) == "nan"


def test_invalid_sign_raises_error():
    with pytest.raises(ValueError):
        Binary32Number.from_components(2, 0, 0)


def test_invalid_exponent_raises_error():
    with pytest.raises(ValueError):
        Binary32Number.from_components(0, 256, 0)


def test_invalid_fraction_raises_error():
    with pytest.raises(ValueError):
        Binary32Number.from_components(0, 0, 1 << 23)


def test_unbiased_exponent_for_infinity_raises_error():
    number = Binary32Number.infinity_with_sign(0)

    with pytest.raises(ValueError):
        _ = number.unbiased_exponent


def test_negate_flips_sign():
    number = Binary32Number.from_components(0, 127, 0)
    assert number.negate().sign == 1


def test_subnormal_properties():
    number = Binary32Number.from_components(0, 0, 1)
    assert number.is_subnormal
    assert number.significand_value == 1


def test_round_fraction_to_zero():
    number = Binary32Rounding().round_fraction(1, 0, 1)
    assert number.is_zero
    assert number.sign == 1


def test_round_fraction_to_infinity():
    number = Binary32Rounding().round_fraction(0, 1 << 200, 1)
    assert number.is_infinity


def test_round_fraction_to_subnormal():
    number = Binary32Rounding().round_fraction(0, 1, 1 << 149)
    assert number.is_subnormal


def test_round_half_to_even():
    assert Binary32Rounding()._rounded_quotient(3, 2, 0) == 2


def test_negative_shift_application():
    numerator, denominator = Binary32Rounding()._apply_shift(3, 5, -2)
    assert (numerator, denominator) == (3, 20)
