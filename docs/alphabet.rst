Alphabets
=========

Access Alphabets
----------------

To access existing alphabets, use the :func:`~bases.alphabet.get` function:

>>> import bases
>>> alphabet.get("base16")
StringAlphabet('0123456789ABCDEF')


To list alphabets (with optional filtering), use the :func:`~bases.alphabet.table` function:

>>> dict(alphabet.table(prefix="base32"))
{
 'base32': StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567', case_sensitive=False),
 'base32hex': StringAlphabet('0123456789ABCDEFGHIJKLMNOPQRSTUV', case_sensitive=False),
 'base32z': StringAlphabet('ybndrfg8ejkmcpqxot1uwisza345h769', case_sensitive=False)
}


Create Alphabets
----------------

To create new alphabets, use the :func:`~bases.alphabet.make` function:

>>> alphabet.make("0123456789abcdef")
StringAlphabet('0123456789abcdef')

To register new alphabets, use the :func:`~bases.alphabet.register` function:

>>> myalpha = alphabet.make("0123456789abcdef")
>>> alphabet.register(base16lower=myalpha)

Alternatively, you can use the optional ``'name'`` argument of the :func:`~bases.alphabet.make` function:

>>> alphabet.make("0123456789abcdef", name="base16lower")
StringAlphabet('0123456789abcdef')
>>> alphabet.get("base16lower")
StringAlphabet('0123456789abcdef')


Pre-defined Alphabets
---------------------

The following alphabets are pre-defined:

>>> from bases.alphabet import StringAlphabet
>>> for name, alph in bases.alphabet.table():
...     if isinstance(alph, StringAlphabet):
...         desc = alph.chars
...     else: # RangeAlphabet
...         desc = f"codepoints: {alph.codepoints}"
...     print(f"{name:<16}{desc}")
...
base10          0123456789
base16          0123456789ABCDEF
base2           01
base32          ABCDEFGHIJKLMNOPQRSTUVWXYZ234567
base32hex       0123456789ABCDEFGHIJKLMNOPQRSTUV
base32z         ybndrfg8ejkmcpqxot1uwisza345h769
base36          0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ
base45          0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:
base58btc       123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz
base58flickr    123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ
base58ripple    rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz
base64          ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
base64url       ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_
base8           01234567

Common variants (case, case sensitivity, padding) of the above encodings can be obtained via the :meth:`~bases.alphabet.abstract.Alphabet.upper`, :meth:`~bases.alphabet.abstract.Alphabet.lower` and :meth:`~bases.alphabet.abstract.Alphabet.with_case_sensitivity` methods of :class:`~bases.alphabet.abstract.Alphabet` objects.
