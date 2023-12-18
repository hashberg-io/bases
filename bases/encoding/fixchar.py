"""
    Fixed-character base encodings, generalising those described by `rfc4648 <https://datatracker.ietf.org/doc/html/rfc4648.html>`_.

    Constructor options:

    - ``char_nbits: Union[int, Literal["auto"]]``, number of bits per character (default: ``"auto"``)
    - ``pad_char: Optional[str]``, optional padding character (default: :obj:`None`)
    - ``padding: PaddingOptions``, padding style (default: ``"ignore"``)

    If ``char_nbits`` is set to ``"auto"`` (by default), it is automatically computed as:

    .. code-block:: python

        int(math.ceil(math.log2(base)))

    From ``char_nbits``, size of a block (in bytes and chars) is computed as:

    .. code-block:: python

        block_nbytes = lcm(char_nbits, 8)//8
        block_nchars = lcm(char_nbits, 8)//char_nbits

    The value ``block_nbytes`` is presently not used, while the ``block_nchars`` is used for padding.

    The ``padding`` option must be set to ``"ignore"`` if a padding character is not specified (i.e. if ``pad_char`` is :obj:`None`).
    If a padding character is specified, it must be a character (string of length 1) not in the encoding alphabet:
    it is allowed in decoding strings, but only at then end (so that ``s.rstrip(pad_char)`` removes all padding).

    The padding behaviour is determined by the value of ``padding``:

    - ``"ignore"``: no padding included on encoding, no padding required on decoding
    - ``"include"``: padding included on encoding, no padding required on decoding
    - ``"require"``: padding included on encoding, padding required on decoding

    Encoding of a bytestring ``b``:

    1. compute the minimum number ``extra_nbits`` of additional bits necessary to make ``8*len(b)`` an integral multiple of ``char_nbits``
    2. convert ``b`` to an unsigned integer ``i`` (big-endian)
    3. left-shift ``i`` by ``extra_nbits`` bits, introducing the necessary zero *pad bits*
    4. converts ``i`` to the encoding base, using the encoding alphabet for digits
    5. if ``padding`` is ``"include"`` or ``"require"``, append the minimum number of padding characters necessary to make the encoded
       string length an integral multiple of ``block_nchars``

    Decoding of a string ``s``:

    1. if ``pad_char`` is not :obj:`None`, count the number N of contiguous padding characters at the end of ``s`` and strip them, obtaining ``s_stripped``
    2. if ``padding`` is ``"require"``, ensure that N is exactly the minimum number of padding characters that must be appended to ``s_stripped``
       to make its length an integral multiple of ``block_nchars``
    3. converts ``s`` to an unsigned integer ``i``, using the encoding alphabet for digits of the encoding base
    4. compute the number ``extra_nbits = (char_nbits*len(s))%8`` of pad bits: if this is not smaller than ``char_nbits``,
       raise `bases.encoding.errors.DecodingError`
    5. extract the value ``i%(2**extra_nbits)`` of the pad bits: if this is not zero, raise :class:`~bases.encoding.errors.DecodingError`
    6. compute the number of bytes in the decoded bytestring as ``original_nbytes = (char_nbits*len(s))//8``
    7. right-shift ``i`` by ``extra_nbits`` bits, removing the zero pad bits
    8. converts ``i`` to its minimal byte representation (big-endian), then zero-pad on the left to reach ``original_nbytes`` bytes
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Mapping, Optional, Union
from typing_extensions import Literal
from typing_validation import validate

from bases.alphabet import Alphabet
from .base import BaseEncoding, BytesLike
from .errors import DecodingError, InvalidDigitError, PaddingError

PaddingOptions = Literal["ignore", "include", "require"]
"""
    Type of allowed padding options for fixed-character encoding.
    See :attr:`FixcharBaseEncoding.padding`.
"""

def _lcm(a: int, b: int) -> int:
    # math.lcm only available in Python 3.8+
    return a*b//math.gcd(a, b)

class FixcharBaseEncoding(BaseEncoding):
    """
        Fixed-character encodings.

        :param alphabet: the alphabet to use for the encoding
        :type alphabet: :obj:`str`, :obj:`range` or :class:`~bases.alphabet.abstract.Alphabet`
        :param case_sensitive: optional case sensitivity (if :obj:`None`, the one from the alphabet is used)
        :type case_sensitive: :obj:`bool` or :obj:`None`, *optional*

        :param char_nbits: number of bits per character (default: ``"auto"``)
        :type char_nbits: :obj:`int` or ``"auto"``, *optional*
        :param pad_char: optional padding character (default: :obj:`None`)
        :type pad_char: :obj:`str` or :obj:`None`, *optional*
        :param padding: padding style (default: ``"ignore"``)
        :type padding: :obj:`PaddingOptions`, *optional*
    """

    _char_nbits: int
    _init_char_nbits: Union[int, Literal["auto"]]
    _pad_char: Optional[str] = None
    _padding: PaddingOptions = "ignore"
    _block_nbytes: int
    _block_nchars: int

    def __init__(self, alphabet: Union[str, range, Alphabet], *,
                 case_sensitive: Optional[bool] = None,
                 char_nbits: Union[int, Literal["auto"]] = "auto",
                 pad_char: Optional[str] = None,
                 padding: PaddingOptions = "ignore"):
        # pylint: disable = too-many-arguments
        validate(char_nbits, Union[int, Literal["auto"]])
        validate(pad_char, Optional[str])
        validate(padding, PaddingOptions)
        if padding not in ("ignore", "include", "require"):
            raise TypeError("Allowed padding options are: 'ignore', 'include' and 'require'.")
        super().__init__(alphabet, case_sensitive=case_sensitive)
        self._init_char_nbits = char_nbits
        if char_nbits == "auto":
            char_nbits = int(math.ceil(math.log2(self.base)))
        self._char_nbits = char_nbits
        self._pad_char = pad_char
        self._padding = padding
        self.__validate_init()
        l = _lcm(char_nbits, 8)
        self._block_nbytes = l//8
        self._block_nchars = l//char_nbits

    def __validate_init(self) -> None:
        alphabet = self.alphabet
        pad_char = self.pad_char
        if pad_char is None:
            if self.padding != "ignore":
                raise ValueError("If padding is not 'ignore', a padding character must be specified.")
        else:
            if len(pad_char) != 1:
                raise ValueError("If specified, padding character must have length 1.")
            if pad_char in alphabet:
                raise ValueError("Padding character cannot be in the alphabet.")
        char_nbits = self.char_nbits
        if char_nbits is not None:
            if char_nbits <= 0:
                raise ValueError("If specified, number of bits per character must be positive.")
            if 2**char_nbits < self.base:
                raise ValueError(f"Number of bits per character is insufficient to cover the whole alphabet. This is likely a mistake. "
                                 f"If it isn't, please truncate the alphabet to {2**char_nbits} characters (or less).")

    @property
    def char_nbits(self) -> int:
        """
            Number of bits per character.
        """
        return self._char_nbits

    @property
    def block_nchars(self) -> int:
        """
            Number of characters in a block.
        """
        return self._block_nchars

    @property
    def effective_base(self) -> int:
        """
            Effective base used when decoding is ``2**char_nbits``.
        """
        effective_base: int = 2**self.char_nbits
        return effective_base

    @property
    def padding(self) -> PaddingOptions:
        """
            Padding style:

            - ``"ignore"``: no padding included on encoding, no padding required on decoding
            - ``"include"``: padding included on encoding, no padding required on decoding
            - ``"require"``: padding included on encoding, padding required on decoding
        """
        return self._padding

    @property
    def include_padding(self) -> bool:
        """
            Whether padding is included on encoding (derived from :attr:`~FixcharBaseEncoding.padding`).
        """
        return self.padding in ("include", "require")

    @property
    def require_padding(self) -> bool:
        """
            Whether padding is required on decoding (derived from :attr:`~FixcharBaseEncoding.padding`).
        """
        return self.padding == "require"

    @property
    def pad_char(self) -> Optional[str]:
        """
            An optional character to be used for padding of encoded strings.
            In `rfc4648 <https://datatracker.ietf.org/doc/html/rfc4648.html>`_, this is ``"="`` for both base64 and base32.
        """
        return self._pad_char

    def pad(self, require: bool = False) -> "FixcharBaseEncoding":
        """
            Returns a copy of this encoding which includes paddding (and optionally requires it).

            Example usage, from ``"include"`` to ``"require"``:

            >>> encoding.base32
            FixcharBaseEncoding(
                StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                               case_sensitive=False),
                pad_char='=', padding='include')
            >>> encoding.base32.pad(require=True)
            FixcharBaseEncoding(
                StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                               case_sensitive=False),
                pad_char='=', padding='require')

            Example usage, from ``"ignore"`` to ``"include"``:

            >>> encoding.base32z
            FixcharBaseEncoding(
                StringAlphabet('ybndrfg8ejkmcpqxot1uwisza345h769',
                               case_sensitive=False))
            >>> encoding.base32z.with_pad_char("=")
            FixcharBaseEncoding(
                StringAlphabet('ybndrfg8ejkmcpqxot1uwisza345h769',
                               case_sensitive=False),
                pad_char='=')
            >>> encoding.base32z.with_pad_char("=").pad()
            FixcharBaseEncoding(
                StringAlphabet('ybndrfg8ejkmcpqxot1uwisza345h769',
                               case_sensitive=False),
                pad_char='=', padding='include')

            :param require: whether padding is to be required on decoding
            :type require: :obj:`bool`
        """
        validate(require, bool)
        options = {"padding": 'require' if require else 'include'}
        return self.with_options(**options)

    def nopad(self, allow: bool = True) -> "FixcharBaseEncoding":
        """
            Returns a copy of this encoding which does not include/require paddding
            (and optionally disallows it by removing the padding character).

            Example usage:

            >>> encoding.base32
            FixcharBaseEncoding(
                StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                               case_sensitive=False),
                pad_char='=', padding='include')
            >>> encoding.base32.nopad()
            FixcharBaseEncoding(
                StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                               case_sensitive=False),
                pad_char='=')
            >>> encoding.base32.nopad(allow=False)
            FixcharBaseEncoding(
                StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                               case_sensitive=False))

            :param allow: whether padding is to be allowed on decoding
            :type allow: :obj:`bool`
        """
        validate(allow, bool)
        options = {
            "padding": "ignore",
            "pad_char": self.pad_char if allow else None
        }
        return self.with_options(**options)

    def with_pad_char(self, pad_char: Optional[str]) -> "FixcharBaseEncoding":
        """
            Returns a copy of this encoding with a different padding character
            (or without a padding character if `pad_char` is `None`).

            Example usage:

            >>> encoding.base32
            FixcharBaseEncoding(
                StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                               case_sensitive=False),
                pad_char='=', padding='include')
            >>> encoding.base32.with_pad_char("~")
            FixcharBaseEncoding(
                StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                               case_sensitive=False),
                pad_char='~', padding='include')

            :param pad_char: padding character (default: :obj:`None`)
            :type pad_char: :obj:`str` or :obj:`None`
        """
        validate(pad_char, Optional[str])
        options: Dict[str, Any] = {"pad_char": pad_char}
        if pad_char is None:
            options["padding"] = "ignore"
        return self.with_options(**options)

    def pad_string(self, s: str) -> str:
        """
            If no padding character is specified for this encoding, returns the input string unchanged.
            If a padding character is specified for this encoding, pads the input string by appending the
            minimum number of padding characters necessary to make its length an integral multiple of the
            block char size (given by :attr:`~FixcharBaseEncoding.block_nchars`).

            The value of :attr:`~FixcharBaseEncoding.padding` is irrelevant to this method.

            :param s: the string
            :type s: :obj:`str`
        """
        validate(s, str)
        pad_char = self.pad_char
        block_nchars = self._block_nchars
        # no padding available for this encoding scheme
        if pad_char is None:
            return s
        # padding available, but no need for padding
        if len(s)%block_nchars == 0:
            return s
        # compute require padding length
        pad_len = block_nchars-(len(s)%block_nchars)
        # return padded string
        return s+pad_char*pad_len

    def strip_string(self, s: str) -> str:
        """
            If no padding character is specified for this encoding, returns the input string unchanged.
            If a padding character is specified for this encoding, strips the input string of any padding
            characters it might have to the right.
            If :attr:`~FixcharBaseEncoding.padding` is set to ``"require"``, checks that the correct number of
            padding characters were included and raises :class:`~bases.encoding.errors.PaddingError` if not.

            :param s: the string
            :type s: :obj:`str`
        """
        validate(s, str)
        pad_char = self.pad_char
        case_sensitive = self.case_sensitive
        block_nchars = self._block_nchars
        # no padding available for this encoding scheme
        if pad_char is None:
            return s
        # padding character(s) to strip from the right of the string
        pad_chars = pad_char
        if not case_sensitive:
            pad_chars += pad_char.lower()+pad_char.upper()
        # strip padding from string
        s_stripped = s.rstrip(pad_chars)
        # if padding is required on decoding, check the correct amount was included
        if self.require_padding:
            padding = len(s)-len(s_stripped)
            extra_nchars = len(s_stripped)%block_nchars
            expected_padding = 0 if extra_nchars == 0 else block_nchars-extra_nchars
            if padding != expected_padding:
                raise PaddingError(padding, expected_padding)
        return s_stripped

    def canonical_bytes(self, b: BytesLike) -> bytes:
        self._validate_bytes(b)
        return bytes(b)

    def canonical_string(self, s: str) -> str:
        validate(s, str)
        if self.include_padding:
            return self.pad_string(s)
        return self.strip_string(s)

    def _validate_string(self, s: str) -> str:
        s = self.strip_string(s)
        return super()._validate_string(s)

    def _encode(self, b: memoryview) -> str:
        alphabet = self.alphabet
        base = self.base
        char_nbits = self.char_nbits
        effective_base = self.effective_base
        # bytes as unsigned integer
        i = int.from_bytes(b, byteorder="big")
        # add padding bits (align to integral number of characters)
        nchars, extra_nbits = divmod((8*len(b)), char_nbits)
        if extra_nbits > 0:
            i <<= char_nbits-extra_nbits # pad bits set to 0
            nchars += 1
        # compute characters in reverse order
        revchars: List[str] = []
        for _ in range(nchars):
            # extract next digit by consuming rightmost char_nbits
            # Same as: d = i % (2**char_nbits); i >>= char_nbits
            i, d = divmod(i, effective_base)
            # ensure digit is valid for actual base (number of characters in the alphabet)
            if not d < base:
                raise InvalidDigitError(d, base)
            # add the next character to the list
            revchars.append(alphabet[d])
        # join characters, pad string (if padding is to be included) and return
        s = "".join(reversed(revchars))
        if not self.include_padding:
            return s
        return self.pad_string(s)

    def _decode(self, s: str) -> bytes:
        base = self.base
        char_nbits = self.char_nbits
        alphabet_revdir = self.alphabet.revdir
        # decode string into unsigned integer
        i = 0
        for c in s:
            d = alphabet_revdir[c]
            i = i*base + d
        # remove padding bits (ensure that there are not too many and that they are all set to zero)
        original_nbytes, extra_nbits = divmod((char_nbits*len(s)), 8)
        if extra_nbits >= char_nbits:
            raise DecodingError(f"More pad bits found ({extra_nbits}) than bits per character ({char_nbits}).")
        if extra_nbits > 0:
            i, pad_bits = divmod(i, 2**extra_nbits)
            if pad_bits != 0:
                raise DecodingError("Pad bits must be zero.")
        # convert unsigned integer into the required number of bytes (zero-pad to the left)
        return i.to_bytes(length=original_nbytes, byteorder="big")

    def options(self, skip_defaults: bool = False) -> Mapping[str, Any]:
        validate(skip_defaults, bool)
        options: Dict[str, Any] = {}
        if not skip_defaults or self._init_char_nbits != "auto":
            options["char_nbits"] = self._init_char_nbits
        if not skip_defaults or self.pad_char is not None:
            options["pad_char"] = self.pad_char
        if not skip_defaults or self.padding != "ignore":
            options["padding"] = self.padding
        return options
