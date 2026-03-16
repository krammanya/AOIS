import pytest

from src.conversions.direct_code_decoder import DirectCodeDecoder
from src.conversions.direct_code_encoder import DirectCodeEncoder
from src.conversions.ones_complement_encoder import OnesComplementEncoder
from src.conversions.twos_complement_decoder import TwosComplementDecoder
from src.conversions.twos_complement_encoder import TwosComplementEncoder


def test_direct_code_encoder_encodes_positive_value():
    encoder = DirectCodeEncoder()
    word = encoder.encode(5)
    assert word.to_string() == "00000000000000000000000000000101"


def test_direct_code_encoder_encodes_negative_value():
    encoder = DirectCodeEncoder()
    word = encoder.encode(-5)
    assert word.to_string() == "10000000000000000000000000000101"


def test_direct_code_encoder_rejects_out_of_range_value():
    encoder = DirectCodeEncoder()

    with pytest.raises(ValueError, match="out of range"):
        encoder.encode(1 << 31)


def test_ones_complement_encoder_encodes_negative_value():
    encoder = OnesComplementEncoder()
    word = encoder.encode(-5)
    assert word.to_string() == "11111111111111111111111111111010"


def test_twos_complement_encoder_encodes_negative_value():
    encoder = TwosComplementEncoder()
    word = encoder.encode(-5)
    assert word.to_string() == "11111111111111111111111111111011"


def test_twos_complement_encoder_rejects_out_of_range_value():
    encoder = TwosComplementEncoder()

    with pytest.raises(ValueError, match="out of range"):
        encoder.encode(1 << 31)


def test_direct_code_decoder_decodes_negative_value():
    encoder = DirectCodeEncoder()
    decoder = DirectCodeDecoder()
    word = encoder.encode(-9)
    assert decoder.decode(word) == -9


def test_twos_complement_decoder_decodes_positive_value():
    encoder = TwosComplementEncoder()
    decoder = TwosComplementDecoder()
    word = encoder.encode(12)
    assert decoder.decode(word) == 12


def test_twos_complement_decoder_decodes_negative_value():
    encoder = TwosComplementEncoder()
    decoder = TwosComplementDecoder()
    word = encoder.encode(-12)
    assert decoder.decode(word) == -12
