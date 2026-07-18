import os
import re

import pytest

DIGEST_JSON_RE = re.compile(r'("digest"\s*:\s*)"[0-9a-f]+"')
DIGEST_QUERY_RE = re.compile(r"digest=[0-9a-f]+")

# Response headers that must never be written to a cassette in this public repo.
# The write endpoint (identifier_lists) sets a session cookie on its response.
SENSITIVE_RESPONSE_HEADERS = ("set-cookie",)


def scrub_response(response):
    """Strip credentials from recorded responses.

    Removes sensitive response headers (the session cookie the write endpoint
    sets) and rewrites the key and digest the API echoes back in the response
    body (the ``meta.query`` block and the ``links.*`` URLs).
    ``filter_query_parameters`` / ``filter_post_data_parameters`` only cover the
    request, so without this a ``pytest --record-mode=rewrite`` run with real
    secrets would write a live session cookie and a valid key/digest into
    cassette responses.
    """
    headers = response.get("headers", {})
    for name in list(headers):
        if name.lower() in SENSITIVE_RESPONSE_HEADERS:
            del headers[name]

    body = response.get("body", {})
    raw = body.get("string")
    if raw is None:
        return response

    is_bytes = isinstance(raw, (bytes, bytearray))
    text = raw.decode("utf-8", "replace") if is_bytes else raw

    key = os.environ.get("API_KEY")
    if key:
        text = text.replace(key, "DUMMY_KEY")
    text = DIGEST_JSON_RE.sub(r'\1"DUMMY_DIGEST"', text)
    text = DIGEST_QUERY_RE.sub("digest=DUMMY_DIGEST", text)

    body["string"] = text.encode("utf-8") if is_bytes else text
    response["body"] = body
    return response


def build_vcr_config():
    """The VCR configuration, exposed as a plain function so it can be tested.

    Keeps API credentials out of recorded cassettes. The Explorer API
    authenticates each request with a public ``key`` and a ``digest`` derived
    from the account secret, and echoes both back in the response body. The
    write endpoint (identifier_lists) also sends them in the request body. All
    are replaced with fixed placeholders in the request URL, the request body
    and the response body so that:

    * no live credential is ever committed to this public repository, and
    * playback matches regardless of which key/secret ran the test, which lets
      the suite run offline with no credentials at all.
    """
    return {
        "filter_query_parameters": [
            ("key", "DUMMY_KEY"),
            ("digest", "DUMMY_DIGEST"),
        ],
        "filter_post_data_parameters": [
            ("key", "DUMMY_KEY"),
            ("digest", "DUMMY_DIGEST"),
        ],
        "filter_headers": ["authorization", "cookie"],
        "before_record_response": scrub_response,
    }


@pytest.fixture(scope="module")
def vcr_config():
    return build_vcr_config()
