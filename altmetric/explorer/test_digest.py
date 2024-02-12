import pytest

from . import api
from ..credentials import API_SECRET


@pytest.mark.parametrize("message,expected", [
    ('', '53534093d456666d5e3fcc8264a21b27acacf494'),
    (None, '53534093d456666d5e3fcc8264a21b27acacf494'),
    ('foo', '89ff9c9e3e6bd43bd0fde6235da2aa913290291d'),
])
def test_calculating_a_digest(message, expected):
    assert api.digest(API_SECRET, message) == expected
