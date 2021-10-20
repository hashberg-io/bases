# pylint: disable = missing-docstring

import pytest

from bases import encoding
from bases.encoding import BaseEncoding
from bases import random
from bases.random import rand_bytes

random.set_options(min_bytes=0, max_bytes=16)
nsamples = 1024

def _test_encode_decode(i: int, b: bytes, enc_name: str, enc: BaseEncoding) -> None:
    try:
        error_msg = f"encoding {repr(enc_name)} failed at #{i} = {list(b)}"
        s = enc.encode(b)
        error_msg += f" with s = {repr(s)}"
        b_dec = enc.decode(s)
        error_msg += f" and b_dec = {list(b_dec)}"
        b_canonical = enc.canonical_bytes(b)
        if b_canonical != b:
            error_msg += f" where b_canonical = {list(b_canonical)}"
        assert b_dec == b_canonical, error_msg
    except Exception as e:
        if not isinstance(e, AssertionError):
            raise Exception(error_msg) from e
        raise e

@pytest.mark.parametrize("enc_name,enc", list(encoding.table()))
def test_encode_decode(enc_name: str, enc: BaseEncoding) -> None:
    test_data = rand_bytes(nsamples, encoding=enc)
    for i, b in enumerate(test_data):
        _test_encode_decode(i, b, enc_name, enc)
