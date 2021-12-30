Getting Started
===============

Bases provides a customisable, parametric implementation of several common styles of Base-N encoding, covering all cases appearing in the `multibase specification <https://github.com/multiformats/multibase>`_ (except for proquints).


Installation
------------

You can install the latest release from `PyPI <https://pypi.org/project/bases/>`_ as follows:

.. code-block:: console

    $ pip install --upgrade bases

GitHub repo: https://github.com/hashberg-io/bases

Basic Usage
-----------

We suggest you import bases as follows:

>>> import bases

The core functionality of the library is performed by the :meth:`~bases.encoding.base.BaseEncoding.encode` and :meth:`~bases.encoding.base.BaseEncoding.decode` methods of :class:`~bases.encoding.base.BaseEncoding` objects (more specifically, instances of its concrete subclasses):

Common encodings are associated to pre-defined constants, for ease of use:

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


Programmatic Management
-----------------------

The :func:`~bases.encoding.get`, :func:`~bases.encoding.has`, :func:`~bases.encoding.make`, :func:`~bases.encoding.table`, :func:`~bases.encoding.register` and :func:`~bases.encoding.unregister` functions provide an interface for programmatic management of base encodings:

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
