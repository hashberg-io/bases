"""
    Block base encodings.

    Split the bytestring to encode (resp. string to decode) into blocks,
    then encodes (resp. decodes) each block individually using an underlying encoding.
    By default, the underlying encoding is a :mod:`~bases.encoding.simple` base encoding.

    Constructor options:

    - ``block_size: Union[int, Mapping[int, int]]`` cf. below
    - ``sep_char: str`` an optional separator character for encoded string blocks (default: ``""``)
    - ``reverse_blocks: bool`` an optional flag to reverse individual char blocks in the encoded string (default: :obj:`False`)

    The ``block_size`` option is mandatory and determines the allowed block sizes for encoding and decoding:

    - if ``block_size`` is a strictly increasing mapping of positive integers to positive integers, its keys are taken
      to be the allowed block byte sizes and its values are taken to be the corresponding block char sizes.
    - if ``block_size`` is an integer, all block byte sizes in ``range(1, block_size+1)`` are allowed, and the coresponding
      block char sizes are computed by:

    .. code-block:: python

        char_size = int(math.floor(math.log(256**byte_size, base)))+1

    The property :attr:`~BlockBaseEncoding.nbytes2nchars` has all valid block byte sizes as keys and the corresponding block char sizes as values.
    The property :attr:`~BlockBaseEncoding.nchars2nbytes` has all valid block char sizes as keys and the corresponding block byte sizes as values.
    Each pair of corresponding block byte and char sizes is assessed to ensure that encoding and decoding are unambiguous,
    using the static methods :meth:`~bases.encoding.zeropad.ZeropadBaseEncoding.max_block_nchars` and
    :meth:`~bases.encoding.zeropad.ZeropadBaseEncoding.max_block_nbytes` from the :mod:`~bases.encoding.zeropad` base encoding implementation
    (cf. class :class:`~bases.encoding.zeropad.ZeropadBaseEncoding`).

    The maximum valid block byte (resp. char) size is used on encoding (resp. decoding) for all blocks except at most the last one:
    if the number of bytes (resp. chars) in the last block is not valid, the bytestring (resp. string) is not valid overall.

    As a concrete example, the following is the constructor for the `base45 encoding <https://datatracker.ietf.org/doc/draft-faltstrom-base45/>`_:

    .. code-block:: python

        base45 = BlockBaseEncoding(alphabet.base45, block_size={1: 2, 2: 3})

    In this case, encoding uses blocks of 2 bytes, with the final block allowed to be 1 or 2 bytes. Decoding uses blocks of 3 chars, with the
    final block allowed to be 2 or 3 chars (but not 1 char). Because no encoding was explicitly specified, the encoding used is the simple
    encoding for the base45 alphabet.

    Encoding of a bytestring ``b``:

    1. split ``b`` into blocks of size :attr:`~BlockBaseEncoding.block_nbytes`, with the final block allowed to be any size in
       :attr:`~BlockBaseEncoding.nbytes2nchars` (raise :class:`~bases.encoding.errors.EncodingError` if it isn't)
    2. encode each block individually using the :attr:`~BlockBaseEncoding.block_encoding`
    3. check that no encoded block string exceeds the block char size corresponding to the original block byte size
    4. prepend zero chars to each encoded block string until it reaches the designated block char size
    5. if ``reverse_blocks``, reverse each individual char block
    6. join the blocks into the final encoded string (using the separator character :attr:`~BlockBaseEncoding.sep_char`, if specified)

    Decoding of a string ``s``:

    1. split ``s`` into blocks of size :attr:`~BlockBaseEncoding.block_nchars`, with the final block allowed to be any size in
       :attr:`~BlockBaseEncoding.nchars2nbytes` (raise :class:`~bases.encoding.errors.DecodingError` if it isn't)
    2. if ``reverse_blocks``, reverse each individual char block
    3. decode each block individually using the :attr:`~BlockBaseEncoding.block_encoding`
    4. check that no decode block bytestring exceeds the block byte size corresponding to the original block char size
    5. prepend zero bytes to each decoded block bytestring until it reaches the designated block byte size
    6. join the blocks into the final decoded bytestring

"""

from __future__ import annotations

import math
from types import MappingProxyType
from typing import Any, Dict, List, Mapping, Optional, Union, TypeVar
from typing_validation import validate

from bases.alphabet import Alphabet
from .base import BaseEncoding, BytesLike, _lstrip_memview
from .simple import SimpleBaseEncoding
from .zeropad import ZeropadBaseEncoding
from .errors import EncodingError, DecodingError, InvalidCharBlockError, InvalidByteBlockError


BlockBaseEncodingSubclass = TypeVar("BlockBaseEncodingSubclass", bound="BlockBaseEncoding")
""" Type variable for subclasses of :class:`BlockBaseEncoding`. """

class BlockBaseEncoding(BaseEncoding):
    r"""
        Block base encodings.

        :param alphabet: the alphabet to use for the encoding
        :type alphabet: :obj:`str`, :obj:`range` or :class:`~bases.alphabet.abstract.Alphabet`
        :param case_sensitive: optional case sensitivity (if :obj:`None`, the one from the alphabet is used)
        :type case_sensitive: :obj:`bool` or :obj:`None`, *optional*


        :param block_size: allowed block size(s) for encoding/decoding
        :type block_size: :obj:`int` or :obj:`~typing.Mapping`\ [:obj:`int`, :obj:`int`]]
        :param sep_char: an optional separator character for encoded string blocks (default: ``""``)
        :type sep_char: :obj:`str`, *optional*
        :param reverse_blocks: an optional flag to reverse individual char blocks in the encoded string (default: :obj:`False`)
        :type sep_char: :obj:`bool`, *optional*

    """
    # pylint: disable = too-many-instance-attributes

    _init_encoding: Union[str, range, Alphabet, BaseEncoding]
    _init_case_sensitive: Optional[bool]
    _init_block_size: Union[int, Mapping[int, int]]

    _block_encoding: BaseEncoding
    _nbytes2nchars: Mapping[int, int]
    _nchars2nbytes: Mapping[int, int]
    _block_nbytes: int
    _sep_char: str = ""
    _block_nchars: int
    _reverse_blocks: bool = False

    def __init__(self, encoding: Union[str, range, Alphabet, BaseEncoding], *,
                 case_sensitive: Optional[bool] = None,
                 block_size: Union[int, Mapping[int, int]],
                 sep_char: str = "",
                 reverse_blocks: bool = False):
        # pylint: disable = too-many-arguments
        validate(encoding, Union[str, range, Alphabet, BaseEncoding])
        validate(block_size, Union[int, Mapping[int, int]])
        validate(sep_char, str)
        validate(reverse_blocks, bool)
        self._init_encoding = encoding
        self._init_case_sensitive = case_sensitive
        self._init_block_size = block_size
        if isinstance(encoding, BaseEncoding):
            alphabet: Union[str, range, Alphabet] = encoding.alphabet
        else:
            alphabet = encoding
            encoding = SimpleBaseEncoding(alphabet)
        super().__init__(alphabet, case_sensitive=case_sensitive)
        self._block_encoding = encoding
        self._sep_char = sep_char
        self._reverse_blocks = reverse_blocks
        if isinstance(block_size, int):
            base = self.base
            block_sizes: Mapping[int, int] = {
                i: int(math.floor(math.log(256**i, base)))+1
                for i in range(1, block_size+1)
            }
        else:
            block_sizes = block_size
        self._nbytes2nchars = MappingProxyType({
            nbytes: block_sizes[nbytes]
            for nbytes in sorted(block_sizes)
        })
        _nchars2nbytes = {
            nchars: nbytes for nbytes, nchars in block_sizes.items()
        }
        self._nchars2nbytes = MappingProxyType({
            nchars: _nchars2nbytes[nchars]
            for nchars in sorted(_nchars2nbytes)
        })
        self._block_nbytes = max(self.nbytes2nchars)
        self._block_nchars = max(self.nchars2nbytes)
        self.__validate_init()

    def __validate_init(self) -> None:
        base = self.base
        sep_char = self.sep_char
        nbytes2nchars = self.nbytes2nchars
        if len(sep_char) not in (0, 1):
            raise ValueError("Separator character must be empty string or length 1 string.")
        prev_nchars: Optional[int] = None
        for _, nchars in nbytes2nchars.items():
            if prev_nchars is None:
                prev_nchars = nchars
            elif prev_nchars >= nchars:
                raise ValueError("Block char size must strictly increase with block byte size.")
        block_nbytes = self.block_nbytes
        block_nchars = self.block_nchars
        max_block_nbytes = ZeropadBaseEncoding.max_block_nbytes(base, block_nchars)
        max_block_nchars = ZeropadBaseEncoding.max_block_nchars(base, block_nbytes)
        if block_nchars > max_block_nchars:
            raise ValueError(f"Number of characters allowed in largest block is too large: "
                             f"the maximum for base = {base} and block_nbytes = {block_nbytes} is "
                             f"block_nchars = {max_block_nchars}")
        if block_nbytes > max_block_nbytes:
            raise ValueError(f"Number of bytes allowed in largest block is too large: "
                             f"the maximum for base = {base} and block_nchars {block_nchars} is "
                             f"block_nbytes = {max_block_nbytes}")

    @property
    def block_encoding(self) -> BaseEncoding:
        """
            The encoding used for individual blocks.
        """
        return self._block_encoding

    @property
    def nbytes2nchars(self) -> Mapping[int, int]:
        """
            Mapping of bytes block sizes to char block sizes.
        """
        return self._nbytes2nchars

    @property
    def nchars2nbytes(self) -> Mapping[int, int]:
        """
            Mapping of char block sizes to byte block sizes.
        """
        return self._nchars2nbytes

    @property
    def block_nbytes(self) -> int:
        """
            Number of bytes in the largest blocks.
        """
        return self._block_nbytes

    @property
    def block_nchars(self) -> int:
        """
            Number of characters in the largest blocks.
        """
        return self._block_nchars

    @property
    def sep_char(self) -> str:
        """
            Optional block separation character.
            It is either the empty string, or a string of length 1.
        """
        return self._sep_char

    @property
    def reverse_blocks(self) -> bool:
        """
            Whether individual char block should be reversed when encoding,
            e.g. as done by the `base45 spec <https://datatracker.ietf.org/doc/draft-faltstrom-base45/>`_.
        """
        return self._reverse_blocks

    def canonical_bytes(self, b: BytesLike) -> bytes:
        self._validate_bytes(b)
        return bytes(b)

    def canonical_string(self, s: str) -> str:
        self._validate_string(s)
        return s

    def _validate_bytes(self, b: BytesLike) -> memoryview:
        b = super()._validate_bytes(b)
        last_block_nbytes = len(b)%self.block_nbytes
        if last_block_nbytes > 0 and last_block_nbytes not in self.nbytes2nchars:
            raise EncodingError(f"Last block of {last_block_nbytes} bytes not allowed.")
        return b

    def _validate_string(self, s: str) -> str:
        validate(s, str)
        sep_char = self.sep_char
        block_nchars = self.block_nchars
        if sep_char:
            char_blocks: List[str] = []
            for idx in range(0, len(s), block_nchars+1):
                char_block = s[idx:idx+block_nchars+1]
                if len(char_block) == block_nchars+1:
                    # intermediate block, must terminate with separator
                    if char_block[-1] != sep_char:
                        raise DecodingError(f"Missing separator at end of block #{idx}")
                    char_blocks.append(char_block[:-1])
                else:
                    # final block
                    char_blocks.append(char_block)
            s = "".join(char_blocks)
        s = super()._validate_string(s)
        last_block_nchars = len(s)%self.block_nchars
        if last_block_nchars > 0 and last_block_nchars not in self.nchars2nbytes:
            raise EncodingError(f"Last block of {last_block_nchars} chars not allowed.")
        return s

    def _encode(self, b: memoryview) -> str:
        zero_char = self.zero_char
        block_nbytes = self.block_nbytes
        nbytes2nchars = self.nbytes2nchars
        reverse_blocks = self.reverse_blocks
        # convert byte blocks into char blocks (all but last are block_nbytes long)
        char_blocks: List[str] = []
        for idx in range(0, len(b), block_nbytes):
            # extract next byte block
            byte_block = b[idx:idx+block_nbytes]
            # simple encoding of byte block
            # s = self._block_encoding.encode(byte_block.lstrip(b"\x00"))
            s = self._block_encoding.encode(_lstrip_memview(byte_block))
            # number of chars in corresponding char block
            block_nchars = nbytes2nchars[len(byte_block)]
            if len(s) > block_nchars:
                raise InvalidByteBlockError(f"Encoded value too large. Block bytes: {list(byte_block)}, encoded chars: {repr(s)}"
                                            f"expected num of encoded chars: {block_nchars}).")
            # pad char block to required number of characters and add to list
            char_block = zero_char*(block_nchars-len(s))+s
            if reverse_blocks:
                char_block = char_block[::-1]
            char_blocks.append(char_block)
        # join character blocks to form encoded string
        return "".join(char_blocks)

    def _decode(self, s: str) -> bytes:
        zero_char = self.zero_char
        block_nchars = self.block_nchars
        nchars2nbytes = self.nchars2nbytes
        reverse_blocks = self.reverse_blocks
        # convert char blocks into byte blocks (all but last are block_nchars long)
        byte_blocks: List[bytes] = []
        for idx in range(0, len(s), block_nchars):
            # extract next char block
            char_block = s[idx:idx+block_nchars]
            if reverse_blocks:
                char_block = char_block[::-1]
            # simple decoding of char block
            b = self._block_encoding.decode(char_block.lstrip(zero_char))
            # number of bytes in corresponding byte block
            block_nbytes = nchars2nbytes[len(char_block)]
            if len(b) > block_nbytes:
                raise InvalidCharBlockError(f"Decoded value too large. Block chars: {repr(char_block)}, decoded bytes: {list(b)}"
                                            f"expected num of decoded bytes: {block_nbytes}).")
            # pad byte block to required number of bytes and add to list
            byte_blocks.append(b"\x00"*(block_nbytes-len(b))+b)
        # join byte blocks to form encoded string
        return b"".join(byte_blocks)

    def options(self, skip_defaults: bool = False) -> Mapping[str, Any]:
        validate(skip_defaults, bool)
        options: Dict[str, Any] = {
            "block_size": self._init_block_size,
        }
        if not skip_defaults or self.sep_char != "":
            options["sep_char"] = self.sep_char
        if not skip_defaults or self.reverse_blocks is not False:
            options["reverse_blocks"] = self.reverse_blocks
        return options

    def with_options(self: BlockBaseEncodingSubclass, **options: Any) -> BlockBaseEncodingSubclass:
        r"""
            Returns a new encoding with the same kind, alphabet and case sensitivity as this one,
            but different options.

            :param options: options to set for the new encoding
            :type options: :obj:`~typing.Dict`\ [:obj:`str`, :obj:`~typing.Any`]

            :rtype: :obj:`BlockBaseEncodingSubclass`
        """
        new_options = {**self.options()}
        for name in options:
            if name not in new_options:
                raise KeyError(f"Unknown option {repr(name)} for {type(self).__name__}")
        new_options.update(options)
        if isinstance(self._init_encoding, BaseEncoding):
            return type(self)(self._init_encoding, case_sensitive=self._init_case_sensitive, **new_options)
        return type(self)(self.alphabet, **new_options)

    def __eq__(self, other: Any) -> bool:
        super_eq = super().__eq__(other)
        if super_eq in (False, NotImplemented):
            return super_eq
        if not isinstance(other, BlockBaseEncoding):
            return NotImplemented
        if isinstance(self._init_encoding, BaseEncoding):
            return self._init_encoding == other._init_encoding and self.case_sensitive == other.case_sensitive
        return True

    def __hash__(self) -> int:
        return hash((type(self), self.alphabet, self.block_encoding, tuple(self.options().items())))

    def __repr__(self) -> str:
        type_name = type(self).__name__
        if isinstance(self._init_encoding, BaseEncoding):
            alphabet_str = f"{self._init_encoding}, case_sensitive={self._init_case_sensitive}"
        else:
            alphabet_str = repr(self.alphabet)
        options = self.options(skip_defaults=True)
        if not options:
            return f"{type_name}({alphabet_str})"
        options_str = ", ".join(f"{name}={repr(value)}" for name, value in options.items())
        return f"{type_name}({alphabet_str}, {options_str})"
