bases: A Python library for Base-N encodings
============================================

.. image:: https://img.shields.io/badge/python-3.7+-green.svg
    :target: https://docs.python.org/3.7/
    :alt: Python versions

.. image:: https://img.shields.io/pypi/v/bases.svg
    :target: https://pypi.python.org/pypi/bases/
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/status/bases.svg
    :target: https://pypi.python.org/pypi/bases/
    :alt: PyPI status

.. image:: http://www.mypy-lang.org/static/mypy_badge.svg
    :target: https://github.com/python/mypy
    :alt: Checked with Mypy
    
.. image:: https://readthedocs.org/projects/bases/badge/?version=latest
    :target: https://bases.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://github.com/hashberg-io/bases/actions/workflows/python-pytest.yml/badge.svg
    :target: https://github.com/hashberg-io/bases/actions/workflows/python-pytest.yml
    :alt: Python package status

.. image:: https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square
    :target: https://github.com/RichardLitt/standard-readme
    :alt: standard-readme compliant


Bases provides a customisable, parametric implementation of several common styles of Base-N encoding, covering all cases appearing in the `multibase specification <https://github.com/multiformats/multibase>`_ (except for proquints).


.. contents::


Install
-------

You can install the latest release from `PyPI <https://pypi.org/project/bases/>`_ as follows:

.. code-block:: console

    $ pip install --upgrade bases


Usage
-----

We suggest you import bases as follows:

>>> import bases


Below are some basic usage examples, to get you started: for detailed documentation, see https://bases.readthedocs.io/


Base encoding objects
^^^^^^^^^^^^^^^^^^^^^

>>> from bases import base32
>>> base32
FixcharBaseEncoding(
    StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                   case_sensitive=False),
    pad_char='=', padding='include')


Encoding
^^^^^^^^

>>> b = bytes([70, 98, 190, 187, 66, 224, 178])
>>> base32.encode(b)
'IZRL5O2C4CZA===='


Decoding
^^^^^^^^

>>> s = 'IZRL5O2C4CZA===='
>>> base32.decode(s)
b'Fb\xbe\xbbB\xe0\xb2'
>>> list(base32.decode(s))
[70, 98, 190, 187, 66, 224, 178]


Case/padding variations
^^^^^^^^^^^^^^^^^^^^^^^

>>> b = bytes([70, 98, 190, 187, 66, 224, 178])
>>> base32.encode(b)
'IZRL5O2C4CZA===='
>>> base32lower = base32.lower()
>>> base32lower
FixcharBaseEncoding(
    StringAlphabet('abcdefghijklmnopqrstuvwxyz234567',
                   case_sensitive=False),
    pad_char='=', padding='include')
>>> base32lower.encode(b)
'izrl5o2c4cza===='
>>> base32nopad = base32.nopad()
>>> base32nopad.encode(b)
'IZRL5O2C4CZA'


Case sensitivity variations
^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> s = 'IZRL5O2C4CZA===='
>>> base32lower.decode(s)
b'Fb\xbe\xbbB\xe0\xb2'
>>> base32lower_casesensitive = base32lower.with_case_sensitivity(True)
>>> base32lower_casesensitive.decode(s)
bases.encoding.errors.NonAlphabeticCharError: Invalid character 'I'
encountered for alphabet StringAlphabet('abcdefghijklmnopqrstuvwxyz234567').


Custom base encodings
^^^^^^^^^^^^^^^^^^^^^

>>> base4 = bases.make("0123", kind="zeropad-enc", block_nchars=4)
>>> base4
ZeropadBaseEncoding(StringAlphabet('0123'), block_nchars=4)



API
---

For the full API documentation, see https://bases.readthedocs.io/


Contributing
------------

Please see `<CONTRIBUTING.md>`_.


License
-------

`MIT © Hashberg Ltd. <LICENSE>`_
