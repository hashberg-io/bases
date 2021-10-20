# pylint: disable = missing-docstring

import pytest

from bases import alphabet
from bases.encoding import * # pylint: disable = wildcard-import, unused-wildcard-import

_multibase_case_insensitivity_b = b"yes mani !"
_multibase_case_insensitivity = {
    ("base16", base16.lower()): "796573206d616e692021",
    ("base16upper", base16): "796573206D616E692021",
    ("base32", base32.nopad().lower()): "pfsxgidnmfxgsibb",
    ("base32upper", base32.nopad()): "PFSXGIDNMFXGSIBB",
    ("base32hex", base32hex.lower().nopad()): "f5in683dc5n6i811",
    ("base32hexupper", base32hex.nopad().upper()): "F5IN683DC5N6I811",
    ("base32pad", base32.lower()): "pfsxgidnmfxgsibb",
    ("base32padupper", base32): "PFSXGIDNMFXGSIBB",
    ("base32hexpad", base32hex.lower()): "f5in683dc5n6i811",
    ("base32hexpadupper", base32hex): "F5IN683DC5N6I811",
    ("base36", base36.lower()): "2lcpzo5yikidynfl",
    ("base36upper", base36): "2LCPZO5YIKIDYNFL",
}

@pytest.mark.parametrize("enc_name,enc,s", [(t[0], t[1], s) for t, s in _multibase_case_insensitivity.items()])
def test_multibase_case_insensitivity(enc_name: str, enc: BaseEncoding, s: str) -> None:
    """
        Test vectors from https://github.com/multiformats/multibase/blob/master/tests/case_insensitivity.csv

        [CC-BY-SA 3.0 license](https://ipfs.io/ipfs/QmVreNvKsQmQZ83T86cWSjPu2vR3yZHGPm5jnxFuunEB9u) © 2016 Protocol Labs Inc.
    """
    assert enc.encode(_multibase_case_insensitivity_b) == s, f"Encoding error on multibase_case_insensitivity test vector for {enc_name}"
    assert enc.decode(s) == _multibase_case_insensitivity_b, f"Decoding error on multibase_case_insensitivity test vector for {enc_name}"
