from conftest import build_vcr_config, scrub_response


def test_scrub_response_removes_the_session_cookie():
    response = {
        "headers": {
            "Set-Cookie": ["_altmetric-explorer_session=secret; path=/"],
            "Content-Type": ["application/json"],
        },
        "body": {"string": b'{"data":{"id":"x"}}'},
    }

    scrubbed = scrub_response(response)

    assert "Set-Cookie" not in scrubbed["headers"]
    assert "Content-Type" in scrubbed["headers"]


def test_scrub_response_replaces_key_and_digest_in_the_body(monkeypatch):
    monkeypatch.setenv("API_KEY", "REALKEY")
    response = {
        "headers": {},
        "body": {"string": b'{"meta":{"query":{"key":"REALKEY","digest":"abc123"}}}'},
    }

    body = scrub_response(response)["body"]["string"].decode()

    assert "REALKEY" not in body
    assert "abc123" not in body
    assert "DUMMY_KEY" in body
    assert '"digest":"DUMMY_DIGEST"' in body


def test_build_vcr_config_scrubs_credentials_from_every_request_channel():
    config = build_vcr_config()

    assert ("key", "DUMMY_KEY") in config["filter_query_parameters"]
    assert ("key", "DUMMY_KEY") in config["filter_post_data_parameters"]
    assert "cookie" in config["filter_headers"]
