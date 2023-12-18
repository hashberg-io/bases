"""
    Abstract base encodings.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional, TypeVar, Union
from typing_extensions import Final
from typing_validation import validate

from bases.alphabet import Alphabet
from bases.alphabet import make as alphabet_make
from .errors import NonAlphabeticCharError

BytesLike = Union[bytes, bytearray, memoryview]
""" Type alias for bytes-like objects. """

byteslike: Final = (bytes, bytearray, memoryview)
""" Tuple of bytes-like objects types (for use with :obj:`isinstance` checks). """

BaseEncodingSubclass = TypeVar("BaseEncodingSubclass", bound="BaseEncoding")
""" Type variable for subclasses of :class:`BaseEncoding`. """

class BaseEncoding(ABC):
    """
        Abstract superclass for base encodings.
        Instances can always be constructed from an alphabet (with optional change of case sensitivity)
        and a number of additional options specified by subclasses.

        :param alphabet: the alphabet to use for the encoding
        :type alphabet: :obj:`str`, :obj:`range` or :class:`~bases.alphabet.abstract.Alphabet`
        :param case_sensitive: optional case sensitivity (if :obj:`None`, the one from the alphabet is used)
        :type case_sensitive: :obj:`bool` or :obj:`None`, *optional*
    """

    _alphabet: Alphabet
    _alphabet_revdir: Mapping[str, int]
    _case_sensitive: bool

    def __init__(self, alphabet: Union[str, range, Alphabet], *,
                 case_sensitive: Optional[bool] = None):
        validate(alphabet, Union[str, range, Alphabet])
        validate(case_sensitive, Optional[bool])
        if isinstance(alphabet, Alphabet):
            if case_sensitive is not None:
                alphabet = alphabet.with_case_sensitivity(case_sensitive)
            self._alphabet = alphabet
        else:
            if case_sensitive is None:
                case_sensitive = True
            self._alphabet = alphabet_make(alphabet, case_sensitive=case_sensitive)

    @property
    def alphabet(self) -> Alphabet:
        """
            The encoding alphabet.

            Example usage:

            >>> encoding.base32.alphabet
            StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                           case_sensitive=False)

        """
        return self._alphabet

    @property
    def base(self) -> int:
        """
            The base for this encoding (the length of the alphabet).

            Example usage:

            >>> encoding.base32.base
            32

        """
        return len(self.alphabet)

    @property
    def case_sensitive(self) -> bool:
        """
            Determines whether the decoder is case sensitive.

            Example usage:

            >>> encoding.base32.case_sensitive
            False

        """
        return self.alphabet.case_sensitive

    @property
    def zero_char(self) -> str:
        """
            The zero digit for this encoding (first character in the alphabet).

            Example usage:

            >>> encoding.base32.alphabet
            StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                           case_sensitive=False)
            >>> encoding.base32.zero_char
            'A'

        """
        return self.alphabet[0]

    def with_alphabet(self: BaseEncodingSubclass, alphabet: Union[str, range, Alphabet], *,
                      case_sensitive: Optional[bool] = None) -> BaseEncodingSubclass:
        """
            Returns a new encoding with the same kind and options as this one,
            but a different alphabet and/or case sensitivity.

            :param alphabet: the alphabet to use for the encoding
            :type alphabet: :obj:`str`, :obj:`range` or :class:`~bases.alphabet.abstract.Alphabet`
            :param case_sensitive: optional case sensitivity (if :obj:`None`, the one from the alphabet is used)
            :type case_sensitive: :obj:`bool` or :obj:`None`, *optional*

            :rtype: :obj:`BaseEncodingSubclass`
        """
        validate(alphabet, Union[str, range, Alphabet])
        validate(case_sensitive, Optional[bool])
        options = {**self.options()}
        options["case_sensitive"] = case_sensitive
        return type(self)(alphabet, **options)

    def with_case_sensitivity(self: BaseEncodingSubclass, case_sensitive: bool) -> BaseEncodingSubclass:
        """
            Returns a new encoding with the same characters as this one but with specified case sensitivity.

            Example usage:

            >>> encoding.base32
            FixcharBaseEncoding(
                StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                               case_sensitive=False),
                pad_char='=', padding='include')
            >>> encoding.base32.with_case_sensitivity(True)
            FixcharBaseEncoding(
                StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'),
                pad_char='=', padding='include')

            :param case_sensitive: case sensitivity for the new encoding
            :type case_sensitive: :obj:`bool`
            :rtype: :obj:`BaseEncodingSubclass`
        """
        validate(case_sensitive, bool)
        return self.with_alphabet(self.alphabet.with_case_sensitivity(case_sensitive))

    def upper(self: BaseEncodingSubclass) -> BaseEncodingSubclass:
        """
            Returns a new encoding with all cased characters turned to uppercase.

            Example usage:

            >>> encoding.base32z
            FixcharBaseEncoding(
                StringAlphabet('ybndrfg8ejkmcpqxot1uwisza345h769',
                               case_sensitive=False))
            >>> encoding.base32z.upper()
            FixcharBaseEncoding(
                StringAlphabet('YBNDRFG8EJKMCPQXOT1UWISZA345H769',
                               case_sensitive=False))

            :rtype: :obj:`BaseEncodingSubclass`

        """
        return self.with_alphabet(self.alphabet.upper())

    def lower(self: BaseEncodingSubclass) -> BaseEncodingSubclass:
        """
            Returns a new encoding with all cased characters turned to lowercase.

            Example usage:

            >>> encoding.base32
            FixcharBaseEncoding(
                StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                               case_sensitive=False),
                pad_char='=', padding='include')
            >>> encoding.base32.lower()
            FixcharBaseEncoding(
                StringAlphabet('abcdefghijklmnopqrstuvwxyz234567',
                               case_sensitive=False),
                pad_char='=', padding='include')

            :rtype: :obj:`BaseEncodingSubclass`

        """
        return self.with_alphabet(self.alphabet.lower())

    def with_options(self: BaseEncodingSubclass, **options: Any) -> BaseEncodingSubclass:
        r"""
            Returns a new encoding with the same kind, alphabet and case sensitivity as this one,
            but different options.


            :param options: options to set for the new encoding
            :type options: :obj:`~typing.Dict`\ [:obj:`str`, :obj:`~typing.Any`]

            :rtype: :obj:`BaseEncodingSubclass`
        """
        new_options = {**self.options()}
        for name in options:
            if name not in new_options:
                raise KeyError(f"Unknown option {repr(name)} for {type(self).__name__}")
        new_options.update(options)
        return type(self)(self.alphabet, **new_options)

    def encode(self, b: BytesLike) -> str:
        """
            Encodes a bytestring into a string.

            Example usage:

            >>> b = bytes([70, 98, 190, 187, 66, 224, 178])
            >>> encoding.base32.encode(b)
            'IZRL5O2C4CZA===='
            >>> s = 'IZRL5O2C4CZA===='
            >>> list(base32.decode(s))
            [70, 98, 190, 187, 66, 224, 178]

            :param b: the bytestring
            :type b: :obj:`BytesLike`

            :raises ~bases.encoding.errors.EncodingError: if the bytestring is invalid
        """
        b = self._validate_bytes(b)
        return self._encode(b)

    def decode(self, s: str) -> bytes:
        """
            Decodes a string into a bytestring.

            Example usage:

            >>> s = 'IZRL5O2C4CZA===='
            >>> list(encoding.base32.decode(s))
            [70, 98, 190, 187, 66, 224, 178]

            :param s: the string
            :type s: :obj:`str`

            :raises ~bases.encoding.errors.DecodingError: if the string is invalid

        """
        s = self._validate_string(s)
        return self._decode(s)

    def canonical_bytes(self, b: BytesLike) -> bytes:
        """
            Returns a canonical version of the bytestring ``b``:
            this is the bytestring obtained by first encoding ``b``
            and then decoding it.

            (This method is overridden by subclasses with more efficient implementations.)

            :param b: the bytestring
            :type b: :obj:`BytesLike`
        """
        return self.decode(self.encode(b))

    def canonical_string(self, s: str) -> str:
        """
            Returns a canonical version of the string ``s``:
            this is the string obtained by first decoding ``s``
            and then encoding it.

            (This method is overridden by subclasses with more efficient implementations.)

            :param s: the string
            :type s: :obj:`str`
        """
        return self.encode(self.decode(s))

    def _validate_bytes(self, b: BytesLike) -> memoryview:
        validate(b, BytesLike)
        return memoryview(b)

    def _validate_string(self, s: str) -> str:
        validate(s, str)
        alphabet = self.alphabet
        for c in s:
            if c not in alphabet:
                raise NonAlphabeticCharError(c, alphabet)
        return s

    @abstractmethod
    def _encode(self, b: memoryview) -> str:
        ...

    @abstractmethod
    def _decode(self, s: str) -> bytes:
        ...

    @abstractmethod
    def options(self, skip_defaults: bool = False) -> Mapping[str, Any]:
        """
            The options used to construct this particular encoding.

            Example usage:

            >>> encoding.base32.options()
            {'char_nbits': 'auto', 'pad_char': '=', 'padding': 'include'}
            >>> encoding.base32.options(skip_defaults=True)
            {'pad_char': '=', 'padding': 'include'}

            :param skip_defaults: if set to :obj:`True`, only options with non-default values are included in the mapping
            :type skip_defaults: :obj:`bool`, *optional*

        """

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, BaseEncoding):
            return NotImplemented
        if type(self) != type(other): # pylint: disable = unidiomatic-typecheck
            return NotImplemented
        return self.options() == other.options()

    def __hash__(self) -> int:
        return hash((type(self), self.alphabet, tuple(self.options().items())))

    def __repr__(self) -> str:
        type_name = type(self).__name__
        alphabet_str = repr(self.alphabet)
        options = self.options(skip_defaults=True)
        if not options:
            return f"{type_name}({alphabet_str})"
        options_str = ", ".join(f"{name}={repr(value)}" for name, value in options.items())
        return f"{type_name}({alphabet_str}, {options_str})"

def lstrip_memview(b: memoryview, byte: int = 0) -> memoryview:
    r"""
        Returns a new memoryview obtained by slicing away all leading zero bytes
        from the given memoryview ``b``.

        Example usage:

        >>> b = bytes([0, 0, 1, 0, 2, 0, 3, 0, 0])
        >>> b
        b'\x00\x00\x01\x00\x02\x00\x03\x00\x00'
        >>> m = memview(b)
        >>> m
        <memory at 0x0000024A3AB9EB80>
        >>> bytes(m)
        b'\x00\x00\x01\x00\x02\x00\x03\x00\x00'
        >>> ms = lstrip_memview(m)
        >>> ms
        <memory at 0x0000024A3AB9EC40>
        >>> bytes(ms)
        b'\x01\x00\x02\x00\x03\x00\x00'

        :param b: the memoryview from which to strip leading zero bytes
        :type b: :obj:`memoryview`
        :param byte: optionally, a leading byte value to strip instead of zero
        :type byte: :obj:`int`, *optional*

        :raises ValueError: if ``byte not in range(256)``

    """
    validate(b, memoryview)
    if byte != 0:
        validate(byte, int)
        if byte not in range(256):
            raise ValueError(f"Byte values must be in range(256), found {byte}.")
    return _lstrip_memview(b, byte)

def _lstrip_memview(b: memoryview, byte: int = 0) -> memoryview:
    idx = 0
    l = len(b)
    while idx < l and b[idx] == byte:
        idx += 1
    return b[idx:]
