"""
    Abstract base encodings.
"""

from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional, TypeVar, Union

from bases import alphabet
from bases.alphabet import Alphabet
from .errors import NonAlphabeticCharError

Self = TypeVar("Self", bound="BaseEncoding")

class BaseEncoding(ABC):
    """
        Abstract superclass for base encodings.
        Instances can always be constructed from an alphabet (with optional change of case sensitivity)
        and a number of additional options specified by subclasses.
    """

    _alphabet: Alphabet
    _alphabet_revdir: Mapping[str, int]
    _case_sensitive: bool

    def __init__(self, chars: Union[str, range, Alphabet], *,
                 case_sensitive: Optional[bool] = None):
        if isinstance(chars, Alphabet):
            if case_sensitive is not None:
                chars = chars.with_case_sensitivity(case_sensitive)
            self._alphabet = chars
        else:
            if case_sensitive is None:
                case_sensitive = True
            self._alphabet = alphabet.make(chars, case_sensitive=case_sensitive)

    @property
    def alphabet(self) -> Alphabet:
        """
            The encoding alphabet.

            Example usage:

            ```py
            >>> encoding.base32.alphabet
            StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                           case_sensitive=False)
            ```
        """
        return self._alphabet

    @property
    def base(self) -> int:
        """
            The base for this encoding (the length of the alphabet).

            Example usage:

            ```py
            >>> encoding.base32.base
            32
            ```
        """
        return len(self.alphabet)

    @property
    def case_sensitive(self) -> bool:
        """
            Determines whether the decoder is case sensitive.

            Example usage:

            ```py
            >>> encoding.base32.case_sensitive
            False
            ```
        """
        return self.alphabet.case_sensitive

    @property
    def zero_char(self) -> str:
        """
            The zero digit for this encoding (first character in the alphabet).

            Example usage:

            ```py
            >>> encoding.base32.alphabet
            StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                           case_sensitive=False)
            >>> encoding.base32.zero_char
            'A'
            ```
        """
        return self.alphabet[0]

    def with_alphabet(self: Self, chars: Union[str, range, Alphabet], *,
                      case_sensitive: Optional[bool] = None) -> Self:
        """
            Returns a new encoding with the same kind and options as this one,
            but a different alphabet and/or case sensitivity.
        """
        options = {**self.options()}
        options["case_sensitive"] = case_sensitive
        return type(self)(chars, **options)

    def with_case_sensitivity(self: Self, case_sensitive: bool) -> Self:
        """
            Returns a new encoding with the same characters as this one but with specified case sensitivity.

            Example usage:

            ```py
            >>> encoding.base32
            FixcharBaseEncoding(
                StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                               case_sensitive=False),
                pad_char='=', padding='include')
            >>> encoding.base32.with_case_sensitivity(True)
            FixcharBaseEncoding(
                StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'),
                pad_char='=', padding='include')
            ```
        """
        return self.with_alphabet(self.alphabet.with_case_sensitivity(case_sensitive))

    def upper(self: Self) -> Self:
        """
            Returns a new encoding with all cased characters turned to uppercase.

            Example usage:

            ```py
            >>> encoding.base32z
            FixcharBaseEncoding(
                StringAlphabet('ybndrfg8ejkmcpqxot1uwisza345h769',
                               case_sensitive=False))
            >>> encoding.base32z.upper()
            FixcharBaseEncoding(
                StringAlphabet('YBNDRFG8EJKMCPQXOT1UWISZA345H769',
                               case_sensitive=False))
            ```
        """
        return self.with_alphabet(self.alphabet.upper())

    def lower(self: Self) -> Self:
        """
            Returns a new encoding with all cased characters turned to lowercase.

            Example usage:

            ```py
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
            ```
        """
        return self.with_alphabet(self.alphabet.lower())

    def with_options(self: Self, **options: Any) -> Self:
        """
            Returns a new encoding with the same kind, alphabet and case sensitivity as this one,
            but different options.
        """
        new_options = {**self.options()}
        for name in options:
            if name not in new_options:
                raise KeyError(f"Unknown option {repr(name)} for {type(self).__name__}")
        new_options.update(options)
        return type(self)(self.alphabet, **new_options)

    def encode(self, b: bytes) -> str:
        """
            Encodes a bytestring into a string.
            Raises `bases.encoding.errors.EncodingError`
            if the bytestring is invalid.

            Example usage:

            ```py
            >>> b = bytes([70, 98, 190, 187, 66, 224, 178])
            >>> encoding.base32.encode(b)
            'IZRL5O2C4CZA===='
            >>> s = 'IZRL5O2C4CZA===='
            >>> list(base32.decode(s))
            [70, 98, 190, 187, 66, 224, 178]
            ```
        """
        b = self._validate_bytes(b)
        return self._encode(b)

    def decode(self, s: str) -> bytes:
        """
            Decodes a string into a bytestring.
            Raises `bases.encoding.errors.DecodingError`
            if the string is invalid.

            Example usage:

            ```py
            >>> s = 'IZRL5O2C4CZA===='
            >>> list(encoding.base32.decode(s))
            [70, 98, 190, 187, 66, 224, 178]
            ```
        """
        s = self._validate_string(s)
        return self._decode(s)

    def canonical_bytes(self, b: bytes) -> bytes:
        """
            Returns a canonical version of the bytestring `b`:
            this is the bytestring obtained by first encoding `b`
            and then decoding it.

            (This method is overridden by subclasses with more efficient implementations.)
        """
        return self.decode(self.encode(b))

    def canonical_string(self, s: str) -> str:
        """
            Returns a canonical version of the string `s`:
            this is the string obtained by first decoding `s`
            and then encoding it.

            (This method is overridden by subclasses with more efficient implementations.)
        """
        return self.encode(self.decode(s))

    def _validate_bytes(self, b: bytes) -> bytes:
        # pylint: disable = no-self-use
        if not isinstance(b, bytes):
            raise TypeError()
        return b

    def _validate_string(self, s: str) -> str:
        if not isinstance(s, str):
            raise TypeError()
        alphabet = self.alphabet
        for c in s:
            if c not in alphabet:
                raise NonAlphabeticCharError(c, alphabet)
        return s

    @abstractmethod
    def _encode(self, b: bytes) -> str:
        ...

    @abstractmethod
    def _decode(self, s: str) -> bytes:
        ...

    @abstractmethod
    def options(self, skip_defaults: bool = False) -> Mapping[str, Any]:
        """
            The options used to construct this particular encoding.
            If `skip_defaults` is `True`, only options with non-default values
            are included in the mapping.

            Example usage:

            ```py
            >>> encoding.base32.options()
            {'char_nbits': 'auto', 'pad_char': '=', 'padding': 'include'}
            >>> encoding.base32.options(skip_defaults=True)
            {'pad_char': '=', 'padding': 'include'}
            ```
        """
        ...

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
