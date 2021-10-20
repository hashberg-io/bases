"""
    Module containing classes for alphabets.

    To access existing alphabets, use the `get` function:

    ```py
        >>> from bases import encoding
        >>> alphabet.get("base16")
        StringAlphabet('0123456789ABCDEF')
    ```

    To create new alphabets, use the `make` function:

    ```py
        >>> alphabet.make("0123456789abcdef")
        StringAlphabet('0123456789abcdef')
    ```

    To register new alphabets, use the `register` function:

    ```py
        >>> myalpha = alphabet.make("0123456789abcdef")
        >>> alphabet.register(base16lower=myalpha)
    ```

    Alternatively, use the optional `"name"` argument of the `make` function:

    ```py
        >>> alphabet.make("0123456789abcdef", name="base16lower")
        StringAlphabet('0123456789abcdef')
        >>> alphabet.get("base16lower")
        StringAlphabet('0123456789abcdef')
    ```

    To list alphabets (with optional filtering), use `table`:

    ```py
        >>> dict(alphabet.table(prefix="base32"))
        {'base32': StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567', case_sensitive=False),
         'base32hex': StringAlphabet('0123456789ABCDEFGHIJKLMNOPQRSTUV', case_sensitive=False),
         'base32z': StringAlphabet('ybndrfg8ejkmcpqxot1uwisza345h769', case_sensitive=False)}
    ```
"""

import re
from typing import Collection, Dict, Iterator, Optional, overload, Tuple, Union
from typing_extensions import Literal

from .abstract import Alphabet as Alphabet
from .string_alphabet import StringAlphabet as StringAlphabet
from .range_alphabet import RangeAlphabet as RangeAlphabet

_alphabets: Dict[str, Alphabet] = {}

def get(name: str) -> Alphabet:
    """
        Gets an alphabet by name, raising `KeyError` if none exists.

        Example usage:

        ```py
        >>> alphabet.get("base16")
        StringAlphabet('0123456789ABCDEF')
        ```
    """
    if name not in _alphabets:
        raise KeyError(f"Alphabet named {repr(name)} does not exist.")
    return _alphabets[name]

def has(name: str) -> bool:
    """
        Checks whether an alphabet with the given name exists.

        Example usage:

        ```py
        >>> from bases import alphabet
        >>> alphabet.has("base32")
        True
        ```
    """
    return name in _alphabets

def register(**kwargs: Alphabet) -> None:
    """
        Registers any number of new alphabets by name.
        Raises `KeyError` is an alphabet with one of the given name already exists.

        Example usage:

        ```py
        >>> from bases import alphabet
        >>> alphabet.register(base16lower=alphabet.base16.lower())
        >>> alphabet.get("base16lower")
        StringAlphabet('0123456789abcdef')
        ```

        Alphabet names must conform with:

        ```py
        re.match(r"^base[0-9][a-zA-Z0-9_]*$", name)
        ```
    """
    for name, alphabet in kwargs.items():
        if not re.match(r"^base[0-9][a-zA-Z0-9_]*$", name):
            raise ValueError(f"Invalid alphabet name {repr(name)}")
        if not isinstance(alphabet, Alphabet):
            raise TypeError()
        if name in _alphabets:
            raise ValueError(f"Alphabet named {repr(name)} already exists.")
        _alphabets[name] = alphabet

def unregister(*names: str) -> None:
    """
        Unregisters any number of existing alphabets by name.
        Raises `KeyError` is an alphabet with one of the given names doesn't exist.

        Example usage:

        ```py
        >>> from bases import alphabet
        >>> alphabet.unregister("base16", "base32")
        >>> alphabet.has("base16")
        False
        >>> alphabet.get("base16")
        KeyError: "Alphabet named 'base16' does not exist."
        ```

        Note that pre-defined constants are unaffected by this:

        ```py
        >>> alphabet.base16
        StringAlphabet('0123456789ABCDEF')
        ```
    """
    for name in names:
        if name not in _alphabets:
            raise KeyError(f"Alphabet named {repr(name)} does not exist.")
        del _alphabets[name]

def table(*, prefix: str = "") -> Iterator[Tuple[str, Alphabet]]:
    """
        Iterates over all registered alphabets, optionally restricting to those with given prefix.

        Example usage:

        ```py
        >>> from bases import alphabet
        >>> dict(alphabet.table(prefix="base32"))
        {'base32': StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567', case_sensitive=False),
         'base32hex': StringAlphabet('0123456789ABCDEFGHIJKLMNOPQRSTUV', case_sensitive=False),
         'base32z': StringAlphabet('ybndrfg8ejkmcpqxot1uwisza345h769', case_sensitive=False)}
        ```

    """
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
        Automatically creates an instance of `bases.alphabet.string_alphabet.StringAlphabet`
        or `bases.alphabet.range_alphabet.RangeAlphabet` based on whether a string or range is passed.

        Example usage with string (case-insensitive base-16):

        ```py
        >>> alphabet.make("0123456789ABCDEF", case_sensitive=False)
        StringAlphabet('0123456789ABCDEF', case_sensitive=False)
        ```

        Example usage with range (extended ASCII):

        ```py
        >>> alphabet.make(range(0x00, 0x100))
        RangeAlphabet(range(0x00, 0x100))
        ```

        If the optional keyword argument `name` is specified, the alphabet is automatically registered using `register`.
    """
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
""" Uppercase case-insensitive base-32 alphabet from [rfc4648](https://datatracker.ietf.org/doc/html/rfc4648). """

base32hex = make("0123456789ABCDEFGHIJKLMNOPQRSTUV", case_sensitive=False, name="base32hex")
""" Uppercase case-insensitive hex base-32 alphabet from [rfc4648](https://datatracker.ietf.org/doc/html/rfc4648). """

base32z = make("ybndrfg8ejkmcpqxot1uwisza345h769", case_sensitive=False, name="base32z")
"""
    Lowercase case-insensitive human-oriented base-32 alphabet from https://philzimmermann.com/docs/human-oriented-base-32-encoding.txt
"""

base64 = make("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/", name="base64")
""" Uppercase case-insensitive base-64 alphabet from [rfc4648](https://datatracker.ietf.org/doc/html/rfc4648). """

base64url = make("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_", name="base64url")
""" Uppercase case-insensitive url-safe base-64 alphabet from [rfc4648](https://datatracker.ietf.org/doc/html/rfc4648). """

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
