# Altmetric Explorer API Client

A basic API client for extracting data from Altmetric Explorer using the Explorer
API ([documentation here](https://docs.altmetric.com/explorer-api/)).  This is intended to be a starter for 10 to help you get going with the API
and you are encouraged to build out whatever you need from here.

A quick example:

```python
from altmetric.explorer import api

# Get real values at https://www.altmetric.com/explorer/settings
API_KEY = 'abababababababab'
API_SECRET = 'cdcdcdcdcdcdcdcd'

client = api.Client('https://www.altmetric.com/explorer/api', API_KEY, API_SECRET)
response = client.get_mention_sources()

# response.meta returns the meta.response JSON object as a python dict
print(response.meta)

# response.data() returns a python generator that yields one row of data at
# a time.  Paging is handled behind the scenes.
for item in response.data:
  print(item)
```

## Calling any endpoint

The client is deliberately not tied to a fixed list of endpoints. `client.get`
takes an API path plus any filters and query parameters as keyword arguments,
builds the query string, and calculates the authentication digest for you:

```python
# Any path under the Explorer API works, with any filters:
response = client.get(
    'research_outputs/mention_sources',
    timeframe='1w',
    mention_sources_countries=['us', 'gb'],
)
```

This means **new Explorer API endpoints and filters work without any change to
this client**: you do not need to wait for a release or add a method. The
`get_*` methods (e.g. `get_mention_sources`) are just thin shorthands for common
paths; add one if it helps readability, but it is never required. The
authoritative list of endpoints and filters lives in the
[Explorer API documentation](https://docs.altmetric.com/explorer-api/), not in
this repository.

## Installation

The code can be installed straight from GitHub using pip:

```sh
pip install https://github.com/altmetric/altmetric-explorer-api-client/tarball/main
```

...or by adding the url to your `requirements.txt` file and running `pip install -r requirements.txt`.

## Getting Started

A [docker compose](https://docs.docker.com/compose/) file is included to setup a development environment.
Start it by running:

```sh
docker compose up # add the -d flag to run in the background
```

If you have any problems, a good first step is to re-start docker compose with the `--build` option so that the api container is re-built from scratch.

```sh
docker compose down
docker compose up --build
```

## For Developers

The tests are written using [pytest](https://docs.pytest.org/).

Run them by starting the docker compose network as described above and then...

```sh
docker compose exec app /bin/sh
pytest
```

or, from the host...

```sh
docker compose exec app pytest
```

The API tests replay recorded HTTP interactions ("cassettes") via
[pytest-recording](https://github.com/kiwicom/pytest-recording), so the suite
runs offline and needs no real credentials. Set `API_KEY` and `API_SECRET` to
any non-empty value. The `conftest.py` fixture filters the key and digest out of
both the request URLs and the response bodies of every recording, so
re-recorded cassettes stay free of credentials.

### Keeping the client in sync with the API

Because the client calls the API generically, most Explorer API changes need no
code change here. To catch the ones that do (an endpoint or response shape
changing), the `API drift check` GitHub Actions workflow re-records the
cassettes against the live API on a schedule and fails if the suite no longer
passes. It needs `API_KEY` and `API_SECRET` repository secrets. You can also run
it on demand from the Actions tab, or locally:

```sh
API_KEY=... API_SECRET=... pytest --record-mode=rewrite
```

The [autopep8](https://pypi.org/project/autopep8/) linter is installed as well.

You can lint your code by running

```sh
docker compose exec app autopep8 --in-place --recursive .
```

