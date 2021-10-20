# pylint: disable = missing-docstring

from typing import Dict

import pytest

from bases.encoding import * # pylint: disable = wildcard-import, unused-wildcard-import
from bases import random
from bases.random import rand_bytes, rand_str

random.set_options(min_bytes=0, max_bytes=16)
nsamples = 1024

lower_encodings: Dict[str, BaseEncoding] = {
    "base16.lower": base16.lower(),
    "base32.lower": base32.lower(),
    "base32hex.lower": base32hex.lower(),
    "base32z.lower": base32z.lower(),
    "base36.lower": base36.lower(),
    "base45.lower": base45.lower(),
}

padded_encodings: Dict[str, BaseEncoding] = {
    "base32z.pad.include": base32z.with_pad_char("=").pad(require=False),
    "base8.pad.require": base8.pad(require=True),
    "base32.pad.require": base32.pad(require=True),
    "base32hex.pad.require": base32hex.pad(require=True),
    "base32z.pad.require": base32z.with_pad_char("=").pad(require=True),
    "base64.pad.require": base64.pad(require=True),
    "base64url.pad.require": base64url.pad(require=True),
}

unpadded_encodings: Dict[str, BaseEncoding] = {
    "base8.nopad": base8.nopad(allow=False),
    "base32.nopad": base32.nopad(allow=False),
    "base32hex.nopad": base32hex.nopad(allow=False),
    "base64.nopad": base64.nopad(allow=False),
    "base64url.nopad": base64url.nopad(allow=False),
}

encodings = {**lower_encodings, **padded_encodings, **unpadded_encodings}

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

@pytest.mark.parametrize("enc_name,enc", encodings.items())
def test_encode_decode(enc_name: str, enc: BaseEncoding) -> None:
    test_data = rand_bytes(nsamples, encoding=enc)
    for i, b in enumerate(test_data):
        _test_encode_decode(i, b, enc_name, enc)

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

@pytest.mark.parametrize("enc_name,enc", encodings.items())
def test_decode_encode(enc_name: str, enc: BaseEncoding) -> None:
    test_data = rand_str(nsamples, encoding=enc)
    for i, s in enumerate(test_data):
        _test_decode_encode(i, s, enc_name, enc)
