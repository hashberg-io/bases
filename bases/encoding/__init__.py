"""
    Module containing classes for encodings.

"""

from __future__ import annotations

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
        Gets an encoding by name.

        Example usage:

        >>> bases.get("base16")
        ZeropadBaseEncoding(
            StringAlphabet('0123456789ABCDEF',
                           case_sensitive=False),
            block_nchars=2)

        :param name: the encoding name
        :type name: :obj:`str`

        :raises KeyError: if an encoding by the given name does not exist
    """
    validate(name, str)
    if name not in _base_encodings:
        raise KeyError(f"Encoding named {repr(name)} does not exist.")
    return _base_encodings[name]

def has(name: str) -> bool:
    """
        Checks whether an encoding with the given name exists.

        >>> bases.has("base32")
        True

        :param name: the encoding name
        :type name: :obj:`str`
    """
    validate(name, str)
    return name in _base_encodings

def register(**encs: BaseEncoding) -> None:
    r"""
        Registers any number of new encodings by name.

        Example usage:

        >>> bases.register(base16lower=encoding.base16.lower())
        >>> bases.get("base16lower")
        ZeropadBaseEncoding(
            StringAlphabet('0123456789abcdef',
                           case_sensitive=False),
            block_nchars=2)

        Encoding names must conform with:

        .. code-block:: python

            re.match(r"^base[0-9][a-zA-Z0-9_]*$", name)

        :param encs: the encodings to register, passed by desired registration name
        :type encs: :obj:`~typing.Dict`\ [:obj:`str`, :class:`~bases.encoding.base.BaseEncoding`]

        :raises KeyError: if an encoding with one of the given names already exists

    """
    for arg in encs.values():
        validate(arg, BaseEncoding)
    for name, encoding in encs.items():
        if not re.match(r"^base[0-9][a-zA-Z0-9_]*$", name):
            raise ValueError(f"Invalid encoding name {repr(name)}")
        if not isinstance(encoding, BaseEncoding):
            raise TypeError()
        if name in _base_encodings:
            raise ValueError(f"Encoding named {repr(name)} already exists.")
        _base_encodings[name] = encoding

def unregister(*names: str) -> None:
    r"""
        Unregisters any number of existing encodings by name.

        Example usage:

        >>> from bases import encoding
        >>> encoding.unregister("base16", "base32")
        >>> encoding.has("base16")
        False
        >>> encoding.get("base16")
        KeyError: "Encoding named 'base16' does not exist."

        Note that pre-defined constants are unaffected by this:

        >>> encoding.base16
        ZeropadBaseEncoding(
            StringAlphabet('0123456789ABCDEF',
                           case_sensitive=False),
            block_nchars=2)

        :param names: the encoding names
        :type names: :obj:`~typing.Tuple`\ [:obj:`str`, ...]

        :raises KeyError: if an encoding with one of the given names does not exists
    """
    for name in names:
        validate(name, str)
    for name in names:
        if name not in _base_encodings:
            raise KeyError(f"Encoding named {repr(name)} does not exist.")
        del _base_encodings[name]

def table(*, prefix: str = "") -> Iterator[Tuple[str, BaseEncoding]]:
    """
        Iterates over all registered encodings, optionally restricting to those with given prefix:

        Example usage:

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

        :param name: optional prefix to filter by when listing encodings
        :type name: :obj:`str`, *optional*
    """
    validate(prefix, str)
    encodings = [(name, encoding) for name, encoding in _base_encodings.items()
                 if name.startswith(prefix)]
    encodings = sorted(encodings, key=lambda pair: pair[0])
    return iter(encodings)

BaseEncodingKind = Literal["simple-enc", "zeropad-enc", "block-enc", "fixchar-enc"]
""" Possible values for the ``kind`` keyword argument to :func:`make` """

_base_encoding_kinds = ("simple-enc", "zeropad-enc", "block-enc", "fixchar-enc")

@overload
def make(chars: Union[str, range, Alphabet], *, kind: Literal["simple-enc"], name: Optional[str] = None,
         case_sensitive: Optional[bool] = None,) -> SimpleBaseEncoding:
    ...

@overload
def make(chars: Union[str, range, Alphabet], *, kind: Literal["zeropad-enc"], name: Optional[str] = None,
         case_sensitive: Optional[bool] = None, block_nbytes: int = 1, block_nchars: int = 1) -> ZeropadBaseEncoding:
    # pylint: disable = too-many-arguments
    ...

@overload
def make(chars: Union[str, range, Alphabet, BaseEncoding], *, kind: Literal["block-enc"], name: Optional[str] = None,
         case_sensitive: Optional[bool] = None, block_size: Union[int, Mapping[int, int]], sep_char: str = "") -> BlockBaseEncoding:
    # pylint: disable = too-many-arguments
    ...

@overload
def make(chars: Union[str, range, Alphabet], *, kind: Literal["fixchar-enc"], name: Optional[str] = None,
         case_sensitive: Optional[bool] = None,) -> FixcharBaseEncoding:
    ...

def make(chars: Union[str, range, Alphabet, BaseEncoding], *, kind: str, name: Optional[str] = None,
         case_sensitive: Optional[bool] = None, **kwargs: Any) -> BaseEncoding:
    r"""
        Utility function to create custom encodings.

        The ``kind`` keyword argument can be used to select different encoding constructors:

        - if ``"simple-enc"``, uses :class:`~bases.encoding.simple.SimpleBaseEncoding`
        - if ``"zeropad-enc"``, uses :class:`~bases.encoding.zeropad.ZeropadBaseEncoding`
        - if ``"block-enc"``, uses :class:`~bases.encoding.block.BlockBaseEncoding`
        - if ``"fixchar-enc"``, uses :class:`~bases.encoding.fixchar.FixcharBaseEncoding`

        If the optional keyword argument ``name`` is specified, the encoding is automatically registered using :func:`register`.

        The positional argument ``chars`` and the keyword argument ``case_sensitive`` are common to all encodings (with
        :class:`~bases.encoding.block.BlockBaseEncoding` additionally accepting a :class:`~bases.encoding.base.BaseEncoding` instance).
        The additional ``kwargs`` are those of each individual class constructor.

        Example usage:

        >>> from bases import encoding
        >>> encoding.make("0123", kind="zeropad-enc", block_nchars=4, name="base4")
        ZeropadBaseEncoding(StringAlphabet('0123'), block_nchars=4)
        >>> encoding.get("base4")
        ZeropadBaseEncoding(StringAlphabet('0123'), block_nchars=4)
        >>> encoding.get("base4").encode(b"0x7E")
        '0300132003131011'

        :param chars: the alphabet to use for the encoding, or a "block encoding" when ``'kind'`` is set to ``'block-enc'``
        :type chars: :obj:`str`, :obj:`range`, :class:`~bases.alphabet.abstract.Alphabet` or :class:`~bases.encoding.base.BaseEncoding`
        :param kind: whether the alphabet is case-sensitive
        :type kind: ``"simple-enc"``, ``"zeropad-enc"``, ``"block-enc"`` or ``"fixchar-enc"``
        :param name: if specified, the newly created alphabet is registered with this name
        :type name: :obj:`str` or :obj:`None`, *optional*
        :param case_sensitive: whether the encoding alphabet is case-sensitive
        :type case_sensitive: :obj:`bool`, *optional*
        :param kwargs: additional keyword arguments to be passed to the chosen encoding constructor
        :type kwargs: :obj:`~typing.Dict`\ [:obj:`str`, :obj:`~typing.Any`]

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
    This is the same encoding specified by `rfc4648 <https://datatracker.ietf.org/doc/html/rfc4648>`_.
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

    Spec from https://datatracker.ietf.org/doc/html/draft-msporny-base58-02 but using alphabet :obj:`~bases.alphabet.base58flickr`.
"""

base58ripple = ZeropadBaseEncoding(alphabet.base58ripple)
"""
    Case-sensitive base-58 encoding used by Ripple.

    Spec from https://datatracker.ietf.org/doc/html/draft-msporny-base58-02 but using alphabet :obj:`~bases.alphabet.base58ripple`.
"""

register(base10=base10, base36=base36, base58btc=base58btc, base58flickr=base58flickr, base58ripple=base58ripple)


# fixed-char base encodings

base8 = FixcharBaseEncoding(alphabet.base8, pad_char="=", padding="include")
""" Base-8 encoding from https://github.com/multiformats/multibase/blob/master/rfcs/Base8.md """

base32 = FixcharBaseEncoding(alphabet.base32, pad_char="=", padding="include")
""" Uppercase case-insensitive base-32 encoding from `rfc4648 <https://datatracker.ietf.org/doc/html/rfc4648>`_. """

base32hex = FixcharBaseEncoding(alphabet.base32hex, pad_char="=", padding="include")
""" Uppercase case-insensitive hex base-32 encoding from `rfc4648 <https://datatracker.ietf.org/doc/html/rfc4648>`_. """

base32z = FixcharBaseEncoding(alphabet.base32z)
"""
    Lowercase case-insensitive human-oriented base-32 encoding from https://philzimmermann.com/docs/human-oriented-base-32-encoding.txt
"""

base64 = FixcharBaseEncoding(alphabet.base64, pad_char="=", padding="include")
""" Uppercase case-sensitive base-64 encoding from `rfc4648 <https://datatracker.ietf.org/doc/html/rfc4648>`_. """

base64url = FixcharBaseEncoding(alphabet.base64url, pad_char="=", padding="include")
""" Uppercase case-sensitive url-safe base-64 encoding from `rfc4648 <https://datatracker.ietf.org/doc/html/rfc4648>`_. """

register(base8=base8, base32=base32, base32hex=base32hex, base32z=base32z,
         base64=base64, base64url=base64url)

# block base encodings

base45 = BlockBaseEncoding(alphabet.base45, block_size={1: 2, 2: 3}, reverse_blocks=True)
"""
    Uppercase case-insensitive base-45 encoding from https://datatracker.ietf.org/doc/draft-faltstrom-base45/

    Note that this is (slightly) different from the `ISO/IEC 18004:2015 standard <https://www.iso.org/standard/62021.html>`_.
"""

register(base45=base45)
