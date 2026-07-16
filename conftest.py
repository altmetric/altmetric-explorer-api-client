import os
import re

import pytest

DIGEST_JSON_RE = re.compile(r'("digest"\s*:\s*)"[0-9a-f]+"')
DIGEST_QUERY_RE = re.compile(r"digest=[0-9a-f]+")


def scrub_response(response):
    """Strip credentials the Explorer API echoes back in response bodies.

    The API returns the request's key and digest in the ``meta.query`` block
    and in the ``links.*`` URLs. ``filter_query_parameters`` only rewrites the
    request URL, so without this a ``pytest --record-mode=rewrite`` run with
    real secrets would write a live key and a valid digest into cassette
    response bodies.
    """
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
    from the account secret, and echoes both back in the response body. Both
    are replaced with fixed placeholders in the request URL and the response
    body so that:

    * no live credential is ever committed to this public repository, and
    * playback matches regardless of which key/secret ran the test, which lets
      the suite run offline with no credentials at all.
    """
    return {
        "filter_query_parameters": [
            ("key", "DUMMY_KEY"),
            ("digest", "DUMMY_DIGEST"),
        ],
        "before_record_response": scrub_response,
    }


@pytest.fixture(scope="module")
def vcr_config():
    return build_vcr_config()
