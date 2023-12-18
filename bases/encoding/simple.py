"""
    Simple base encodings.

    Encoding of a bytestring ``b``:

    1. if ``b`` contains any leading zero bytes, raises :class:`~bases.encoding.errors.EncodingError`
    2. converts ``b`` to an unsigned integer ``i`` (big-endian)
    3. converts ``i`` to the encoding base, using the encoding alphabet for digits

    Decoding of a string ``s``:

    1. if ``s`` contains any leading zero characters, raises :class:`~bases.encoding.errors.DecodingError`
    2. converts ``s`` to an unsigned integer ``i``, using the encoding alphabet for digits of the encoding base
    3. converts ``i`` to its minimal byte representation (big-endian)
"""

from __future__ import annotations

from typing import Any, List, Mapping, Optional, Union
from typing_validation import validate

from bases.alphabet import Alphabet
from .base import BaseEncoding, BytesLike
from .errors import EncodingError, DecodingError

class SimpleBaseEncoding(BaseEncoding):
    """
        Simple base encodings.

        :param alphabet: the alphabet to use for the encoding
        :type alphabet: :obj:`str`, :obj:`range` or :class:`~bases.alphabet.abstract.Alphabet`
        :param case_sensitive: optional case sensitivity (if :obj:`None`, the one from the alphabet is used)
        :type case_sensitive: :obj:`bool` or :obj:`None`, *optional*
    """

    def __init__(self, alphabet: Union[str, range, Alphabet], *,
                 case_sensitive: Optional[bool] = None):
        super().__init__(alphabet, case_sensitive=case_sensitive)

    def canonical_bytes(self, b: BytesLike) -> bytes:
        self._validate_bytes(b)
        return bytes(b)

    def canonical_string(self, s: str) -> str:
        self._validate_string(s)
        return s

    def _validate_bytes(self, b: BytesLike) -> memoryview:
        b = super()._validate_bytes(b)
        if len(b) > 0 and b[0] == 0:
            raise EncodingError("Bytestrings cannot have leading zero bytes.")
        return b

    def _validate_string(self, s: str) -> str:
        s = super()._validate_string(s)
        if s.startswith(self.zero_char):
            raise DecodingError("Strings cannot have leading zero characters.")
        return s

    def _encode(self, b: memoryview) -> str:
        alphabet = self.alphabet
        base = self.base
        # turn bytes into integer
        i = int.from_bytes(b, byteorder="big")
        # compute encoded string chars in reversed order
        revchars: List[str] = []
        while i > 0:
            i, d = divmod(i, base)
            revchars.append(alphabet[d])
        # return encoded string
        return "".join(reversed(revchars))

    def _decode(self, s: str) -> bytes:
        alphabet_revdir = self.alphabet.revdir
        base = self.base
        # turn chars in to integer
        i = 0
        for c in s:
            d = alphabet_revdir[c]
            i = i*base + d
        # compute minimum number of bytes to represent integer
        bitlen = i.bit_length()
        nbytes = bitlen//8 if bitlen%8==0 else 1+bitlen//8
        # return decoded bytes
        return i.to_bytes(length=nbytes, byteorder="big")

    def options(self, skip_defaults: bool = False) -> Mapping[str, Any]:
        validate(skip_defaults, bool)
        return {}
