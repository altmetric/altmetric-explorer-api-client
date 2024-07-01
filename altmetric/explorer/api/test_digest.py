import pytest

from .client import digest

API_SECRET = 'my_secret_key'


@pytest.mark.parametrize("message,expected", [
    ('', '4b4f493acb45332879e4812a98473fc98209fee6'),
    (None, '4b4f493acb45332879e4812a98473fc98209fee6'),
    ('foo', '155ce81b88766ccd779d515af9ab6081586f077f'),
])
def test_calculating_a_digest(message, expected):
    assert digest(API_SECRET, message) == expected
