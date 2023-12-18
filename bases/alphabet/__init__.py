"""
    Module containing classes for alphabets.
"""

from __future__ import annotations

import re
from typing import Collection, Dict, Iterator, Optional, overload, Tuple, Union
from typing_extensions import Literal
from typing_validation import validate

from .abstract import Alphabet as Alphabet
from .string_alphabet import StringAlphabet as StringAlphabet
from .range_alphabet import RangeAlphabet as RangeAlphabet

_alphabets: Dict[str, Alphabet] = {}

def get(name: str) -> Alphabet:
    """
        Gets an alphabet by name, raising `KeyError` if none exists.

        Example usage:

        >>> alphabet.get("base16")
        StringAlphabet('0123456789ABCDEF')

        :param name: the alphabet name
        :type name: :obj:`str`

    """
    validate(name, str)
    if name not in _alphabets:
        raise KeyError(f"Alphabet named {repr(name)} does not exist.")
    return _alphabets[name]

def has(name: str) -> bool:
    """
        Checks whether an alphabet with the given name exists.

        Example usage:

        >>> from bases import alphabet
        >>> alphabet.has("base32")
        True

        :param name: the alphabet name
        :type name: :obj:`str`
    """
    validate(name, str)
    return name in _alphabets

def register(**alphabets: Alphabet) -> None:
    r"""
        Registers any number of new alphabets by name.

        Example usage:

        >>> from bases import alphabet
        >>> alphabet.register(base16lower=alphabet.base16.lower())
        >>> alphabet.get("base16lower")
        StringAlphabet('0123456789abcdef')

        Alphabet names must conform with:

        .. code-block::

            re.match(r"^base[0-9][a-zA-Z0-9_]*$", name)

        :param alphabets: the alphabets to register, passed by desired registration name
        :type alphabets: :obj:`~typing.Dict`\ [:obj:`str`, :class:`~bases.alphabet.abstract.Alphabet`]

        :raises KeyError: if an alphabet with one of the given names already exists
    """
    for arg in alphabets.values():
        validate(arg, Alphabet)
    for name, alphabet in alphabets.items():
        if not re.match(r"^base[0-9][a-zA-Z0-9_]*$", name):
            raise ValueError(f"Invalid alphabet name {repr(name)}")
        if not isinstance(alphabet, Alphabet):
            raise TypeError()
        if name in _alphabets:
            raise ValueError(f"Alphabet named {repr(name)} already exists.")
        _alphabets[name] = alphabet

def unregister(*names: str) -> None:
    r"""
        Unregisters any number of existing alphabets by name.

        Example usage:

        >>> from bases import alphabet
        >>> alphabet.unregister("base16", "base32")
        >>> alphabet.has("base16")
        False
        >>> alphabet.get("base16")
        KeyError: "Alphabet named 'base16' does not exist."

        Note that pre-defined constants are unaffected by this:

        >>> alphabet.base16
        StringAlphabet('0123456789ABCDEF')

        :param names: the alphabet names
        :type names: :obj:`~typing.Tuple`\ [:obj:`str`, ...]

        :raises KeyError: if an alphabet with one of the given names does not exists

    """
    for name in names:
        validate(name, str)
    for name in names:
        if name not in _alphabets:
            raise KeyError(f"Alphabet named {repr(name)} does not exist.")
        del _alphabets[name]

def table(*, prefix: str = "") -> Iterator[Tuple[str, Alphabet]]:
    """
        Iterates over all registered alphabets, optionally restricting to those with given prefix.

        Example usage:

        >>> from bases import alphabet
        >>> dict(alphabet.table(prefix="base32"))
        {'base32': StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567', case_sensitive=False),
         'base32hex': StringAlphabet('0123456789ABCDEFGHIJKLMNOPQRSTUV', case_sensitive=False),
         'base32z': StringAlphabet('ybndrfg8ejkmcpqxot1uwisza345h769', case_sensitive=False)}

        :param name: optional prefix to filter by when listing alphabets
        :type name: :obj:`str`, *optional*

    """
    validate(prefix, str)
    alphabets = [(name, alphabet) for name, alphabet in _alphabets.items()
                 if name.startswith(prefix)]
    alphabets = sorted(alphabets, key=lambda pair: pair[0])
    return iter(alphabets)

@overload
def make(chars: str, *, case_sensitive: bool = True, name: Optional[str] = None) -> StringAlphabet:
    ...

@overload
def make(chars: range, *, case_sensitive: bool = True, name: Optional[str] = None) -> RangeAlphabet:
    ...

def make(chars: Union[str, range], *, case_sensitive: bool = True, name: Optional[str] = None) -> Union[StringAlphabet, RangeAlphabet]:
    """
        Utility function to create custom alphabets.
        Automatically creates an instance of :class:`~bases.alphabet.string_alphabet.StringAlphabet`
        or :class:`~bases.alphabet.range_alphabet.RangeAlphabet` based on whether a string or range is passed.

        Example usage with string (case-insensitive base-16):

        >>> alphabet.make("0123456789ABCDEF", case_sensitive=False)
        StringAlphabet('0123456789ABCDEF', case_sensitive=False)

        Example usage with range (extended ASCII):

        >>> alphabet.make(range(0x00, 0x100))
        RangeAlphabet(range(0x00, 0x100))

        If the optional keyword argument ``name`` is specified, the alphabet is automatically registered using :func:`register`.

        :param chars: the alphabet characters or codepoint range
        :type chars: :obj:`str` or :obj:`range`
        :param case_sensitive: whether the alphabet is case-sensitive
        :type case_sensitive: :obj:`bool`, *optional*
        :param name: if specified, the newly created alphabet is registered with this name
        :type name: :obj:`str` or :obj:`None`, *optional*
    """
    validate(chars, Union[str, range])
    validate(case_sensitive, bool)
    validate(name, Optional[str])
    if isinstance(chars, str):
        string_alphabet = StringAlphabet(chars, case_sensitive=case_sensitive)
        if name is not None:
            register(**{name: string_alphabet})
        return string_alphabet
    if isinstance(chars, range):
        range_alphabet = RangeAlphabet(chars, case_sensitive=case_sensitive)
        if name is not None:
            register(**{name: range_alphabet})
        return range_alphabet
    raise NotImplementedError(f"Character type {type(chars)} not supported.")

base2 = make("01", name="base2")
""" Base-2 alphabet. """

base8 = make("01234567", name="base8")
""" Base-8 alphabet. """

base16 = make("0123456789ABCDEF", case_sensitive=False, name="base16")
""" Uppercase case-insensitive base-16 alphabet. """

base32 = make("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567", case_sensitive=False, name="base32")
""" Uppercase case-insensitive base-32 alphabet from `rfc4648 <https://datatracker.ietf.org/doc/html/rfc4648>`_. """

base32hex = make("0123456789ABCDEFGHIJKLMNOPQRSTUV", case_sensitive=False, name="base32hex")
""" Uppercase case-insensitive hex base-32 alphabet from `rfc4648 <https://datatracker.ietf.org/doc/html/rfc4648>`_. """

base32z = make("ybndrfg8ejkmcpqxot1uwisza345h769", case_sensitive=False, name="base32z")
"""
    Lowercase case-insensitive human-oriented base-32 alphabet from https://philzimmermann.com/docs/human-oriented-base-32-encoding.txt
"""

base64 = make("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/", name="base64")
""" Uppercase case-insensitive base-64 alphabet from `rfc4648 <https://datatracker.ietf.org/doc/html/rfc4648>`_. """

base64url = make("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_", name="base64url")
""" Uppercase case-insensitive url-safe base-64 alphabet from `rfc4648 <https://datatracker.ietf.org/doc/html/rfc4648>`_. """

base10 = make("0123456789", name="base10")
""" Base-10 alphabet. """

base36 = make("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", case_sensitive=False, name="base36")
""" Uppercase case-insensitive base-36 alphabet. """

base58btc = make("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz", name="base58btc")
""" Case-sensitive base-58 alphabet used by Bitcoin. """

base58flickr = make("123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ", name="base58flickr")
""" Case-sensitive base-58 alphabet used by Flickr. """

base58ripple = make("rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz", name="base58ripple")
""" Case-sensitive base-58 alphabet used by Ripple. """

base45 = make("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:", case_sensitive=False, name="base45")
"""
    Uppercase case-insensitive base-45 alphabet from https://datatracker.ietf.org/doc/draft-faltstrom-base45/
"""
