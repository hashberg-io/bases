"""
    Zero-padded base encodings.

    Similar to :mod:`~bases.encoding.simple` base encodings, but additionally:

    - preserves leading zeros
    - optionally enforces a fixed block size for encoded strings and decoded bytestrings

    Constructor options:

    - ``block_nbytes: int`` number of bytes in a block for decoded bytestrings (default: 1)
    - ``block_nchars: int`` number of chars in a block for encoded strings (default: 1)

    The static method :meth:`ZeropadBaseEncoding.max_block_nchars` (resp. :meth:`ZeropadBaseEncoding.max_block_nbytes`) gives the
    maximum block size in chars (resp. bytes) that can be used for a given block size in bytes (resp. chars).
    This is to ensure that encoding/decoding can always be performed unambiguously.

    Encoding of a bytestring ``b``:

    1. count the number Z of leading zero byte blocks in ``b`` and strip them (default: count zero bytes and strip them)
    2. encode ``b`` as a :mod:`~bases.encoding.simple` base encoding would
    3. prepend the minimum number of zero chars necessary to make the encoded string length an integral multiple of ``block_nchars``
    4. prepend Z zero char blocks to the encoded string

    Decoding of a string ``s``:

    1. count the number Z of leading zero char blocks in ``s`` and strip them (default: count zero chars and strip them)
    2. decode ``s`` as a :mod:`~bases.encoding.simple` base encoding would
    3. prepend the minimum number of zero bytes necessary to make the decoded bytestring length an integral multiple of ``block_nbytes``
    4. prepend Z zero byte blocks to the encoded string
"""

from __future__ import annotations

import math
from typing import Any, Dict, Mapping, Optional, Union
from typing_validation import validate

from bases.alphabet import Alphabet
from .base import BaseEncoding, _lstrip_memview
from .simple import SimpleBaseEncoding

class ZeropadBaseEncoding(BaseEncoding):
    """
        Zero-added base encodings.

        :param alphabet: the alphabet to use for the encoding
        :type alphabet: :obj:`str`, :obj:`range` or :class:`~bases.alphabet.abstract.Alphabet`
        :param case_sensitive: optional case sensitivity (if :obj:`None`, the one from the alphabet is used)
        :type case_sensitive: :obj:`bool` or :obj:`None`, *optional*
        :param block_nbytes: number of bytes in a block for decoded bytestrings (default: 1)
        :type block_nbytes: :obj:`int`, *optional*
        :param block_nchars: number of chars in a block for encoded strings (default: 1)
        :type block_nchars: :obj:`int`, *optional*
    """

    _simple_encoding: SimpleBaseEncoding
    _block_nbytes: int
    _block_nchars: int

    def __init__(self, alphabet: Union[str, range, Alphabet], *,
                 case_sensitive: Optional[bool] = None,
                 block_nbytes: int = 1,
                 block_nchars: int = 1):
        validate(block_nbytes, int)
        validate(block_nchars, int)
        super().__init__(alphabet, case_sensitive=case_sensitive)
        self._simple_encoding = SimpleBaseEncoding(self.alphabet)
        self._block_nbytes = block_nbytes
        self._block_nchars = block_nchars
        self.__validate_init()

    def __validate_init(self) -> None:
        base = self.base
        block_nbytes = self.block_nbytes
        block_nchars = self.block_nchars
        max_block_nbytes = ZeropadBaseEncoding.max_block_nbytes(base, block_nchars)
        max_block_nchars = ZeropadBaseEncoding.max_block_nchars(base, block_nbytes)
        if block_nchars > max_block_nchars:
            raise ValueError(f"Number of characters allowed per zero-padding block is too large: "
                             f"the maximum for base = {base} and block_nbytes = {block_nbytes} is "
                             f"block_nchars = {max_block_nchars}")
        if block_nbytes > max_block_nbytes:
            raise ValueError(f"Number of bytes allowed per zero-padding block is too large: "
                             f"the maximum for base = {base} and block_nchars {block_nchars} is "
                             f"block_nbytes = {max_block_nbytes}")

    @staticmethod
    def max_block_nchars(base: int, block_nbytes: int) -> int:
        """
            Returns the maximum integer value for ``block_chars`` such that:


            .. code-block:: python

                256**block_nbytes > base**(block_nchars-1)

            :param block_nbytes: number of bytes in a block for decoded bytestrings
            :type block_nbytes: :obj:`int`
        """
        validate(base, int)
        validate(block_nbytes, int)
        if base <= 1:
            raise ValueError("Base must be >= 2.")
        if block_nbytes <= 0:
            raise ValueError("Number of bytes per zero-padding block must be positive.")
        _max_nc = block_nbytes/math.log(base, 256)+1
        _max_nc_floor = int(math.floor(_max_nc))
        return _max_nc_floor if _max_nc > _max_nc_floor else _max_nc_floor-1


    @staticmethod
    def max_block_nbytes(base: int, block_nchars: int) -> int:
        """
            Returns the maximum integer value for ``block_nbytes`` such that:

            .. code-block:: python

                base**block_nchars > 256**(block_nbytes-1)

            :param block_nchars: number of chars in a block for encoded strings
            :type block_nchars: :obj:`int`
        """
        validate(base, int)
        validate(block_nchars, int)
        if base <= 1:
            raise ValueError("Base must be >= 2.")
        if block_nchars <= 0:
            raise ValueError("Number of chars per zero-padding block must be positive.")
        _max_nb = block_nchars/math.log(256, base)+1
        _max_nb_floor = int(math.floor(_max_nb))
        return _max_nb_floor if _max_nb > _max_nb_floor else _max_nb_floor-1


    @property
    def block_nbytes(self) -> int:
        """
            Number of bytes in a block.
        """
        return self._block_nbytes

    @property
    def block_nchars(self) -> int:
        """
            Number of characters in a block.
        """
        return self._block_nchars


    def _num_canonical_bytes(self, b: memoryview) -> int:
        self._validate_bytes(b)
        block_nbytes = self.block_nbytes
        extra_bytes = len(b)%block_nbytes
        if extra_bytes == 0:
            return len(b)
            # return b
        return (block_nbytes-extra_bytes)+len(b)
        # return bytes(chain(repeat(0, block_nbytes-extra_bytes), iter(b)))
        # return b"\x00"*(block_nbytes-extra_bytes)+b

    def _canonical_string(self, s: str) -> str:
        self._validate_string(s)
        block_nchars = self.block_nchars
        extra_chars = len(s)%block_nchars
        if extra_chars == 0:
            return s
        return self.zero_char*(block_nchars-extra_chars)+s

    def _encode(self, b: memoryview) -> str:
        canonical_nbytes = self._num_canonical_bytes(b)
        block_nbytes = self.block_nbytes
        block_nchars = self.block_nchars
        zero_char = self.zero_char
        # strip leading zero bytes
        # b_stripped = b.lstrip(b"\x00")
        b_stripped = _lstrip_memview(b)
        # compute simple base encoding
        s = self._simple_encoding.encode(b_stripped)
        # pad simple base encoding to integral multiple of block char size
        extra_chars = len(s)%block_nchars
        if extra_chars != 0:
            s = zero_char*(block_nchars-extra_chars)+s
        # count leading zero blocks
        num_zero_blocks = (canonical_nbytes-len(b_stripped))//block_nbytes
        # return zero-padded base encoding
        s = zero_char*num_zero_blocks*block_nchars+s
        return s

    def _decode(self, s: str) -> bytes:
        s = self._canonical_string(s)
        block_nbytes = self.block_nbytes
        block_nchars = self.block_nchars
        # strip leading zero chars
        s_stripped = s.lstrip(self.zero_char)
        # compute simple base decoding
        b = self._simple_encoding.decode(s_stripped)
        # pad simple base decoding to integral multiple of block byte size
        extra_bytes = len(b)%block_nbytes
        if extra_bytes != 0:
            b = b"\x00"*(block_nbytes-extra_bytes)+b
        # compute leading zero blocks
        num_zero_blocks = (len(s)-len(s_stripped))//block_nchars
        # return zero-padded base decoding
        b = b"\x00"*num_zero_blocks*block_nbytes+b
        return b

    def options(self, skip_defaults: bool = False) -> Mapping[str, Any]:
        validate(skip_defaults, bool)
        options: Dict[str, Any] = {}
        if not skip_defaults or self.block_nbytes != 1:
            options["block_nbytes"] = self.block_nbytes
        if not skip_defaults or self.block_nchars != 1:
            options["block_nchars"] = self.block_nchars
        return options
