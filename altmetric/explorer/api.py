import base64
from itertools import groupby
import hmac
import hashlib

import requests


def all_pages(url):
    while url:
        response = requests.get(url)
        if response.status_code != requests.codes.ok:
            raise Exception(f'{url} returned {response.status_code}')

        page = response.json()
        url = page.get('links', {}).get('next', None)

        yield page


def digest(secret, message):
    if message is None:
        message = ''
    hmac_sha1 = hmac.new(secret.encode('utf-8'),
                         message.encode('utf-8'), hashlib.sha1)
    signature = base64.b64encode(hmac_sha1.digest()).decode('utf-8')
    signature = hmac_sha1.hexdigest()
    return signature


class FilterList:
    def __init__(self, filters):
        self.filters = filters

    def message(self):
        result = []
        for attr, values in groupby(self.filters, lambda t: t[0]):
            result.append(attr)
            for _, value in values:
                result.append(value)
        return '|'.join(result)

    def params(self):
        return str(self)

    def __str__(self):
        return '&'.join(f'filter[{attr}][]={value}' for attr, value in self.filters)

    def __iter__(self):
        return iter(self.filters)


class Query:
    def __init__(self, **kvargs):
        self.items = []
        self.add_params(**kvargs)

    def add_params(self, **kvargs):
        for arg, value in kvargs.items():
            match arg:
                case 'order':
                    self.items.append(f'filter[order]={value}')
                case 'page_size':
                    self.items.append(f'page[size]={value}')
                case 'page_number':
                    self.items.append(f'page[number]={value}')
                case _:
                    self.items.append(f'{arg}={value}')
        return self

    def add_auth(self, api_key, digest):
        return self.add_params(key=api_key, digest=digest)

    def add_str(self, item):
        self.items.append(str(item))
        return self

    def __str__(self):
        return "&".join(self.items)


class Client:
    def __init__(self, api_endpoint, api_key, api_secret):
        if api_key == None or api_secret == None:
            raise ValueError('api_key and api_secret cannot be None')

        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.api_secret = api_secret

    def get(self, path, filters=(), page_size=100, order=None, limit=None):
        filters = FilterList(filters)
        query = Query(
            page_size=page_size,
            order=order
        )
        query.add_auth(self.api_key,
                       digest(self.api_secret, filters.message()))
        query.add_str(filters)

        url = self.api_endpoint + '/' + path + '?' + str(query)

        result = []
        for page in all_pages(url):
            data = page.get('data', [])
            total_rows = len(data) + len(result)
            if limit and total_rows > limit:
                remainder = len(data) - (total_rows - limit)
                result += data[0:remainder]
                break
            else:
                result += data

        return result

    def get_meta(self, path, filters=()):
        filters = FilterList(filters)
        query = Query()
        query.add_auth(self.api_key, digest(
            self.api_secret, filters.message()))
        query.add_str(filters)

        url = self.api_endpoint + '/' + path + '?' + str(query)
        response = requests.get(url)
        return response.json().get('meta', {})

    def get_mention_sources(self, filters=(), page_size=100, order=None, limit=None):
        return self.get('research_outputs/mention_sources', filters, page_size, order, limit)

    def get_mention_sources_meta_response(self, filters=()):
        return self.get_meta('research_outputs/mention_sources', filters).get('response', None)

    def get_mentions(self, filters=(), page_size=100, order=None, limit=None):
        return self.get('research_outputs/mentions', filters, page_size, order, limit)

    def get_mentions_meta_response(self, filters=()):
        return self.get_meta('research_outputs/mentions', filters).get('response', None)
