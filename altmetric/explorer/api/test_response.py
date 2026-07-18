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


def test_resource_returns_the_single_data_object():
    raw = FakeApiResponse(200, {
        'meta': {'response': {'status': 'ok'}},
        'data': {'id': 'abc', 'counts': {'dois': 2}, 'content': '10.1/x'}
    })

    response = Response(raw)

    assert response.resource == {'id': 'abc',
                                 'counts': {'dois': 2}, 'content': '10.1/x'}


def test_resource_is_none_when_the_request_failed(not_found):
    assert Response(not_found).resource is None


def test_data_yields_a_single_object_payload_whole():
    # a create response has a dict under `data`; .data must yield the object,
    # not iterate the dict's keys
    raw = FakeApiResponse(200, {'data': {'id': 'abc', 'counts': {}}})

    assert list(Response(raw).data) == [{'id': 'abc', 'counts': {}}]


def test_resource_is_none_when_the_response_has_no_data_object():
    raw = FakeApiResponse(200, {'meta': {'response': {'status': 'ok'}}})

    assert Response(raw).resource is None


def test_errors_returns_the_error_envelope():
    raw = FakeApiResponse(400, {
        'meta': {'response': {'status': 'error'}},
        'errors': [{'status': '400', 'code': 'invalid_identifier_list'}]
    })

    assert Response(raw).errors == [
        {'status': '400', 'code': 'invalid_identifier_list'}]


def test_errors_is_empty_when_there_are_none():
    raw = FakeApiResponse(
        200, {'meta': {'response': {'status': 'ok'}}, 'data': []})

    assert Response(raw).errors == []


def test_errors_is_empty_when_the_body_is_a_non_object_json_value():
    # a bare JSON array or string parses fine but is not an error envelope
    assert Response(FakeApiResponse(400, [{'status': '400'}])).errors == []
    assert Response(FakeApiResponse(400, 'rate limited')).errors == []


def test_errors_is_empty_when_the_body_is_not_json(mocker):
    # a gateway HTML/plain-text error: json() raises, errors must not crash
    raw = mocker.Mock(status_code=500, text='<html>Bad Gateway</html>')
    raw.json.side_effect = ValueError('no json')

    assert Response(raw).errors == []


def test_errors_is_empty_when_the_errors_value_is_not_a_list():
    # a null or object `errors` (both hit the same not-a-list guard) -> []
    raw = FakeApiResponse(400, {'errors': {'code': 'x'}})

    assert Response(raw).errors == []
