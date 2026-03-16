from src.bcd.bcd2421_constants import BCD2421_TO_DECIMAL, DECIMAL_TO_BCD2421
from src.bcd.bcd2421_number import Bcd2421Number


class Bcd2421Codec:
    def encode(self, value: str | int) -> Bcd2421Number:
        decimal_text = self._normalize_decimal_text(value)
        bits: list[int] = []

        for symbol in decimal_text:
            bits.extend(DECIMAL_TO_BCD2421[int(symbol)])

        return Bcd2421Number(bits)

    def decode(self, number: Bcd2421Number) -> str:
        digits = [str(self.decode_tetrad(tetrad)) for tetrad in number.tetrads]
        return self._strip_leading_zeros("".join(digits))

    def encode_digit(self, digit: int) -> list[int]:
        self._validate_digit(digit)
        return DECIMAL_TO_BCD2421[digit][:]

    def decode_tetrad(self, tetrad: list[int]) -> int:
        tetrad_key = tuple(tetrad)

        if tetrad_key not in BCD2421_TO_DECIMAL:
            raise ValueError("Invalid BCD 2421 tetrad")

        return BCD2421_TO_DECIMAL[tetrad_key]

    def _normalize_decimal_text(self, value: str | int) -> str:
        decimal_text = str(value).strip()

        if decimal_text == "":
            raise ValueError("Decimal value must not be empty")

        if decimal_text.startswith("-"):
            raise ValueError("Negative numbers are not supported for BCD 2421")

        if not decimal_text.isdigit():
            raise ValueError("BCD 2421 codec supports only decimal digits")

        return self._strip_leading_zeros(decimal_text)

    def _strip_leading_zeros(self, decimal_text: str) -> str:
        stripped_text = decimal_text.lstrip("0")

        if stripped_text == "":
            return "0"

        return stripped_text

    def _validate_digit(self, digit: int) -> None:
        if digit not in DECIMAL_TO_BCD2421:
            raise ValueError("Decimal digit must be in range 0..9")
