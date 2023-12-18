"""
    Abstract alphabets.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional, overload, Sequence, Union
from typing_extensions import Self
from typing_validation import validate

class Alphabet(ABC, Sequence[str]):
    """
        Abstract superclass for alphabets with specified case sensitivity.
        It contains a mapping of digits (numbers in ``range(len(self))``) to characters
        and a reverse mapping of characters to digits:

        >>> alphabet.base16
        StringAlphabet('0123456789ABCDEF')
        >>> alphabet.base16[12]
        'C'
        >>> alphabet.base16.index("C")
        12

        :param case_sensitive: whether the alphabet is case-sensitive
        :type case_sensitive: :obj:`bool`, *optional*
    """

    _case_sensitive: bool

    def __init__(self, case_sensitive: bool = True):
        validate(case_sensitive, bool)
        self._case_sensitive = case_sensitive

    @property
    def case_sensitive(self) -> bool:
        """
            Case sensitivity of the alphabet (default: :obj:`True`).
            If set to :obj:`False`, characters will be deemed in the alphabet regardless of case.
            However, accessing characters from the alphabet will yield the case originally specified:

            >>> alphabet.base32
            StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                           case_sensitive=False)
            >>> "a" in alphabet.base32
            True
            >>> alphabet.base32[0]
            'A'

        """
        return self._case_sensitive

    def index(self, char: str, start: int = 0, stop: Optional[int] = None) -> int:
        """
            Returns the index of a character in the alphabet.
            Optionally allows a starting index (included) and stopping index (excluded).

            Example usage:

            >>> alphabet.base32
            StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                           case_sensitive=False)
            >>> alphabet.base32.index("F")
            5
            >>> alphabet.base32[5]
            'F'
            >>> alphabet.base32.index("f") # case-insensitive
            5

            :param char: the character to look for
            :type char: :obj:`str`
            :param start: optional start index (included) for the search range
            :param start: :obj:`int`, *optional*
            :param start: optional end index (excluded) for the search range
            :param start: :obj:`int` or :obj:`None`, *optional*

            :raises ValueError: if the character is not in the alphabet
        """
        # pylint: disable = arguments-renamed
        validate(char, str)
        validate(start, int)
        validate(stop, Optional[int])
        if start < 0:
            start = max(len(self) + start, 0)
        if stop is None:
            stop = start+max(len(self)-start, 0)
        elif stop < 0:
            stop += len(self)
        revdir = self.revdir
        if char not in revdir:
            raise ValueError(f"Char {repr(char)} not in alphabet.")
        idx = revdir[char]
        if not start <= idx < stop:
            raise ValueError(f"Char {repr(char)} not in alphabet[{start}:{stop}].")
        return idx

    def count(self, char: str) -> int:
        """
            Returns 1 if `char` is in the alphabet and 0 otherwise.

            :param char: the character to count for
            :type char: :obj:`str`
        """
        # pylint: disable = arguments-renamed
        validate(char, str)
        return 1 if char in self else 0

    def __contains__(self, char: Any) -> bool:
        if not isinstance(char, str):
            return False
        return char in self.revdir

    @property
    @abstractmethod
    def revdir(self) -> Mapping[str, int]:
        """
            Reverse directory for the alphabet, mapping characters to their index.

            Example usage:

            >>> alphabet.base16.revdir
            mappingproxy({'0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
                          '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                          'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15})

            For case-insensitive alphabets, this contains both cases of any cased characters:

            >>> alphabet.base16.with_case_sensitivity(False).revdir
            mappingproxy({'0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
                          '5': 5, '6': 6, '7': 7,'8': 8, '9': 9,
                          'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15,
                          'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15})

        """

    @abstractmethod
    def with_case_sensitivity(self, case_sensitive: bool) -> Self:
        """
            Returns a new alphabet with the same characters as this one but with specified case sensitivity.

            Example usage:

            >>> alphabet.base32
            StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                           case_sensitive=False)
            >>> alphabet.base32.with_case_sensitivity(True)
            StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567')

            :param case_sensitive: whether the new alphabet is case-sensitive
            :type case_sensitive: :obj:`bool`, *optional*
        """

    @abstractmethod
    def upper(self) -> Alphabet:
        """
            Returns a new alphabet with all cased characters turned to uppercase.

            Example usage:

            >>> alphabet.base32z
            StringAlphabet('ybndrfg8ejkmcpqxot1uwisza345h769',
                           case_sensitive=False)
            >>> alphabet.base32z.upper()
            StringAlphabet('YBNDRFG8EJKMCPQXOT1UWISZA345H769',
                           case_sensitive=False)

        """

    @abstractmethod
    def lower(self) -> Alphabet:
        """
            Returns a new alphabet with all cased characters turned to lowercase.

            Example usage:

            >>> alphabet.base16
            StringAlphabet('0123456789ABCDEF')
            >>> alphabet.base16.lower()
            StringAlphabet('0123456789abcdef')

        """

    @abstractmethod
    def __len__(self) -> int:
        ...

    @overload
    def __getitem__(self, idx: int) -> str:
        ...

    @overload
    def __getitem__(self, idx: slice) -> Alphabet:
        ...

    @abstractmethod
    def __getitem__(self, idx: Union[int, slice]) -> Union[str, Alphabet]:
        ...

