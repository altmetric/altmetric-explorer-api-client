import sys

from altmetric.explorer import api

URL = 'https://www.altmetric.com/explorer/api/research_outputs/mention_sources?digest=3736a6809659da2c28cca8e9736b4010979066a6&filter[mention_sources_countries][]=JP&filter[scope]=all&filter[timeframe]=at&key=b5f9faabd368491692d4209087ffacae'


def each_row(url, page_size=100):
    i = 0
    url = url + f'&page[size]={page_size}'

    for page in api.all_pages(url):
        print(f'+++++ Fetched page #{i} from api +++++', file=sys.stderr)
        for row in page['data']:
            yield row
        i += 1


rows = each_row(URL, page_size=2)
