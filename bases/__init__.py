"""
    A Python library for general base-N encodings.

    The following base encodings and be imported directly from top level:

    >>> import bases
    >>> for name in dir(bases):
    ...     if name.startswith("base"):
    ...         print(name)
    ...
    base10
    base16
    base2
    base32
    base32hex
    base32z
    base36
    base45
    base58btc
    base58flickr
    base58ripple
    base64
    base64url
    base8

    For example:

    >>> from bases import base10, base32
    >>> base10
    ZeropadBaseEncoding(StringAlphabet('0123456789'))
    >>> base32
    FixcharBaseEncoding(StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                                       case_sensitive=False),
                        pad_char='=', padding='include')

"""

from __future__ import annotations

__version__ = "0.3.0"

from . import encoding as encoding
from . import alphabet as alphabet
from .encoding import (base2, base16, base8, base10, base36, base58btc, base58flickr, base58ripple,
                       base32, base32hex, base32z, base64, base64url, base45,)
from .encoding import get, has, make, register, unregister, table

# re-export all encodings and functions.
__all__ = [
    "base2", "base16", "base8", "base10", "base36", "base58btc", "base58flickr", "base58ripple",
    "base32", "base32hex", "base32z", "base64", "base64url", "base45",
    "get", "has", "make", "register", "unregister", "table"
]
