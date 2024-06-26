# Altmetric Explorer API Client

A basic API client for extracting data from Altmetric Explorer using the Explorer
API ([documentation here](https://www.altmetric.com/explorer/documentation/api)).  This is intended to be a starter for 10 to help you get going with the API
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

See the code in [examples/](examples/) for more examples.  You can run them by
executing `python -m examples.<example_name>`

## Installation

A [docker compose](https://docs.docker.com/compose/) file is included to setup a development environment in docker that runs a Jupyter Labs server so you can experiment with the api.

Start it by running:

```sh
docker compose up # add the -d flag to run in the background
```

Then visit http://localhost:8888/lab/tree/getting_started.ipynb and follow the instructions in the notebook to learn how to use the API client.

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


