Encodings
=========

Access encodings
----------------

To access existing encodings, use the :func:`~bases.encoding.get` function:

>>> from bases import encoding
>>> encoding.get("base32")
FixcharBaseEncoding(
    StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                   case_sensitive=False),
    pad_char='=', padding='include')

To list alphabets (with optional filtering), use the :func:`~bases.encoding.table` function:

>>> dict(encoding.table(prefix="base32"))
{
 'base32':      FixcharBaseEncoding(
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


Create encodings
----------------

To create new encodings, use the :func:`~bases.encoding.make` function:

>>> encoding.make("0123", kind="zeropad-enc", block_nchars=4)
ZeropadBaseEncoding(StringAlphabet('0123'), block_nchars=4)

To register new encodings, use the :func:`~bases.encoding.register` function:

>>> myenc = encoding.get("base16").lower()
>>> encoding.register(base16lower=myenc)
>>> encoding.get("base16lower")
ZeropadBaseEncoding(
    StringAlphabet('0123456789abcdef',
                   case_sensitive=False),
    block_nchars=2)

Alternatively, you can use the optional ``'name'`` argument of the :func:`~bases.encoding.make` function:

>>> encoding.make("0123", kind="zeropad-enc", block_nchars=4, name="base4")
ZeropadBaseEncoding(StringAlphabet('0123'), block_nchars=4)
>>> encoding.get("base4")
ZeropadBaseEncoding(StringAlphabet('0123'), block_nchars=4)


Pre-defined Base Encodings
--------------------------

The following base encodings are pre-defined:

>>> for name, enc in bases.table():
...     print(f"{name:<16}{type(enc).__name__[:-12]}")
...
base10          Zeropad
base16          Zeropad
base2           Zeropad
base32          Fixchar
base32hex       Fixchar
base32z         Fixchar
base36          Zeropad
base45          Block
base58btc       Zeropad
base58flickr    Zeropad
base58ripple    Zeropad
base64          Fixchar
base64url       Fixchar
base8           Fixchar

Common variants (case, case sensitivity, padding) of the above encodings can be obtained via the :meth:`~bases.encoding.base.BaseEncoding.upper`, :meth:`~bases.encoding.base.BaseEncoding.lower` and :meth:`~bases.encoding.base.BaseEncoding.with_case_sensitivity` methods of :class:`~bases.encoding.base.BaseEncoding` objects and via the :meth:`~bases.encoding.fixchar.FixcharBaseEncoding.pad` and :meth:`~bases.encoding.fixchar.FixcharBaseEncoding.nopad` methods of :class:`~bases.encoding.fixchar.FixcharBaseEncoding` objects.
