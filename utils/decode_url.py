import fileinput
from urllib.parse import unquote, parse_qs, urlparse

for url in fileinput.input():
    url = url.rstrip()
    if url == '':
        continue

    parsed_url = urlparse(url)
    print('unencoded:', unquote(url))
    print('host:', parsed_url.hostname)
    print('path:', parsed_url.path)
    print('params:')
    for key, value in parse_qs(parsed_url.query).items():
        print(f'  - {repr(key)}: {repr(value)}')
