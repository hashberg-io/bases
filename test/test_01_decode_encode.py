# pylint: disable = missing-docstring

import pytest

from bases import encoding
from bases.encoding import BaseEncoding
from bases import random
from bases.random import rand_str

random.set_options(min_bytes=0, max_bytes=16)
nsamples = 1024

def _test_decode_encode(i: int, s: str, enc_name: str, enc: BaseEncoding) -> None:
    try:
        error_msg = f"encoding {repr(enc_name)} failed at #{i} = {repr(s)}"
        b = enc.decode(s)
        error_msg += f" with b = {list(b)}"
        s_enc = enc.encode(b)
        error_msg += f" and s_enc = {repr(s_enc)}"
        s_canonical = enc.canonical_string(s)
        if s_canonical != s:
            error_msg += f" where s_canonical = {repr(s_canonical)}"
        assert s_enc == s_canonical, error_msg
    except Exception as e:
        if not isinstance(e, AssertionError):
            raise Exception(error_msg) from e
        raise e

@pytest.mark.parametrize("enc_name,enc", list(encoding.table()))
def test_decode_encode(enc_name: str, enc: BaseEncoding) -> None:
    test_data = rand_str(nsamples, encoding=enc)
    for i, s in enumerate(test_data):
        _test_decode_encode(i, s, enc_name, enc)
