import pytest

from src.utils.word32 import Word32


def test_create_valid_word32():
    bits = [0] * 32
    word = Word32(bits)
    assert word.bits == bits


def test_invalid_length_raises_value_error():
    bits = [0] * 31
    with pytest.raises(ValueError, match="exactly 32 bits"):
        Word32(bits)


def test_invalid_bit_value_raises_value_error():
    bits = [0] * 31 + [2]
    with pytest.raises(ValueError, match="only 0 or 1"):
        Word32(bits)


def test_to_string_returns_binary_string():
    bits = [1, 0, 1, 0] + [0] * 28
    word = Word32(bits)
    assert word.to_string() == "1010" + "0" * 28


def test_bits_returns_copy_not_original_internal_list():
    bits = [0] * 32
    word = Word32(bits)

    returned_bits = word.bits
    returned_bits[0] = 1

    assert word.bits[0] == 0


def test_equal_words_are_equal():
    bits = [1] * 32
    word1 = Word32(bits)
    word2 = Word32(bits)
    assert word1 == word2


def test_word32_not_equal_to_other_type():
    word = Word32([0] * 32)
    assert word != [0] * 32