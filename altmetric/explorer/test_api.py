import pytest

from . import api
from ..credentials import API_KEY, API_SECRET


@pytest.fixture
def api_client():
    return api.Client('https://www.altmetric.com/explorer/api', API_KEY, API_SECRET)


def test_api_checks_for_invalid_key_and_secret():
    with pytest.raises(ValueError):
        api.Client('https://www.altmetric.com/explorer/api', None, None)


@pytest.mark.parametrize("client_fn,page_size,limit", [
    ('get_mention_sources', 100, 10),
    ('get_mention_sources', 9, 10),
    ('get_mentions', 100, 10),
    ('get_mentions', 9, 10),
])
def test_getting_data_from_the_api(client_fn, page_size, limit, api_client):
    fn = getattr(api_client, client_fn)
    rows = fn(page_size=page_size, limit=limit)
    assert (len(rows)) == limit


@pytest.mark.skip
@pytest.mark.parametrize("client_fn, expected_keys", [
    ('get_mentions_meta_response', ('description',
                                    'status',
                                    'total-pages',
                                    'total-results')),
    ('get_mention_sources_meta_response', ('description',
                                           'status',
                                           'total-mentions',
                                           'total-pages',
                                           'total-results'))
])
def test_getting_the_response_block_from_the_meta_block(client_fn, expected_keys, api_client):
    fn = getattr(api_client, client_fn)
    result = fn(filters=[])
    assert set(result.keys()) == set(expected_keys)

@pytest.mark.skip
def test_api_default_parameters(api_client):
    rows = api_client.get('research_outputs/mention_sources')
    assert len(rows) > 0
