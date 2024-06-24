#!/usr/bin/env python

import sys
from altmetric.explorer.api import Client

if len(sys.argv) < 3:
    print('Please pass API_KEY and API_SECRET', file=sys.stderr)
    sys.exit(1)

API_KEY = sys.argv[1]
API_SECRET = sys.argv[2]

api_client = Client(
    'https://www.altmetric.com/explorer/api', API_KEY, API_SECRET)

print(f'INFO : querying explorer API for policy & blog mention sources')
response = api_client.get_mention_sources(
    order='profile-type',
    mention_sources_types=['type:policy', 'type:blog'],
    timeframe='at')

meta = response.meta()
print(f'INFO : got metadata:')
for key, value in meta.items():
    print(f'  {key} = {repr(value)}')

data = list(response.data())
print(f'INFO : found {len(data)} policy blog sources', file=sys.stderr)
