# `bases`: a Python library for general Base-N encodings.

[![Generic badge](https://img.shields.io/badge/python-3.6+-green.svg)](https://docs.python.org/3.6/)
![PyPI version shields.io](https://img.shields.io/pypi/v/bases.svg)
[![PyPI status](https://img.shields.io/pypi/status/bases.svg)](https://pypi.python.org/pypi/bases/)
[![Checked with Mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](https://github.com/python/mypy)
[![Python package](https://github.com/hashberg-io/bases/actions/workflows/python-pytest.yml/badge.svg)](https://github.com/hashberg-io/bases/actions/workflows/python-pytest.yml)
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)


## Table of Contents

- [Install](#install)
- [Usage](#usage)
- [API](#api)
- [Contributing](#contributing)
- [License](#license)


## Install

You can install this package with `pip`:

```
pip install bases
```

## Usage

The core functionality of the library is performed by the `encode` and `decode` methods of base encodings, instances of `BaseEncoding` (or, more precisely, of its concrete subclasses).

Common encodings are associated to pre-defined constants:

```py
>>> from bases import base32
>>> base32
FixcharBaseEncoding(
    StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                   case_sensitive=False),
    pad_char='=', padding='include')
```

The `encode` method can be used to encode bytestrings into strings:

```py
>>> b = bytes([70, 98, 190, 187, 66, 224, 178])
>>> base32.encode(b)
'IZRL5O2C4CZA===='
```

The `decode` method can be used to decode strings into bytestrings:

```py
>>> s = 'IZRL5O2C4CZA===='
>>> base32.decode(s)
b'Fb\xbe\xbbB\xe0\xb2'
>>> list(base32.decode(s))
[70, 98, 190, 187, 66, 224, 178]
```

The `get(name)`, `has(name)`, `make(...)` and `table(prefix="")` functions provide an interface for the programmatic management of encodings.
The [get(name)](https://hashberg-io.github.io/bases/encoding/index.html#bases.encoding.get) function can be used to obtain an existing encoding by name:

```py
>>> import bases
>>> bases.get("base32")
FixcharBaseEncoding(
    StringAlphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                   case_sensitive=False),
    pad_char='=', padding='include')
```

The [make(...)](https://hashberg-io.github.io/bases/encoding/index.html#bases.encoding.make) function can be used to create a new encoding from a given alphabet, encoding kind and options:

```py
>>> bases.make("0123", kind="zeropad-enc", block_nchars=4, name="base4")
ZeropadBaseEncoding(StringAlphabet('0123'), block_nchars=4)
```

The optional keyword argument `name` can be used to register with the library for future retrieval.
The [has(name)](https://hashberg-io.github.io/bases/encoding/index.html#bases.encoding.has) function can be used to check whether an encoding exists by a given name:

```py
>>> bases.has("base4")
True
```

The [table(prefix="")](https://hashberg-io.github.io/bases/encoding/index.html#bases.encoding.table) function can be used to iterate through the existing encoding, optionally filtering by name prefix:

```py
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
```

For further information, please refer to the [API documentation](https://hashberg-io.github.io/bases/bases/index.html).

## API

The [API documentation](https://hashberg-io.github.io/bases/bases/index.html) for this package is automatically generated by [pdoc](https://pdoc3.github.io/pdoc/).


## Contributing

Please see [the contributing file](./CONTRIBUTING.md).


## License

[MIT © Hashberg Ltd.](LICENSE)
