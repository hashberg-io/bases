# pylint: disable = missing-docstring

import pytest

from bases import alphabet
from bases.encoding import * # pylint: disable = wildcard-import, unused-wildcard-import

_multibase_leading_zero_b = b"\x00yes mani !"
_multibase_leading_zero = {
    ("base2", base2): "0000000001111001011001010111001100100000011011010110000101101110011010010010000000100001",
    ("base8", base8.nopad()): "000745453462015530267151100204",
    ("base10", base10): "0573277761329450583662625",
    ("base16", base16.lower()): "00796573206d616e692021",
    ("base16upper", base16): "00796573206D616E692021",
    ("base32", base32.nopad().lower()): "ab4wk4zanvqw42jaee",
    ("base32upper", base32.nopad()): "AB4WK4ZANVQW42JAEE",
    ("base32hex", base32hex.lower().nopad()): "01smasp0dlgmsq9044",
    ("base32hexupper", base32hex.nopad().upper()): "01SMASP0DLGMSQ9044",
    ("base32pad", base32.lower()): "ab4wk4zanvqw42jaee======",
    ("base32padupper", base32): "AB4WK4ZANVQW42JAEE======",
    ("base32hexpad", base32hex.lower()): "01smasp0dlgmsq9044======",
    ("base32hexpadupper", base32hex): "01SMASP0DLGMSQ9044======",
    ("base32z", base32z): "ybhskh3ypiosh4jyrr",
    ("base36", base36.lower()): "02lcpzo5yikidynfl",
    ("base36upper", base36): "02LCPZO5YIKIDYNFL",
    ("base58flickr", base58flickr): "17Pznk19XTTzBtx",
    ("base58btc", base58btc): "17paNL19xttacUY",
    ("base64", base64.nopad()): "AHllcyBtYW5pICE",
    ("base64pad", base64): "AHllcyBtYW5pICE=",
    ("base64url", base64url.nopad()): "AHllcyBtYW5pICE",
    ("base64urlpad", base64url): "AHllcyBtYW5pICE=",
}

@pytest.mark.parametrize("enc_name,enc,s", [(t[0], t[1], s) for t, s in _multibase_leading_zero.items()])
def test_multibase_leading_zero(enc_name: str, enc: BaseEncoding, s: str) -> None:
    """
        Test vectors from https://github.com/multiformats/multibase/blob/master/tests/leading_zero.csv

        [CC-BY-SA 3.0 license](https://ipfs.io/ipfs/QmVreNvKsQmQZ83T86cWSjPu2vR3yZHGPm5jnxFuunEB9u) © 2016 Protocol Labs Inc.
    """
    assert enc.encode(_multibase_leading_zero_b) == s, f"Encoding error on multibase_leading_zero test vector for {enc_name}"
    assert enc.decode(s) == _multibase_leading_zero_b, f"Decoding error on multibase_leading_zero test vector for {enc_name}"


_multibase_leading_two_zeros_b = b"\x00\x00yes mani !"
_multibase_leading_two_zeros = {
    ("base2", base2): "000000000000000001111001011001010111001100100000011011010110000101101110011010010010000000100001",
    ("base8", base8.nopad()): "00000171312714403326055632220041",
    ("base10", base10): "00573277761329450583662625",
    ("base16", base16.lower()): "0000796573206d616e692021",
    ("base16upper", base16): "0000796573206D616E692021",
    ("base32", base32.nopad().lower()): "aaahszltebwwc3tjeaqq",
    ("base32upper", base32.nopad()): "AAAHSZLTEBWWC3TJEAQQ",
    ("base32hex", base32hex.lower().nopad()): "0007ipbj41mm2rj940gg",
    ("base32hexupper", base32hex.nopad().upper()): "0007IPBJ41MM2RJ940GG",
    ("base32pad", base32.lower()): "aaahszltebwwc3tjeaqq====",
    ("base32padupper", base32): "AAAHSZLTEBWWC3TJEAQQ====",
    ("base32hexpad", base32hex.lower()): "0007ipbj41mm2rj940gg====",
    ("base32hexpadupper", base32hex): "0007IPBJ41MM2RJ940GG====",
    ("base32z", base32z): "yyy813murbssn5ujryoo",
    ("base36", base36.lower()): "002lcpzo5yikidynfl",
    ("base36upper", base36): "002LCPZO5YIKIDYNFL",
    ("base58flickr", base58flickr): "117Pznk19XTTzBtx",
    ("base58btc", base58btc): "117paNL19xttacUY",
    ("base64", base64.nopad()): "AAB5ZXMgbWFuaSAh",
    ("base64pad", base64): "AAB5ZXMgbWFuaSAh",
    ("base64url", base64url.nopad()): "AAB5ZXMgbWFuaSAh",
    ("base64urlpad", base64url): "AAB5ZXMgbWFuaSAh",
}

@pytest.mark.parametrize("enc_name,enc,s", [(t[0], t[1], s) for t, s in _multibase_leading_two_zeros.items()])
def test_multibase_two_leading_zeros(enc_name: str, enc: BaseEncoding, s: str) -> None:
    """
        Test vectors from https://github.com/multiformats/multibase/blob/master/tests/two_leading_zeros.csv

        [CC-BY-SA 3.0 license](https://ipfs.io/ipfs/QmVreNvKsQmQZ83T86cWSjPu2vR3yZHGPm5jnxFuunEB9u) © 2016 Protocol Labs Inc.
    """
    assert enc.encode(_multibase_leading_two_zeros_b) == s, f"Encoding error on multibase_leading_zero test vector for {enc_name}"
    assert enc.decode(s) == _multibase_leading_two_zeros_b, f"Decoding error on multibase_leading_zero test vector for {enc_name}"
