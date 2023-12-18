"""
    Encoding error classes.
"""

from __future__ import annotations

import binascii
from typing_validation import validate

from bases.alphabet import Alphabet

class Error(binascii.Error):
    """
        Generic encoding or decoding error.
    """

class EncodingError(Error):
    """
        Generic encoding error.
    """

class InvalidDigitError(EncodingError):
    """
        Encoding error raised when a digit does not index a character
        in the given alphabet (because ``not 0 <= digit < len(alphabet)``)
    """

    digit: int
    base: int

    def __init__(self, digit: int, base: int) -> None:
        validate(digit, int)
        validate(base, int)
        self.digit = digit
        self.base = base
        if 0 <= digit < base:
            raise ValueError(f"Digit {digit} is valid for base {base}.")
        error_msg = f"Invalid digit {digit} encountered for base {base}."
        super().__init__(error_msg)

class InvalidByteBlockError(EncodingError):
    """
        Encoding error raised by block encodings when a byte block is invalid.
    """

class DecodingError(Error):
    """
        Generic decoding error.
    """

class NonAlphabeticCharError(DecodingError):
    """
        Decoding error raised when a character is not in the given alphabet,
        (considering case-insensitivity of the alphabet, if relevant).
    """

    char: str
    alphabet: Alphabet

    def __init__(self, char: str, alphabet: Alphabet) -> None:
        validate(char, str)
        validate(alphabet, Alphabet)
        self.char = char
        self.alphabet = alphabet
        if char in alphabet:
            raise ValueError(f"Character {repr(char)} is alphabetic.")
        error_msg = f"Invalid character {repr(char)} encountered for alphabet {str(alphabet)}."
        super().__init__(error_msg)

class PaddingError(DecodingError):
    """
        Decoding error raised when a string to be decoded has incorrect padding.
    """

    padding: int
    expected_padding: int

    def __init__(self, padding: int, expected_padding: int) -> None:
        validate(padding, int)
        validate(expected_padding, int)
        self.padding = padding
        self.expected_padding = expected_padding
        if padding < expected_padding:
            error_msg = f"Insufficient padding: found {padding}, expected {expected_padding}"
        elif padding > expected_padding:
            error_msg = f"Excessive padding: found {padding}, expected {expected_padding}"
        else:
            raise ValueError("Padding is exactly what was expected.")
        super().__init__(error_msg)

class InvalidCharBlockError(DecodingError):
    """
        Decoding error raised by block encodings when a char block is invalid.
    """
