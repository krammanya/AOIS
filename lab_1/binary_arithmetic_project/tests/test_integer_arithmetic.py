import pytest

from src.arithmetic.direct_code_divider import DirectCodeDivider
from src.arithmetic.direct_code_multiplier import DirectCodeMultiplier
from src.arithmetic.twos_complement_adder import TwosComplementAdder
from src.arithmetic.twos_complement_subtractor import TwosComplementSubtractor
from src.conversions.direct_code_encoder import DirectCodeEncoder
from src.conversions.twos_complement_encoder import TwosComplementEncoder


def test_twos_complement_adder_adds_positive_values():
    adder = TwosComplementAdder()
    result_word, result_value, overflow = adder.add(5, 7)
    assert result_word.to_string() == "00000000000000000000000000001100"
    assert result_value == 12
    assert overflow is False


def test_twos_complement_adder_detects_overflow():
    adder = TwosComplementAdder()
    _, _, overflow = adder.add((1 << 30), (1 << 30))
    assert overflow is True


def test_twos_complement_adder_add_words_matches_integer_addition():
    encoder = TwosComplementEncoder()
    adder = TwosComplementAdder()
    left_word = encoder.encode(-3)
    right_word = encoder.encode(8)
    result_word, overflow = adder.add_words(left_word, right_word)
    assert result_word.to_string() == encoder.encode(5).to_string()
    assert overflow is False


def test_twos_complement_subtractor_subtracts_values():
    subtractor = TwosComplementSubtractor()
    result_word, result_value, overflow = subtractor.subtract(10, 3)
    assert result_word.to_string() == "00000000000000000000000000000111"
    assert result_value == 7
    assert overflow is False


def test_twos_complement_subtractor_negates_value():
    subtractor = TwosComplementSubtractor()
    negated_word = subtractor.negate(5)
    assert negated_word.to_string() == "11111111111111111111111111111011"


def test_direct_code_multiplier_multiplies_values():
    multiplier = DirectCodeMultiplier()
    result_word, result_value = multiplier.multiply(3, -4)
    assert result_word.to_string() == "10000000000000000000000000001100"
    assert result_value == -12


def test_direct_code_multiplier_rejects_out_of_range_result():
    multiplier = DirectCodeMultiplier()

    with pytest.raises(ValueError, match="out of range"):
        multiplier.multiply((1 << 30) - 1, 3)


def test_direct_code_divider_divides_values():
    divider = DirectCodeDivider()
    quotient_word, binary_result, decimal_result = divider.divide(7, 2)
    assert quotient_word.to_string() == DirectCodeEncoder().encode(3).to_string()
    assert binary_result.startswith("11.")
    assert decimal_result == "3.50000"


def test_direct_code_divider_rejects_division_by_zero():
    divider = DirectCodeDivider()

    with pytest.raises(ValueError, match="Division by zero"):
        divider.divide(7, 0)
