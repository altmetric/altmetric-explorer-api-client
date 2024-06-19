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
client.get_mention_sources()
```

## Useful Python Links

* Generators: https://realpython.com/introduction-to-python-generators/
* Iterators: https://realpython.com/python-iterators-iterables/



