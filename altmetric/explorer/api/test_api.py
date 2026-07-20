import re
from urllib.parse import urlparse, parse_qs

import pytest

from . import Client
from .client import digest
from .env import API_KEY, API_SECRET


@pytest.fixture
def api_client():
    return Client('https://www.altmetric.com/explorer/api', API_KEY, API_SECRET)


def test_api_checks_for_invalid_key_and_secret():
    with pytest.raises(ValueError):
        Client(
            'https://www.altmetric.com/explorer/api', None, None)


@pytest.mark.vcr(allow_playback_repeats=True)
@pytest.mark.parametrize("client_fn", [
    ('get_attention_summary'),
    ('get_demographics'),
    ('get_journals'),
    ('get_mention_sources'),
    ('get_mentions'),
    ('get_research_outputs')
])
def test_getting_data_from_the_api(client_fn, api_client):
    fn = getattr(api_client, client_fn)
    response = fn(page_size=1)  # return a tiny page so tests run quickly

    assert response.status_code == 200
    try:
        assert len(next(response.data).keys()) > 0
        assert len(next(response.data).keys()) > 0  # from second page
    except StopIteration:
        pytest.fail('no data returned')


@pytest.mark.vcr(allow_playback_repeats=True)
def test_getting_included_from_the_api(api_client):
    response = api_client.get_research_outputs()

    assert response.status_code == 200
    try:
        assert len(next(response.included).keys()) > 0
        assert len(next(response.included).keys()) > 0  # from second page
    except StopIteration:
        pytest.fail('no data returned')


@pytest.mark.vcr(allow_playback_repeats=True)
@pytest.mark.parametrize("client_fn, expected_keys", [
    ('get_attention_summary', ('description',
                               'status',
                               'total-pages',
                               'total-results')),
    ('get_demographics', ('description',
                          'status',
                          'total-pages',
                          'total-results')),
    ('get_journals', ('description',
                      'status',
                      'total-pages',
                      'total-results')),
    ('get_mention_sources', ('description',
                             'status',
                             'total-mentions',
                             'total-pages',
                             'total-results')),
    ('get_mentions', ('description',
                      'status',
                      'total-pages',
                      'total-results')),
    ('get_research_outputs', ('description',
                              'status',
                              'total-pages',
                              'total-results'))
])
def test_getting_the_response_block_from_the_meta_block(client_fn, expected_keys, api_client):
    fn = getattr(api_client, client_fn)
    response = fn(page_size=1)  # return a tiny page so tests run quickly
    assert set(response.meta.keys()) == set(expected_keys)


@pytest.mark.parametrize('identifiers, expected_raw', [
    ('10.1/x altmetric:1', '10.1/x altmetric:1'),
    (['10.1/x', 'altmetric:1'], '10.1/x\naltmetric:1'),
    # a set is sorted so the body (and digest) is deterministic
    ({'altmetric:1', '10.1/x'}, '10.1/x\naltmetric:1'),
])
def test_creating_an_identifier_list_signs_the_raw_body(mocker, identifiers, expected_raw):
    post = mocker.patch('altmetric.explorer.api.client.requests.post')
    post.return_value.status_code = 200
    post.return_value.json.return_value = {
        'meta': {'response': {'status': 'ok'}}, 'data': {}}
    client = Client('https://www.altmetric.com/explorer/api',
                    'pub-key', 'my-secret-with-hyphens')

    client.create_identifier_list(identifiers)

    (url,), kwargs = post.call_args
    assert url == 'https://www.altmetric.com/explorer/api/identifier_lists'
    assert kwargs['data'] == {
        'key': 'pub-key',
        # digest is signed with the secret's hyphens stripped, over the raw body
        'digest': digest('mysecretwithhyphens', expected_raw),
        'identifiers': expected_raw,
    }


@pytest.mark.parametrize('identifiers', ['', '   ', [], (), None])
def test_creating_an_identifier_list_rejects_empty_identifiers(api_client, identifiers):
    with pytest.raises(ValueError, match=r'(?i)identifiers cannot be empty'):
        api_client.create_identifier_list(identifiers)


@pytest.mark.parametrize('identifiers', [
    b'10.1/x',           # bytes iterate as ints
    bytearray(b'10.1/x'),
    {'10.1/x': 1},       # a mapping iterates as keys
    ['10.1/x', None],    # a non-string item
])
def test_creating_an_identifier_list_rejects_non_string_input(api_client, identifiers):
    # these would otherwise be silently signed and POSTed as garbage
    with pytest.raises(TypeError):
        api_client.create_identifier_list(identifiers)


@pytest.mark.vcr
def test_creating_an_identifier_list(api_client):
    response = api_client.create_identifier_list(
        '10.3133/pp1348 altmetric:101427008 10.1007/bf01734359')

    assert response.status_code == 200
    assert response.meta == {'status': 'ok'}
    assert re.match(r'^[0-9a-f-]{36}$', response.resource['id'])
    assert response.resource['counts']['dois'] == 2
    assert 'content' in response.resource


URL_EXAMPLES = [
    (('https://altmetric.com/explorer/api/research_outputs/mentions'),
     ('https://www.altmetric.com/explorer/api/research_outputs/mentions?'
      'digest=aaabbb&'
      'key=xxxxyyyy')
     ),

    (('research_outputs/mentions'),
     ('https://www.altmetric.com/explorer/api/research_outputs/mentions?'
      'digest=aaabbb&'
      'key=xxxxyyyy')
     ),

    (('https://altmetric.com/explorer/api/research_outputs/mentions?'
      'digest=6f4e3b50a2bc442199a2c32449b1754d&'
      'key=xxxxyyyy'),
     ('https://www.altmetric.com/explorer/api/research_outputs/mentions?'
      'digest=aaabbb&'
      'key=xxxxyyyy')
     ),

    (('https://altmetric.com/explorer/api/research_outputs/mentions?'
      'digest=6f4e3b50a2bc442199a2c32449b1754d&'
      'key=xxxxyyyy&'
      'page[size]=10&page[number]=3'),
     ('https://www.altmetric.com/explorer/api/research_outputs/mentions?'
      'digest=aaabbb&'
      'key=xxxxyyyy&'
      'page[size]=10&page[number]=3'
      )),

    (('https://altmetric.com/explorer/api/research_outputs/mentions?'
      'digest=6f4e3b50a2bc442199a2c32449b1754d&'
      'key=xxxxyyyy&'
      'page[size]=10&page[number]=3&'
      'filter[order]=score_desc&'
      'filter[type][]=book&'
      'filter[type][]=chapter'
      ),
     ('https://www.altmetric.com/explorer/api/research_outputs/mentions?'
      'digest=aaabbb&'
      'key=xxxxyyyy&'
      'page[size]=10&page[number]=3&'
      'filter[order]=score_desc&'
      'filter[type][]=book&'
      'filter[type][]=chapter'
      ))
]


@pytest.mark.parametrize('url,expected', URL_EXAMPLES)
def test_recoding_a_url(mocker, api_client, url, expected):
    mocker.patch('altmetric.explorer.api.client.digest', return_value='aaabbb')
    api_client.api_key = 'xxxxyyyy'

    result = urlparse(api_client.recode_url(url))
    expected = urlparse(expected)

    # Query params may be ordered differently between the result and expected urls
    # even though they are semantically identical so it's easier to test the
    # component parts of the url individually rather than trying to ensure
    # the query strings are identical.
    assert result.scheme == expected.scheme
    assert result.hostname == expected.hostname
    assert result.netloc == expected.netloc
    assert result.path == expected.path
    assert result.params == expected.params
    assert result.fragment == expected.fragment
    assert parse_qs(result.query) == parse_qs(expected.query)


@pytest.mark.parametrize('url,expected', [
    (urlparse(url), urlparse(expected)) for url, expected in URL_EXAMPLES]
)
def test_recoding_a_url_from_a_url_object(mocker, api_client, url, expected):
    mocker.patch('altmetric.explorer.api.client.digest', return_value='aaabbb')
    api_client.api_key = 'xxxxyyyy'

    result = urlparse(api_client.recode_url(url))
    expected = expected

    # Query params may be ordered differently between the result and expected urls
    # even though they are semantically identical so it's easier to test the
    # component parts of the url individually rather than trying to ensure
    # the query strings are identical.
    assert result.scheme == expected.scheme
    assert result.hostname == expected.hostname
    assert result.netloc == expected.netloc
    assert result.path == expected.path
    assert result.params == expected.params
    assert result.fragment == expected.fragment
    assert parse_qs(result.query) == parse_qs(expected.query)


@pytest.mark.parametrize('query_string', [
    'wombat=1',
    'wombat[value]=foo',
    'wombat][=foo',
])
def test_recoding_a_url_rejects_invalid_query_string(api_client, query_string):
    url = f'{api_client.api_endpoint}?{query_string}'

    with pytest.raises(ValueError, match=r'(?i)unexpected query parameter.+wombat'):
        urlparse(api_client.recode_url(url))


def test_recoding_a_url_rejects_query_that_is_not_a_string(api_client):
    with pytest.raises(ValueError, match=r'(?i)must be a string'):
        urlparse(api_client.recode_url(1234))
