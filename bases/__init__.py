"""
    A Python library for general base-N encodings.

    The core functionality of the library is performed by the `bases.encoding.base.BaseEncoding.encode`
    and `bases.encoding.base.BaseEncoding.decode` methods of base encodings, instances of
    `bases.encoding.base.BaseEncoding` (more precisely, of its concrete subclasses).

    Common encodings are associated to pre-defined constants, for ease of use:

    ```py
        >>> from bases import base32
        >>> base32
        FixcharBaseEncoding(
            StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                           case_sensitive=False),
            pad_char='=', padding='include')
        >>> b = bytes([70, 98, 190, 187, 66, 224, 178])
        >>> base32.encode(b)
        'IZRL5O2C4CZA===='
        >>> s = 'IZRL5O2C4CZA===='
        >>> list(base32.decode(s))
        [70, 98, 190, 187, 66, 224, 178]
    ```

    The `bases.encoding.get`, `bases.encoding.has`, `bases.encoding.make`, `bases.encoding.table`,
    `bases.encoding.register` and `bases.encoding.unregister` functions provide an interface for
    the programmatic management of encodings:

    ```py
        >>> import bases
        >>> bases.get("base32")
        FixcharBaseEncoding(
            StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                           case_sensitive=False),
            pad_char='=', padding='include')
        >>> bases.make("0123", kind="zeropad-enc", block_nchars=4, name="base4")
        ZeropadBaseEncoding(StringAlphabet('0123'), block_nchars=4)
        >>> bases.get("base4")
        ZeropadBaseEncoding(StringAlphabet('0123'), block_nchars=4)
        >>> dict(bases.table(prefix="base32"))
        {'base32':      FixcharBaseEncoding(
                            StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                                           case_sensitive=False),
                            pad_char='=', padding='include'),
         'base32hex':   FixcharBaseEncoding(
                            StringAlphabet('0123456789ABCDEFGHIJKLMNOPQRSTUV',
                                           case_sensitive=False),
                            pad_char='=', padding='include'),
         'base32z':     FixcharBaseEncoding(
                            StringAlphabet('ybndrfg8ejkmcpqxot1uwisza345h769',
                                           case_sensitive=False))
        }
    ```

    The pre-defined encoding constants and utility functions are defined and documented in
    the `bases.encoding` sub-module, but they can be imported directly from `bases` for added convenience.

"""

__version__ = "0.2.0"

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

# functions are already documented in `bases.encoding`
__pdoc__ = {name: False for name in ["get", "has", "make", "register", "unregister", "table"]}
