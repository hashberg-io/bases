# pylint: disable = missing-docstring

import pytest
from base58 import b58encode, b58decode

from bases import alphabet
from bases.encoding import base58btc
from bases import random
from bases.random import rand_bytes, rand_str

_base58_testvecs = {
    # from https://datatracker.ietf.org/doc/html/draft-msporny-base58-02
    b"Hello World!": "2NEpo7TZRRrLZSi2U",
    b"The quick brown fox jumps over the lazy dog.": "USm3fpXnKG5EUBx2ndxBDMPVciP5hGey2Jh4NDv6gmeo1LkMeiKrLJUUBk6Z",
    0x0000287fb4cd.to_bytes(6, byteorder="big"): "11233QC4", # fix leading 1 typo from https://datatracker.ietf.org/doc/html/draft-msporny-base58-02,
    # from https://github.com/keis/base58/blob/master/test_base58.py
    b'hello world': "StV1DL6CwTryKyV",
    b'\0\0hello world': "11StV1DL6CwTryKyV",
    b'': "",
    b'\x00': "1",
    0x111d38e5fc9071ffcd20b4a763cc9ae4f252bb4e48fd66a835e252ada93ff480d6dd43dc62a641155a5.to_bytes(42, byteorder="big"): alphabet.base58btc.chars[1:]
}

@pytest.mark.parametrize("b,s", _base58_testvecs.items())
def test_base58(b: bytes, s: str) -> None:
    """
        Test vectors from:
        - https://datatracker.ietf.org/doc/html/draft-msporny-base58-02
        - https://github.com/keis/base58/blob/master/test_base58.py

        LICENSE FOR https://github.com/keis/base58

        Copyright (c) 2015 David Keijser

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in
        all copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
        THE SOFTWARE.
    """
    assert base58btc.encode(b) == s, "Encoding error on test vector for base58"
    assert base58btc.decode(s) == b, "Decoding error on test vector for base58"


random.set_options(min_bytes=0, max_bytes=16)
nsamples = 1024

def test_encode() -> None:
    test_data = rand_bytes(nsamples, encoding=base58btc)
    for i, b in enumerate(test_data):
        s = base58btc.encode(b)
        s_exp = b58encode(b).decode("utf-8")
        assert s == s_exp, f"Encoding discrepancy at sample #{i}"

def test_decode() -> None:
    test_data = rand_str(nsamples, encoding=base58btc)
    for i, s in enumerate(test_data):
        b = base58btc.decode(s)
        b_exp = b58decode(s.encode("utf-8"))
        assert b == b_exp, f"Decoding discrepancy at sample #{i}"
