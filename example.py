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


print(f'INFO : querying explorer API for policy blog sources', file=sys.stderr)

result = api_client.get_mention_sources(
    order='profile-type',
    mention_sources_types=['type:policy', 'type:blog'],
    timeframe='at')

print(f'INFO : found {len(result)} policy blog sources', file=sys.stderr)

meta_response = api_client.get_mention_sources_meta_response(
    filters=[('mention_sources_types', 'type:policy'),
             ('mention_sources_types', 'type:blog')])

print(f'INFO : got meta response {meta_response}', file=sys.stderr)
