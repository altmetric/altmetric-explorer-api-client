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
print(response.meta())

# response.data() returns a python generator that yields one row of data at
# a time.  Paging is handled behind the scenes.
for item in response.data():
  print(item)
```

See the code in [examples/](examples/) for more examples.  You can run them by
executing `python -m examples.<example_name>`

## Installation

Install the dependencies needed to query the api:

```sh
pip install -r requirements.txt
```

If you want to run the tests, you also need to install the development dependencies:

```sh
pip install -r requirements.dev.txt
```

Alternatively, a docker compose file is available to setup a development environment in docker.  Start it by running:

```sh
docker compose up # add the -d flag to run in the background
```

## Useful Python Links

* Generators: https://realpython.com/introduction-to-python-generators/
* Iterators: https://realpython.com/python-iterators-iterables/



