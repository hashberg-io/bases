"""
    Alphabets explicitly specified by strings.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Any, Mapping, overload, Union
from typing_validation import validate

from .abstract import Alphabet

class StringAlphabet(Alphabet):
    """
        Class for alphabets explicitly specified by a string of (unique) characters
        and optional case sensitivity (default: case-sensitive).

        Example usage:

        >>> from bases.alphabet import StringAlphabet
        >>> StringAlphabet("0123456789abcdef", case_sensitive=False)
        StringAlphabet('0123456789abcdef', case_sensitive=False)
        >>> StringAlphabet("0123").case_sensitive
        True

        :param chars: a string excplicitly listing all characters in the alphabet
        :type chars: :obj:`str`
        :param case_sensitive: whether the alphabet is case-sensitive
        :type case_sensitive: :obj:`bool`, *optional*

        :raises ValueError: if the alphabet contains fewer than 2 characters
        :raises ValueError: if ``chars`` contains repeated characters
        :raises ValueError: if the alphabet is case-insensitive and it contains both uppercase and lowercase versions of the same character

    """

    _chars: str
    _revdir: Mapping[str, int]
    _case_sensitive: bool

    def __init__(self, chars: str, *,
                 case_sensitive: bool = True):
        super().__init__(case_sensitive)
        validate(chars, str)
        self._chars = chars
        revdir = {
            c: idx for idx, c in enumerate(chars)
        }
        if not case_sensitive:
            revdir.update({
                c.upper(): idx for idx, c in enumerate(chars)
            })
            revdir.update({
                c.lower(): idx for idx, c in enumerate(chars)
            })
        self._revdir = MappingProxyType(revdir)
        self.__validate_init()

    def __validate_init(self) -> None:
        chars = self._chars
        case_sensitive = self.case_sensitive
        if len(chars) <= 1:
            raise ValueError("Alphabet must have at least two characters.")
        if len(chars) != len(set(chars)):
            raise ValueError("Alphabet cannot contain repeated characters.")
        if not case_sensitive:
            chars_set_upper = {c.upper() for c in chars}
            chars_set_lower = {c.lower() for c in chars}
            if len(chars_set_upper) != len(chars) or len(chars_set_lower) != len(chars):
                raise ValueError("Alphabet contains lowercase and uppercase versions of the same character, "
                                 "encoding must be case-sensitive.")

    @property
    def chars(self) -> str:
        """
            The characters that define this alphabet.

            Example usage:

            >>> alphabet.base16.chars
            '0123456789ABCDEF'

        """
        return self._chars

    @property
    def revdir(self) -> Mapping[str, int]:
        return self._revdir

    def __len__(self) -> int:
        return len(self._chars)

    @overload
    def __getitem__(self, idx: int) -> str:
        ...

    @overload
    def __getitem__(self, idx: slice) -> "StringAlphabet":
        ...

    def __getitem__(self, idx: Union[int, slice]) -> Union[str, "StringAlphabet"]:
        validate(idx, Union[int, slice])
        if isinstance(idx, slice):
            new_chars = self._chars[idx]
            return StringAlphabet(new_chars, case_sensitive=self.case_sensitive)
        return self._chars[idx]

    def with_case_sensitivity(self, case_sensitive: bool) -> "StringAlphabet":
        validate(case_sensitive, bool)
        if case_sensitive == self.case_sensitive:
            return self
        return StringAlphabet(self.chars, case_sensitive=case_sensitive)

    def upper(self) -> "StringAlphabet":
        chars = self.chars.upper()
        if chars == self.chars:
            return self
        return StringAlphabet(chars, case_sensitive=self.case_sensitive)

    def lower(self) -> "StringAlphabet":
        chars = self.chars.lower()
        if chars == self.chars:
            return self
        return StringAlphabet(chars, case_sensitive=self.case_sensitive)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, StringAlphabet):
            return NotImplemented
        return self.chars == other.chars and self.case_sensitive == other.case_sensitive

    def __hash__(self) -> int:
        return hash((type(self), self.chars, self.case_sensitive))

    def __repr__(self) -> str:
        chars_str = repr(self.chars)
        if self.case_sensitive:
            return f"StringAlphabet({chars_str})"
        case_sensitive_str = f"case_sensitive={self.case_sensitive}"
        return f"StringAlphabet({chars_str}, {case_sensitive_str})"
