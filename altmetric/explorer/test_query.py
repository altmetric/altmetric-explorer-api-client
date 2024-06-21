import pytest

from . import api


@pytest.mark.parametrize('params,query_string', [
    ({}, ''),
    ({'page_size': 30}, 'page[size]=30'),
    ({'page_number': 4}, 'page[number]=4'),
    ({'page_size': 100, 'page_number': 9}, 'page[size]=100&page[number]=9'),
    ({'order': 'some_field'}, 'filter[order]=some_field'),
    ({'mention_source_countries': ['JP', 'CN']},
        'filter[mention_source_countries][]=JP&filter[mention_source_countries][]=CN'),
    ({'mention_source_countries': ('JP', 'CN')},
        'filter[mention_source_countries][]=JP&filter[mention_source_countries][]=CN'),
    ({'timeframe': '3d'},
        'filter[timeframe]=3d'),
    ({'foo': 'bar', 'key': 'key123', 'digest': 'digestabc'},
        'key=key123&digest=digestabc&filter[foo]=bar')
])
def test_query_string(params, query_string):
    assert str(api.Query(**params)) == query_string
    assert str(api.Query().add_params(**params)) == query_string

@pytest.mark.parametrize('params,message', [
    ({}, ''),
    ({'q': 'hello'}, 'q|hello'),
    ({'q': 'hello', 'p': 'goodbye'}, 'p|goodbye|q|hello'),
    ({'page_size': 30}, ''),
    ({'page_number': 4}, ''),
    ({'page_size': 100, 'page_number': 9}, ''),
    ({'order': 'some_field'}, ''),
    ({'list': ['a','b','c']}, 'list|a|b|c'),
    ({'list': ['c','b','a']}, 'list|c|b|a'), # param values do not need to be sorted alphabetically
    ({'list': ('a','b','c')}, 'list|a|b|c'),

])
def test_message(params, message):
    query = api.Query(**params)
    assert query.filters.message() == message

def test_message_supports_sets():
    query = api.Query(list = set(['a','b','c']))
    response = query.filters.message()
    array = response.split('|')
    assert array[0] == 'list'
    assert set(array[1:4]) == set(['a', 'b', 'c'])


