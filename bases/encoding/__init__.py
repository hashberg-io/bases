"""
    Module containing classes for encodings.

    To access existing encodings, use the `get` function:

    ```py
        >>> from bases import encoding
        >>> encoding.get("base32")
        FixcharBaseEncoding(
            StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                           case_sensitive=False),
            pad_char='=', padding='include')
    ```

    To create new encodings, use the `make` function:

    ```py
        >>> encoding.make("0123", kind="zeropad-enc", block_nchars=4)
        ZeropadBaseEncoding(StringAlphabet('0123'), block_nchars=4)
    ```

    To register new encodings, use the `register` function:

    ```py
        >>> myenc = encoding.get("base16").lower()
        >>> encoding.register(base16lower=myenc)
        >>> encoding.get("base16lower")
        ZeropadBaseEncoding(
            StringAlphabet('0123456789abcdef',
                           case_sensitive=False),
            block_nchars=2)
    ```

    Alternatively, use the optional `"name"` argument of the `make` function:

    ```py
        >>> encoding.make("0123", kind="zeropad-enc", block_nchars=4, name="base4")
        ZeropadBaseEncoding(StringAlphabet('0123'), block_nchars=4)
        >>> encoding.get("base4")
        ZeropadBaseEncoding(StringAlphabet('0123'), block_nchars=4)
    ```

    To list alphabets (with optional filtering), use `table`:

    ```py
        >>> dict(encoding.table(prefix="base32"))
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

"""

import re
from typing import Any, cast, Collection, Dict, Iterator, Mapping, Optional, overload, Tuple, Type, Union
from typing_extensions import Literal
from typing_validation import validate

from bases import alphabet
from bases.alphabet import Alphabet
from .base import BaseEncoding as BaseEncoding
from .simple import SimpleBaseEncoding as SimpleBaseEncoding
from .zeropad import ZeropadBaseEncoding as ZeropadBaseEncoding
from .block import BlockBaseEncoding as BlockBaseEncoding
from .fixchar import FixcharBaseEncoding as FixcharBaseEncoding

_base_encodings: Dict[str, BaseEncoding] = {}

def get(name: str) -> BaseEncoding:
    """
        Gets an encoding by name, raising `KeyError` if none exists.

        Example usage:

        ```py
        >>> from bases import encoding
        >>> encoding.get("base16")
        ZeropadBaseEncoding(
            StringAlphabet('0123456789ABCDEF',
                           case_sensitive=False),
            block_nchars=2)
        ```
    """
    validate(name, str)
    if name not in _base_encodings:
        raise KeyError(f"Encoding named {repr(name)} does not exist.")
    return _base_encodings[name]

def has(name: str) -> bool:
    """
        ```py
        >>> from bases import encoding
        >>> encoding.has("base32")
        True
        ```
    """
    validate(name, str)
    return name in _base_encodings

def register(**kwargs: BaseEncoding) -> None:
    """
        Registers any number of new encodings by name.
        Raises `KeyError` is an encoding with one of the given name already exists.

        Example usage:

        ```py
        >>> from bases import encoding
        >>> encoding.register(base16lower=encoding.base16.lower())
        >>> encoding.get("base16lower")
        ZeropadBaseEncoding(
            StringAlphabet('0123456789abcdef',
                           case_sensitive=False),
            block_nchars=2)
        ```

        Encoding names must conform with:

        ```py
        re.match(r"^base[0-9][a-zA-Z0-9_]*$", name)
        ```
    """
    for arg in kwargs.values():
        validate(arg, BaseEncoding)
    for name, encoding in kwargs.items():
        if not re.match(r"^base[0-9][a-zA-Z0-9_]*$", name):
            raise ValueError(f"Invalid encoding name {repr(name)}")
        if not isinstance(encoding, BaseEncoding):
            raise TypeError()
        if name in _base_encodings:
            raise ValueError(f"Encoding named {repr(name)} already exists.")
        _base_encodings[name] = encoding

def unregister(*names: str) -> None:
    """
        Unregisters any number of existing encodings by name.
        Raises `KeyError` is an encoding with one of the given names doesn't exist.

        Example usage:

        ```py
        >>> from bases import encoding
        >>> encoding.unregister("base16", "base32")
        >>> encoding.has("base16")
        False
        >>> encoding.get("base16")
        KeyError: "Encoding named 'base16' does not exist."
        ```

        Note that pre-defined constants are unaffected by this:

        ```py
        >>> encoding.base16
        ZeropadBaseEncoding(
            StringAlphabet('0123456789ABCDEF',
                           case_sensitive=False),
            block_nchars=2)
        ```
    """
    for name in names:
        validate(name, str)
    for name in names:
        if name not in _base_encodings:
            raise KeyError(f"Encoding named {repr(name)} does not exist.")
        del _base_encodings[name]

def table(*, prefix: str = "") -> Iterator[Tuple[str, BaseEncoding]]:
    """
        Iterates over all registered alphabets, optionally restricting to those with given prefix:

        Example usage:

        ```py
        >>> from bases import encoding
        >>> dict(encoding.table(prefix="base32"))
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

    """
    validate(prefix, str)
    encodings = [(name, encoding) for name, encoding in _base_encodings.items()
                 if name.startswith(prefix)]
    encodings = sorted(encodings, key=lambda pair: pair[0])
    return iter(encodings)

BaseEncodingKind = Literal["simple-enc", "zeropad-enc", "block-enc", "fixchar-enc"]
_base_encoding_kinds = ("simple-enc", "zeropad-enc", "block-enc", "fixchar-enc")

@overload
def make(chars: Union[str, range, Alphabet], *, kind: Literal["simple-enc"], name: Optional[str] = None,
         case_sensitive: Optional[bool] = None,) -> SimpleBaseEncoding:
    ...

@overload
def make(chars: Union[str, range, Alphabet], *, kind: Literal["zeropad-enc"], name: Optional[str] = None,
         case_sensitive: Optional[bool] = None, block_nbytes: int = 1, block_nchars: int = 1) -> ZeropadBaseEncoding:
    ...

@overload
def make(chars: Union[str, range, Alphabet], *, kind: Literal["block-enc"], name: Optional[str] = None,
         case_sensitive: Optional[bool] = None, block_size: Union[int, Mapping[int, int]], sep_char: str = "") -> BlockBaseEncoding:
    ...

@overload
def make(chars: Union[str, range, Alphabet], *, kind: Literal["fixchar-enc"], name: Optional[str] = None,
         case_sensitive: Optional[bool] = None,) -> FixcharBaseEncoding:
    ...

def make(chars: Union[str, range, Alphabet, BaseEncoding], *, kind: str, name: Optional[str] = None,
         case_sensitive: Optional[bool] = None, **kwargs: Any) -> BaseEncoding:
    """
        Utility function to create custom encodings.
        The `kind` keyword argument can be used to select different encoding constructors:

        - if `"simple-enc"`, uses `bases.encoding.simple.SimpleBaseEncoding`
        - if `"zeropad-enc"`, uses `bases.encoding.zeropad.ZeropadBaseEncoding`
        - if `"block-enc"`, uses `bases.encoding.block.BlockBaseEncoding`
        - if `"fixchar-enc"`, uses `bases.encoding.fixchar.FixcharBaseEncoding`

        If the optional keyword argument `name` is specified, the encoding is automatically registered using `register`.

        The positional argument `chars` and the keyword argument `case_sensitive` are common to all encodings (with
        `bases.encoding.block.BlockBaseEncoding` additionally accepting a `bases.encoding.base.BaseEncoding` instance).
        The additional `kwargs` are those of each individual class constructor.

        Example usage:

        ```py
        >>> from bases import encoding
        >>> encoding.make("0123", kind="zeropad-enc", block_nchars=4, name="base4")
        ZeropadBaseEncoding(StringAlphabet('0123'), block_nchars=4)
        >>> encoding.get("base4")
        ZeropadBaseEncoding(StringAlphabet('0123'), block_nchars=4)
        >>> encoding.get("base4").encode(b"0x7E")
        '0300132003131011'
        ```

    """
    validate(chars, Union[str, range, Alphabet, BaseEncoding])
    validate(kind, str)
    validate(name, Optional[str])
    validate(case_sensitive, Optional[bool])
    kwargs["case_sensitive"] = case_sensitive
    if kind == "simple-enc":
        if isinstance(chars, BaseEncoding):
            raise ValueError("Argument 'chars' can be a BaseEncoding only when 'kind' is 'block-enc'.")
        enc: BaseEncoding = SimpleBaseEncoding(chars, **kwargs)
    elif kind == "zeropad-enc":
        if isinstance(chars, BaseEncoding):
            raise ValueError("Argument 'chars' can be a BaseEncoding only when 'kind' is 'block-enc'.")
        enc = ZeropadBaseEncoding(chars, **kwargs)
    elif kind == "block-enc":
        enc = BlockBaseEncoding(chars, **kwargs)
    elif kind == "fixchar-enc":
        if isinstance(chars, BaseEncoding):
            raise ValueError("Argument 'chars' can be a BaseEncoding only when 'kind' is 'block-enc'.")
        enc = FixcharBaseEncoding(chars, **kwargs)
    else:
        raise ValueError(f"Encoding kind {repr(kind)} not currently supported.")
    if name is not None:
        register(**{name: enc})
    return enc

# zero-padded base encodings (fixed blocks)

base2 = ZeropadBaseEncoding(alphabet.base2, block_nchars=8)
""" Base-2 encoding (8-char blocks). """

base16 = ZeropadBaseEncoding(alphabet.base16, block_nchars=2)
"""
    Uppercase case-insensitive base-16 encoding (2-char blocks).
    This is the same encoding specified by [rfc4648](https://datatracker.ietf.org/doc/html/rfc4648).
"""

register(base2=base2, base16=base16)


# zero-padded base encodings (elastic)

base10 = ZeropadBaseEncoding(alphabet.base10)
""" Base-10 encoding. """

base36 = ZeropadBaseEncoding(alphabet.base36)
""" Uppercase case-insensitive base-36 alphabet. """

base58btc = ZeropadBaseEncoding(alphabet.base58btc)
"""
    Case-sensitive base-58 encoding used by Bitcoin.

    Specs from https://datatracker.ietf.org/doc/html/draft-msporny-base58-02
"""

base58flickr = ZeropadBaseEncoding(alphabet.base58flickr)
"""
    Case-sensitive base-58 encoding used by Flickr.

    Spec from https://datatracker.ietf.org/doc/html/draft-msporny-base58-02 but using alphabet `bases.alphabet.base58flickr`.
"""

base58ripple = ZeropadBaseEncoding(alphabet.base58ripple)
"""
    Case-sensitive base-58 encoding used by Ripple.

    Spec from https://datatracker.ietf.org/doc/html/draft-msporny-base58-02 but using alphabet `bases.alphabet.base58ripple`.
"""

register(base10=base10, base36=base36, base58btc=base58btc, base58flickr=base58flickr, base58ripple=base58ripple)


# fixed-char base encodings

base8 = FixcharBaseEncoding(alphabet.base8, pad_char="=", padding="include")
""" Base-8 encoding from https://github.com/multiformats/multibase/blob/master/rfcs/Base8.md """

base32 = FixcharBaseEncoding(alphabet.base32, pad_char="=", padding="include")
""" Uppercase case-insensitive base-32 encoding from [rfc4648](https://datatracker.ietf.org/doc/html/rfc4648). """

base32hex = FixcharBaseEncoding(alphabet.base32hex, pad_char="=", padding="include")
""" Uppercase case-insensitive hex base-32 encoding from [rfc4648](https://datatracker.ietf.org/doc/html/rfc4648). """

base32z = FixcharBaseEncoding(alphabet.base32z)
"""
    Lowercase case-insensitive human-oriented base-32 encoding from https://philzimmermann.com/docs/human-oriented-base-32-encoding.txt
"""

base64 = FixcharBaseEncoding(alphabet.base64, pad_char="=", padding="include")
""" Uppercase case-sensitive base-64 encoding from [rfc4648](https://datatracker.ietf.org/doc/html/rfc4648). """

base64url = FixcharBaseEncoding(alphabet.base64url, pad_char="=", padding="include")
""" Uppercase case-sensitive url-safe base-64 encoding from [rfc4648](https://datatracker.ietf.org/doc/html/rfc4648). """

register(base8=base8, base32=base32, base32hex=base32hex, base32z=base32z,
         base64=base64, base64url=base64url)

# block base encodings

base45 = BlockBaseEncoding(alphabet.base45, block_size={1: 2, 2: 3}, reverse_blocks=True)
"""
    Uppercase case-insensitive base-45 encoding from https://datatracker.ietf.org/doc/draft-faltstrom-base45/

    Note that this is (slightly) different from the [ISO/IEC 18004:2015 standard](https://www.iso.org/standard/62021.html)
"""

register(base45=base45)
