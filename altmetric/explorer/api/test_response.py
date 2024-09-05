import pytest
from mergedeep import merge

from .response import Response


class FakeApiResponse:
    def __init__(self, status_code, text, next_page=None):
        self.status_code = status_code
        self.text = text
        self.next_page = next_page

    def json(self):
        if self.next_page:
            return merge({}, self.text, {'links': {'next': self.next_page}})
        return self.text

    def __repr__(self):
        return f'FakeApiResponse({self.status_code}, {repr(self.text)}, next_page={repr(self.next_page)})'


def fake_get(attrs):
    def fn(url):
        try:
            return attrs[url]
        except KeyError:
            raise StopIteration()
    return fn


@ pytest.fixture
def page1():
    return FakeApiResponse(200, {
        "links": {},
        "meta": {'response': {'from': 'page1'}},
        "data": [{'id': 1, 'foo': 'bar'}],
        "included": []
    })


@ pytest.fixture
def page2():
    return FakeApiResponse(200, {
        'links': {},
        'meta': {'response': {'from': 'page2'}},
        'data': [{'id': 2, 'foo': 'bop'}],
        'included': []
    })


@ pytest.fixture
def ok():
    return FakeApiResponse(200, 'OK')


@ pytest.fixture
def multiple_choices():
    return FakeApiResponse(300, 'Multiple Choices')


@ pytest.fixture
def not_found():
    return FakeApiResponse(404, 'Not Found')


def test_good_response_from_the_api(page1):
    response = Response(page1)

    assert response.status_code == 200
    assert list(response.data) == [{'id': 1, 'foo': 'bar'}]


def test_response_returns_all_pages(mocker, page1, page2):
    page1.next_page = 'https://example.com/pages/2'

    mocker.patch('requests.get', side_effect=fake_get(
        {'https://example.com/pages/2': page2}))

    response = Response(page1)
    assert list(response.data) == [
        {'id': 1, 'foo': 'bar'}, {'id': 2, 'foo': 'bop'}]


def test_response_returns_meta_from_first_page(mocker, page1, page2):
    page1.next_page = 'https://example.com/pages/2'

    mocker.patch('requests.get', side_effect=fake_get(
        {'https://example.com/pages/2': page2}))

    response = Response(page1)
    assert response.meta == {'from': 'page1'}


def test_api_failure_data(multiple_choices):
    response = Response(multiple_choices)

    # Using the most unusual status "300: Multiple Choices" to test
    # the boundary condition between 299 and 300
    assert response.status_code == 300
    assert response.meta is None
    assert list(response.data) == []
    assert response.text == 'Multiple Choices'


def test_api_failure_predicate(ok):
    response = Response(ok)

    assert not response.failed
    assert response.ok


def test_api_ok_predicate(not_found):
    response = Response(not_found)

    assert response.failed
    assert not response.ok
