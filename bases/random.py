"""
    Functions to generate random data.
"""

from __future__ import annotations

# pylint: disable = global-statement

from contextlib import contextmanager
from itertools import chain, islice
from random import Random # pylint: disable = import-self
from types import MappingProxyType
from typing import Any, Dict, Iterator, Mapping, Optional
from typing_validation import validate

from .alphabet import Alphabet
from .encoding import BaseEncoding, SimpleBaseEncoding, ZeropadBaseEncoding, BlockBaseEncoding, FixcharBaseEncoding


_default_options: Mapping[str, Any] = MappingProxyType({
    "min_bytes": 0,
    "max_bytes": 16,
    "min_chars": 0,
    "max_chars": 16,
})


_options: Mapping[str, Any] = MappingProxyType(_default_options)
_rand: Random = Random(0)


def reset_options() -> None:
    """
        Resets random generation options to their default values.
    """
    global _options
    global _rand
    _options = _default_options
    _rand = Random(0)


def default_options() -> Mapping[str, Any]:
    """
        Readonly view of the default random generation options.
    """
    return _default_options


def get_options() -> Mapping[str, Any]:
    """
        Readonly view of the current random generation options.
    """
    return _options


@contextmanager
def options(*,
            seed: Optional[int] = None,
            min_bytes: Optional[int] = None,
            max_bytes: Optional[int] = None,
            min_chars: Optional[int] = None,
            max_chars: Optional[int] = None,) -> Iterator[None]:
    """
        Returns with-statement context manager for temporary option setting:

        .. code-block:: python

            with options(**options):
                for value in rand_data(num_samples, encoding):
                    ...

        See :func:`set_options` for a description of the options.
    """
    # pylint: disable = too-many-locals
    for arg in (seed, min_bytes, max_bytes, min_chars, max_chars):
        validate(arg, Optional[int])
    global _options
    global _rand
    _old_options = _options
    _old_rand = _rand
    try:
        set_options(seed=seed,
                    min_bytes=min_bytes, max_bytes=max_bytes,
                    min_chars=min_chars, max_chars=max_chars,)
        yield
    finally:
        _options = _old_options
        _rand = _old_rand


def set_options(*,
                seed: Optional[int] = None,
                min_bytes: Optional[int] = None,
                max_bytes: Optional[int] = None,
                min_chars: Optional[int] = None,
                max_chars: Optional[int] = None,) -> None:
    """
        Permanently sets random generation options:

        .. code-block:: python

            seed: int           # set new random number generator, with this seed
            min_bytes: int      # min length of `bytes` value
            max_bytes: int      # max length of `bytes` value
            min_chars: int      # min length of `str` value
            max_chars: int      # max length of `str` value

    """
    # pylint: disable = too-many-branches, too-many-locals, too-many-statements
    for arg in (seed, min_bytes, max_bytes, min_chars, max_chars):
        validate(arg, Optional[int])
    global _options
    global _rand
    # set newly passed options
    _new_options: Dict[str, Any] = {}
    if seed is not None:
        _rand = Random(seed)
    if min_bytes is not None:
        if min_bytes < 0:
            raise ValueError("Value for min_bytes is negative.")
        _new_options["min_bytes"] = min_bytes
    if max_bytes is not None:
        if max_bytes < 0:
            raise ValueError("Value for max_bytes is negative.")
        _new_options["max_bytes"] = max_bytes
    if min_chars is not None:
        if min_chars < 0:
            raise ValueError("Value for min_chars is negative.")
        _new_options["min_chars"] = min_chars
    if max_chars is not None:
        if max_chars < 0:
            raise ValueError("Value for max_chars is negative.")
        _new_options["max_chars"] = max_chars
    # pass-through other options with former values
    for k, v in _options.items():
        if k not in _new_options:
            _new_options[k] = v
    # check compatibility conditions
    if _new_options["min_bytes"] > _new_options["max_bytes"]:
        raise ValueError("Value for min_bytes is larger than value for max_bytes.")
    if _new_options["min_chars"] > _new_options["max_chars"]:
        raise ValueError("Value for min_chars is larger than value for max_chars.")
    # update options
    _options = MappingProxyType(_new_options)


def rand_bytes(n: Optional[int] = None, *, encoding: Optional[BaseEncoding] = None) -> Iterator[bytes]:
    """
        Generates a stream of random :obj:`bytes` objects.
        If a number ``n`` is given, that number of samples is yelded.
        If an encoding ``encoding`` is given, only bytes valid for that encoding are yielded.

        Example usage:

        >>> my_random_bytes = list(random.rand_bytes(4, encoding=base10))
        >>> [list(b) for b in my_random_bytes]
        [[0, 30, 135, 156, 223, 90, 134, 83, 6, 243, 245],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 49, 216, 87, 1, 2],
         [70, 98, 190, 187, 66, 224, 178],
         [0, 96, 63]]

        :param n: the number of samples
        :type n: :obj:`int` or :obj:`None`, *optional*
        :param encoding: optional encoding for which the bytestrings must be valid
        :type encoding: :obj:`~bases.encoding.base.BaseEncoding` or :obj:`None`, *optional*

    """
    validate(n, Optional[int])
    validate(encoding, Optional[BaseEncoding])
    if encoding is None:
        return rand_raw_bytes(n)
    if isinstance(encoding, SimpleBaseEncoding):
        return _rand_bytes_simple_enc(n, encoding)
    if isinstance(encoding, ZeropadBaseEncoding):
        return _rand_bytes_zeropad_enc(n, encoding)
    if isinstance(encoding, BlockBaseEncoding):
        return _rand_bytes_block_enc(n, encoding)
    if isinstance(encoding, FixcharBaseEncoding):
        return _rand_bytes_fixedchar_enc(n, encoding)
    raise ValueError(f"Unsupported encoding type {type(encoding)}")


def rand_raw_bytes(n: Optional[int] = None, *, min_bytes: Optional[int] = None, max_bytes: Optional[int] = None) -> Iterator[bytes]:
    """
        Generates a stream of random :obj:`bytes` objects.
        If a number ``n`` is given, that number of samples is yelded.
        The optional ``min_bytes`` and ``max_bytes`` parameters can be used to set a minimum/maximum length
        for the :obj:`bytes` objects: if :obj:`None`, the values are fetched from :func:`get_options`.

        :param n: the number of samples
        :type n: :obj:`int` or :obj:`None`, *optional*
        :param min_bytes: the minimum length for the bytestrings
        :type min_bytes: :obj:`int` or :obj:`None`, *optional*
        :param max_bytes: the maximum length for the bytestrings
        :type max_bytes: :obj:`int` or :obj:`None`, *optional*
    """
    validate(n, Optional[int])
    validate(min_bytes, Optional[int])
    validate(max_bytes, Optional[int])
    if n is not None and n < 0:
        raise ValueError()
    if min_bytes is None:
        min_bytes = _options["min_bytes"]
    if max_bytes is None:
        max_bytes = _options["max_bytes"]
    rand = _rand
    # main yielding loop
    yielded = 0
    while n is None or yielded < n:
        # sample random length
        l = rand.randint(min_bytes, max_bytes)
        # yield random unsigned integer filling l bytes
        i = rand.randrange(0, 256**l)
        yield i.to_bytes(l, byteorder="big")
        yielded += 1


def _rand_bytes_simple_enc(n: Optional[int], _: SimpleBaseEncoding) -> Iterator[bytes]:
    if n is not None and n < 0:
        raise ValueError()
    min_bytes = _options["min_bytes"]
    max_bytes = _options["max_bytes"]
    rand = _rand
    # main yielding loop
    yielded = 0
    while n is None or yielded < n:
        # sample random length
        l = rand.randint(min_bytes, max_bytes)
        # yield random unsigned integer filling l bytes with no leading zero bytes
        if l == 0:
            i = 0
        else:
            i = rand.randrange(256**(l-1), 256**l)
        yield i.to_bytes(l, byteorder="big")
        yielded += 1

def _rand_bytes_zeropad_enc(n: Optional[int], _: ZeropadBaseEncoding) -> Iterator[bytes]:
    if n is not None and n < 0:
        raise ValueError()
    min_bytes = _options["min_bytes"]
    max_bytes = _options["max_bytes"]
    rand = _rand
    # main yielding loop
    yielded = 0
    while n is None or yielded < n:
        # sample random length
        l = rand.randint(min_bytes, max_bytes)
        # sample random number of leading zero bytes
        z = rand.randint(0, l)
        # yield random unsigned integer filling l-z bytes
        if l == z:
            i = 0
        else:
            i = rand.randrange(256**(l-z-1), 256**(l-z))
        yield i.to_bytes(l, byteorder="big")
        yielded += 1

def _rand_bytes_block_enc(n: Optional[int], encoding: BlockBaseEncoding) -> Iterator[bytes]:
    if n is not None and n < 0:
        raise ValueError()
    min_bytes = _options["min_bytes"]
    max_bytes = _options["max_bytes"]
    rand = _rand
    # pre-compute valid bytestring lengths for block base encoding
    block_nbytes = encoding.block_nbytes
    nbytes2nchars = encoding.nbytes2nchars
    valid_lengths = [l for l in range(min_bytes, max_bytes+1)
                     if l%block_nbytes == 0 or l%block_nbytes in nbytes2nchars]
    # main yielding loop
    yielded = 0
    while n is None or yielded < n:
        # sample random valid length
        l = rand.choice(valid_lengths)
        # yield random unsigned integer filling l bytes
        i = rand.randrange(0, 256**l)
        yield i.to_bytes(l, byteorder="big")
        yielded += 1


def _rand_bytes_fixedchar_enc(n: Optional[int], _: FixcharBaseEncoding) -> Iterator[bytes]:
    return rand_raw_bytes(n)


def rand_str(n: Optional[int] = None, *, encoding: Optional[BaseEncoding]=None, alphabet: Optional[Alphabet]=None) -> Iterator[str]:
    """
        Generates a stream of random strings.
        If a number ``n`` is given, that number of samples is yelded.
        Exactly one of ``encoding`` or ``alphabet`` must be given:
        - if an ``encoding`` is given, only strings valid for that encoding are yielded
        - if an ``alphabet`` is given, only strings valid for that alphabet are yielded

        Example usage:

        >>> my_random_strings = list(random.rand_str(4, encoding=base32))
        >>> my_random_strings
        ['2CQ7ZT6WNI', 'IGQJTGA', 'V6GW3UN64QDAFZA7', 'PUEMOPJ4']

        :param n: the number of samples
        :type n: :obj:`int` or :obj:`None`, *optional*
        :param encoding: optional encoding for which the strings must be valid
        :type encoding: :obj:`~bases.encoding.base.BaseEncoding` or :obj:`None`, *optional*
        :param alphabet: optional alphabet for which the bytestrings must be valid
        :type alphabet: :obj:`~bases.alphabet.abstract.Alphabet` or :obj:`None`, *optional*

        :raises ValueError: unless exactly one of ``encoding`` or ``alphabet`` is specified
        :raises ValueError: if an instance of a an unsupported (i.e. custom) base encoding subclass is passed to ``encoding``

    """
    validate(n, Optional[int])
    validate(encoding, Optional[BaseEncoding])
    validate(alphabet, Optional[Alphabet])
    if encoding is None:
        if alphabet is None:
            raise ValueError("One of 'encoding' or 'alphabet' must be specified.")
        return _rand_alphabet_string(n, alphabet)
    if alphabet is not None:
        raise ValueError("Exactly one of 'encoding' or 'alphabet' must be specified.")
    if isinstance(encoding, SimpleBaseEncoding):
        return _rand_str_simple_enc(n, encoding)
    if isinstance(encoding, ZeropadBaseEncoding):
        return _rand_str_zeropad_enc(n, encoding)
    if isinstance(encoding, BlockBaseEncoding):
        return _rand_str_block_enc(n, encoding)
    if isinstance(encoding, FixcharBaseEncoding):
        return _rand_str_fixedchar_enc(n, encoding)
    raise ValueError(f"Unsupported encoding type {type(encoding)}")

def rand_char(n: Optional[int] = None, *, alphabet: Alphabet, non_zero: bool = False) -> Iterator[str]:
    """
        Generates a stream of random characters from the alphabet (one character yielded at a time).
        If a number ``n`` is given, that number of samples is yelded.
        If ``non_zero`` is :obj:`True`, the zero character for the alphabet is not yielded.

        :param n: the number of samples
        :type n: :obj:`int` or :obj:`None`, *optional*
        :param alphabet: optional alphabet for which the characters must be valid
        :type alphabet: :obj:`~bases.alphabet.abstract.Alphabet` or :obj:`None`, *optional*
        :param non_zero: whether to exclude the zero character for the alphabet
        :type non_zero: :obj:`bool`, *optional*
    """
    if n is not None and n < 0:
        raise ValueError()
    start = 1 if non_zero else 0
    end = len(alphabet)
    rand = _rand
    yielded = 0
    while n is None or yielded < n:
        # yield random character (excluding zero character, if non_zero is True)
        idx = rand.randrange(start, end)
        yield alphabet[idx]
        yielded += 1

def _rand_alphabet_string(n: Optional[int], alphabet: Alphabet) -> Iterator[str]:
    if n is not None and n < 0:
        raise ValueError()
    min_chars = _options["min_chars"]
    max_chars = _options["max_chars"]
    rand = _rand
    # infinte random character stream
    rand_char_stream = rand_char(alphabet=alphabet)
    # main yielding loop
    yielded = 0
    while n is None or yielded < n:
        # sample random length
        l = rand.randint(min_chars, max_chars)
        # yield random string filling l characters
        yield "".join(islice(rand_char_stream, l))
        yielded += 1


def _rand_str_simple_enc(n: Optional[int], encoding: SimpleBaseEncoding) -> Iterator[str]:
    if n is not None and n < 0:
        raise ValueError()
    min_chars = _options["min_chars"]
    max_chars = _options["max_chars"]
    rand = _rand
    # infinte random character streams
    rand_char_stream = rand_char(alphabet=encoding.alphabet)
    rand_nonzero_char_stream = rand_char(alphabet=encoding.alphabet, non_zero=True)
    # main yielding loop
    yielded = 0
    while n is None or yielded < n:
        # sample random length
        l = rand.randint(min_chars, max_chars)
        # yield random str filling l characters with no leading zero characters
        if l == 0:
            yield ""
        else:
            yield "".join(chain(islice(rand_nonzero_char_stream, 1),
                                islice(rand_char_stream, l-1)))
        yielded += 1


def _rand_str_zeropad_enc(n: Optional[int], encoding: ZeropadBaseEncoding) -> Iterator[str]:
    if n is not None and n < 0:
        raise ValueError()
    min_chars = _options["min_chars"]
    max_chars = _options["max_chars"]
    rand = _rand
    # zero character
    zero_char = encoding.zero_char
    # infinte random character streams
    rand_char_stream = rand_char(alphabet=encoding.alphabet)
    rand_nonzero_char_stream = rand_char(alphabet=encoding.alphabet, non_zero=True)
    # main yielding loop
    yielded = 0
    while n is None or yielded < n:
        # sample random length
        l = rand.randint(min_chars, max_chars)
        # sample random number of leading zero chars
        z = rand.randint(0, l)
        # yield random str filling l characters with given number of leading zeros
        if l-z == 0:
            yield zero_char*z
        else:
            yield zero_char*z+"".join(chain(islice(rand_nonzero_char_stream, 1),
                                            islice(rand_char_stream, l-z-1)))
        yielded += 1

def rand_block_chars(n: Optional[int] = None, *, block_nchars: int, encoding: BlockBaseEncoding) -> Iterator[str]:
    """
        Generates a stream of random char blocks for a block base encoding.
        If a number ``n`` is given, that number of samples is yelded.
        The number ``block_nchars`` of characters in the blocks must be valid for the encoding.

        :param n: the number of samples
        :type n: :obj:`int` or :obj:`None`, *optional*
        :param block_nchars: the number of characters in a block
        :type block_nchars: :obj:`int`
        :param encoding: block encoding for which the char blocks must be valid
        :type encoding: :obj:`~bases.encoding.block.BlockBaseEncoding`
    """
    if n is not None and n < 0:
        raise ValueError()
    # extract block size in chars and bytes
    nchars2nbytes = encoding.nchars2nbytes
    if block_nchars not in nchars2nbytes:
        raise ValueError(f"Invalid number of characters per block ({block_nchars})")
    block_nbytes = nchars2nbytes[block_nchars]
    # infinite random byte stream
    rand_bytes_stream = rand_raw_bytes(min_bytes=1, max_bytes=1)
    # main yielding loop
    yielded = 0
    while n is None or yielded < n:
        block_bytes = b"".join(islice(rand_bytes_stream, block_nbytes))
        s = encoding.encode(block_bytes)
        yield s
        yielded += 1

def _rand_str_block_enc(n: Optional[int], encoding: BlockBaseEncoding) -> Iterator[str]:
    if n is not None and n < 0:
        raise ValueError()
    min_chars = _options["min_chars"]
    max_chars = _options["max_chars"]
    rand = _rand
    # pre-compute valid string lengths for block base encoding
    block_nchars = encoding.block_nchars
    nchars2nbytes = encoding.nchars2nbytes
    valid_lengths = [l for l in range(min_chars, max_chars+1)
                     if l%block_nchars == 0 or l%block_nchars in nchars2nbytes]
    # infinte random character streams
    rand_block_stream = {
        nchars: rand_block_chars(block_nchars=nchars, encoding=encoding)
        for nchars in nchars2nbytes
    }
    # main yielding loop
    yielded = 0
    while n is None or yielded < n:
        # sample random valid length
        l = rand.choice(valid_lengths)
        num_full_blocks, final_block_nchars = divmod(l, block_nchars)
        full_blocks = islice(rand_block_stream[block_nchars], num_full_blocks)
        if final_block_nchars == 0:
            yield "".join(full_blocks)
        else:
            final_block = islice(rand_block_stream[final_block_nchars], 1)
            yield "".join(chain(full_blocks, final_block))
        yielded += 1

def _rand_str_fixedchar_enc(n: Optional[int], encoding: FixcharBaseEncoding) -> Iterator[str]:
    # pylint: disable = too-many-locals
    if n is not None and n < 0:
        raise ValueError()
    min_chars = _options["min_chars"]
    max_chars = _options["max_chars"]
    rand = _rand
    # pre-compute valid string lengths for fixed-char base encoding
    alphabet = encoding.alphabet
    char_nbits = encoding.char_nbits
    valid_lengths = [l for l in range(min_chars, max_chars+1)
                     if (l*char_nbits)%8 < char_nbits]
    # infinte random character stream
    rand_char_stream = rand_char(alphabet=encoding.alphabet)
    # main yielding loop
    yielded = 0
    while n is None or yielded < n:
        # sample random length
        l = rand.choice(valid_lengths)
        # yield random str filling l characters with pad bits set to zero
        extra_nbits = (l*char_nbits)%8
        if extra_nbits == 0:
            s = "".join(islice(rand_char_stream, l))
        else:
            all_chars_but_last = "".join(islice(rand_char_stream, l-1))
            last_char_idx = rand.randrange(0, 2**(char_nbits-extra_nbits))<<extra_nbits
            last_char = alphabet[last_char_idx]
            s = all_chars_but_last+last_char
        if encoding.padding == "ignore":
            yield s
        else:
            yield encoding.pad_string(s)
        yielded += 1
