import pytest

from src.conversions.unsigned_binary_converter import UnsignedBinaryConverter


def test_to_bits_converts_zero():
    assert UnsignedBinaryConverter.to_bits(0, 4) == [0, 0, 0, 0]


def test_to_bits_converts_positive_number():
    assert UnsignedBinaryConverter.to_bits(5, 4) == [0, 1, 0, 1]


def test_to_bits_rejects_negative_value():
    with pytest.raises(ValueError, match="non-negative"):
        UnsignedBinaryConverter.to_bits(-1, 4)


def test_to_bits_rejects_value_that_does_not_fit():
    with pytest.raises(ValueError, match="does not fit"):
        UnsignedBinaryConverter.to_bits(16, 4)
