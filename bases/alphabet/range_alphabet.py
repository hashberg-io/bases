"""
    Alphabets implicitly specified by Unicode codepoint range.
"""

from __future__ import annotations

from typing import Any, Iterator, Mapping, overload, Union
from typing_validation import validate

from .abstract import Alphabet
from .string_alphabet import StringAlphabet

class RangeAlphabet(Alphabet):
    """
        Class for alphabets implicitly specified by a range of Unicode codepoints
        and optional case sensitivity (default: case-sensitive).

        Example usage:

        >>> from bases.alphabet import RangeAlphabet
        >>> RangeAlphabet(range(0x00, 0x100))
        RangeAlphabet(range(0x0, 0x100))

        :param codepoints: a range of unicode codepoints for the alphabet
        :type codepoints: :obj:`range`
        :param case_sensitive: whether the alphabet is case-sensitive
        :type case_sensitive: :obj:`bool`, *optional*

        :raises ValueError: if the range is shorter than 2 integers
        :raises ValueError: if the alphabet is case-insensitive and it contains both uppercase and lowercase versions of the same character

    """

    _codepoints: range
    _revdir: Mapping[str, int]
    _case_sensitive: bool

    def __init__(self, codepoints: range, *,
                 case_sensitive: bool = True):
        super().__init__(case_sensitive)
        validate(codepoints, range)
        self._codepoints = codepoints
        self._revdir = _RangeAlphabetRevdir(self)
        self.__validate_init()

    def __validate_init(self) -> None:
        codepoints = self._codepoints
        case_sensitive = self.case_sensitive
        if len(codepoints) <= 1:
            raise ValueError("Alphabet must have at least two characters.")
        if not case_sensitive:
            codepoints_set = set(codepoints)
            for i in codepoints:
                c = chr(i)
                if ord(c.upper()) in codepoints_set and ord(c.lower()) in codepoints_set:
                    raise ValueError("Alphabet contains lowercase and uppercase versions of the same character, "
                                     "encoding must be case-sensitive.")

    @property
    def codepoints(self) -> range:
        """
            The codepoint range that defines this alphabet.

            Example usage:

            >>> RangeAlphabet(range(0x00, 0x100)).codepoints
            range(0, 256)

        """
        return self._codepoints

    @property
    def revdir(self) -> Mapping[str, int]:
        return self._revdir

    def __len__(self) -> int:
        return len(self._codepoints)

    @overload
    def __getitem__(self, idx: int) -> str:
        ...

    @overload
    def __getitem__(self, idx: slice) -> "RangeAlphabet":
        ...

    def __getitem__(self, idx: Union[int, slice]) -> Union[str, "RangeAlphabet"]:
        validate(idx, Union[int, slice])
        if isinstance(idx, slice):
            new_codepoints = self._codepoints[idx]
            return RangeAlphabet(new_codepoints, case_sensitive=self.case_sensitive)
        return chr(self._codepoints[idx])

    def with_case_sensitivity(self, case_sensitive: bool) -> "RangeAlphabet":
        validate(case_sensitive, bool)
        if case_sensitive == self.case_sensitive:
            return self
        return RangeAlphabet(self.codepoints, case_sensitive=case_sensitive)

    def as_string_alphabet(self) -> StringAlphabet:
        """
            Converts this alphabet into a string alphabet explicitly defined
            by the string containing all characters in the codepoint range.

            Example usage:

            >>> RangeAlphabet(range(0x20, 0x7E)).as_string_alphabet()
            StringAlphabet(' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMN
                            OPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}')

        """
        chars = "".join(self)
        return StringAlphabet(chars, case_sensitive=self.case_sensitive)

    def upper(self) -> StringAlphabet:
        chars = "".join(self).upper()
        return StringAlphabet(chars, case_sensitive=self.case_sensitive)

    def lower(self) -> StringAlphabet:
        chars = "".join(self).lower()
        return StringAlphabet(chars, case_sensitive=self.case_sensitive)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, RangeAlphabet):
            return NotImplemented
        return self.codepoints == other.codepoints and self.case_sensitive == other.case_sensitive

    def __hash__(self) -> int:
        return hash((type(self), self.codepoints, self.case_sensitive))

    def __repr__(self) -> str:
        codepoints_str = f"range({hex(self.codepoints.start)}, {hex(self.codepoints.stop)})"
        if self.case_sensitive:
            return f"RangeAlphabet({codepoints_str})"
        case_sensitive_str = f"case_sensitive={self.case_sensitive}"
        return f"RangeAlphabet({codepoints_str}, {case_sensitive_str})"

class _RangeAlphabetRevdir(Mapping[str, int]):

    _alphabet: RangeAlphabet

    def __init__(self, alphabet: RangeAlphabet):
        self._alphabet = alphabet

    def __iter__(self) -> Iterator[str]:
        return iter(self._alphabet)

    def __len__(self) -> int:
        return len(self._alphabet)

    def __contains__(self, char: Any) -> bool:
        if not isinstance(char, str):
            return False
        alphabet = self._alphabet
        if alphabet.case_sensitive:
            return ord(char) in alphabet.codepoints
        return ord(char.upper()) in alphabet.codepoints or ord(char.lower()) in alphabet.codepoints

    def __getitem__(self, char: str) -> int:
        validate(char, str)
        alphabet = self._alphabet
        if ord(char) in alphabet.codepoints:
            return ord(char)-alphabet.codepoints.start
        if not alphabet.case_sensitive:
            if ord(char.upper()) in alphabet.codepoints:
                return ord(char.upper())-alphabet.codepoints.start
            if ord(char.lower()) in alphabet.codepoints:
                return ord(char.lower())-alphabet.codepoints.start
        raise KeyError(f"Character {repr(char)} not in alphabet.")
