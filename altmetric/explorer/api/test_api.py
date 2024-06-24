import pytest

from . import Client
from .env import API_KEY, API_SECRET


@pytest.fixture
def api_client():
    return Client('https://www.altmetric.com/explorer/api', API_KEY, API_SECRET)


def test_api_checks_for_invalid_key_and_secret():
    with pytest.raises(ValueError):
        Client(
            'https://www.altmetric.com/explorer/api', None, None)


@pytest.mark.parametrize("client_fn", [
    ('get_mention_sources'),
    ('get_mentions'),
])
def test_getting_data_from_the_api(client_fn, api_client):
    fn = getattr(api_client, client_fn)
    response = fn(page_size=1)  # return a tiny page so tests run quickly
    try:
        row = next(response.data())
        assert len(row.keys()) > 0
    except StopIteration:
        pytest.fail('no data returned')


@pytest.mark.parametrize("client_fn, expected_keys", [
    ('get_mention_sources', ('description',
                             'status',
                             'total-mentions',
                             'total-pages',
                             'total-results')),
    ('get_mentions', ('description',
                      'status',
                      'total-pages',
                      'total-results'))
])
def test_getting_the_response_block_from_the_meta_block(client_fn, expected_keys, api_client):
    fn = getattr(api_client, client_fn)
    response = fn(page_size=1)  # return a tiny page so tests run quickly
    assert set(response.meta().keys()) == set(expected_keys)
