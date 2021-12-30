Random data
===========

The :mod:`~bases.random` module provides functionality to generate random Base-N data, via the :func:`bases.random.rand_bytes` and :func:`bases.random.rand_str` functions:

- the function call ``rand_bytes(n)`` returns an iterator yielding a stream of ``n`` random bytestrings
- the function call ``rand_bytes(n, encoding=enc)`` returns an iterator yielding a stream of ``n`` random bytestrings valid for the encoding
  (i.e. they should be encoded without error)
- the function call ``rand_str(n, encoding=enc)`` returns an iterator yielding a stream of ``n`` random strings valid for the encoding
  (i.e. they should be decoded without error)
- the function call ``rand_str(n, alphabet=alph)`` returns an iterator yielding a stream of ``n`` random strings with characters from the alphabet
- the function call ``rand_bytes()`` returns an iterator yielding an infinite stream of random bytestrings
- the function call ``rand_bytes(encoding=enc)`` returns an iterator yielding an infinite stream of random bytestrings valid for the encoding
- the function call ``rand_str(encoding=enc)`` returns an iterator yielding an infinite stream of random strings valid for the encoding
- the function call ``rand_str(alphabet=alph)`` returns an iterator yielding an infinite stream of random strings with characters from the alphabet


Generate random data
--------------------

Example of random base data generation:

>>> from bases import base10, base32
>>> from bases import random
>>> my_random_bytes = list(random.rand_bytes(4, encoding=base10))
>>> [list(b) for b in my_random_bytes]
[[0, 30, 135, 156, 223, 90, 134, 83, 6, 243, 245],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 49, 216, 87, 1, 2],
 [70, 98, 190, 187, 66, 224, 178],
 [0, 96, 63]]
>>> my_random_strings = list(random.rand_str(4, encoding=base32))
>>> my_random_strings
['2CQ7ZT6WNI', 'IGQJTGA', 'V6GW3UN64QDAFZA7', 'PUEMOPJ4']


Random generation options
-------------------------

The :func:`bases.random.options` context manager is used to set options temporarily, within the scope of a ``with`` directive:

- ``min_bytes`` and ``max_bytes`` set bounds on the length of bytestrings yielded by ``rand_bytes``
- ``min_chars`` and ``max_chars`` set bounds on the length of strings yielded by ``rand_str``

Options can be set with :func:`bases.random.set_options` and reset with :func:`bases.random.reset_options`.
A read-only view on options can be obtained from :func:`bases.random.get_options`, and a read-only view on default options can be obtained from :func:`bases.random.default_options`:

>>> random.default_options()
mappingproxy({'min_bytes': 0, 'max_bytes': 16,
              'min_chars': 0, 'max_chars': 16})
