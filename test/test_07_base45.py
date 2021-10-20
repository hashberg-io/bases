# pylint: disable = missing-docstring

import pytest

from bases.encoding import base45

_base45_testvecs = {
    # from https://datatracker.ietf.org/doc/draft-faltstrom-base45/
    b"AB": "BB8",
    b"Hello!!": "%69 VD92EX0",
    b"base-45": "UJCLQE7W581",
    b"ietf!": "QED8WEX0",
}

@pytest.mark.parametrize("b,s", _base45_testvecs.items())
def test_base45(b: bytes, s: str) -> None:
    """
        Test vectors from https://datatracker.ietf.org/doc/draft-faltstrom-base45/
    """
    assert base45.encode(b) == s, "Encoding error on test vector for base45b"
    assert base45.decode(s) == b, "Decoding error on test vector for base45b"
