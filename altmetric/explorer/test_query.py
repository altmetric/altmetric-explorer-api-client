import pytest

from . import api


@pytest.mark.parametrize('params,query_string', [
    ({'page_size': 30}, 'page[size]=30'),
    ({'page_number': 4}, 'page[number]=4'),
    ({'page_size': 100, 'page_number': 9}, 'page[size]=100&page[number]=9'),
    ({'order': 'some_field'}, 'filter[order]=some_field'),
    ({'mention_source_countries': ['JP', 'CN']},
        'filter[mention_source_countries][]=JP&filter[mention_source_countries][]=CN'),
    ({'mention_source_countries': ('JP', 'CN')},
        'filter[mention_source_countries][]=JP&filter[mention_source_countries][]=CN')
])
def test_query_string(params, query_string):
    assert str(api.Query(**params)) == query_string
    assert str(api.Query().add_params(**params)) == query_string
