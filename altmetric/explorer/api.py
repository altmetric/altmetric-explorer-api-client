import base64
from itertools import groupby
import hmac
import hashlib

import requests


def all_pages(url):
    '''Returns a generator that lazily yields all the pages returned by a
    request to the Explorer API.  The next page is found by looking for
    the links.next key in an API response.  If the key is found then
    the current page will be yielded by and the next page URL will be cached
    for the next time the generator is called.  Otherwise the page will be yielded
    and the generator will close.
    '''
    while url:
        response = requests.get(url)
        if response.status_code != requests.codes.ok:
            raise Exception(f'{url} returned {response.status_code}')

        page = response.json()
        url = page.get('links', {}).get('next', None)

        yield page


def digest(secret, message):
    '''Calculates a cryptographic digest based on the user's API secret key and
    the values of some of the parameters as described here:

    https://www.altmetric.com/explorer/documentation/api#authentication
    '''
    if message is None:
        message = ''
    hmac_sha1 = hmac.new(secret.encode('utf-8'),
                         message.encode('utf-8'), hashlib.sha1)
    signature = base64.b64encode(hmac_sha1.digest()).decode('utf-8')
    signature = hmac_sha1.hexdigest()
    return signature


class Filters:
    def __init__(self):
        self.items = []

    def add_filter(self, arg, value):
        self.items.append((arg, value))
        return self

    def __len__(self):
        return len(self.items)

    def message(self):
        result = []
        for arg, value in sorted(self.items):
            result.append(arg)
            if type(value) in (list, tuple, set):
                for val in value:
                    result.append(val)
            else:
                result.append(value)
        return '|'.join(result)

    def __str__(self):
        result = []
        for arg, value in self.items:
            if type(value) == list or type(value) == tuple:
                for val in value:
                    result.append(f'filter[{arg}][]={val}')
            else:
                result.append(f'filter[{arg}]={value}')
        return '&'.join(result)


class Query:
    '''Builder class that builds up a list of parameters to be passed to an
    API endpoint and generates a URL query string'''

    def __init__(self, **kvargs):
        '''Initialise a Query with an initial set of params'''
        self.items = []
        self.filters = Filters()
        self.add_params(**kvargs)

    def add_params(self, **kvargs):
        """Add parameter(s) to the query

        Returns:
            Query: self
        """
        for arg, value in kvargs.items():
            match arg:
                case 'page_size':
                    self.items.append(f'page[size]={value}')
                case 'page_number':
                    self.items.append(f'page[number]={value}')
                case 'order':
                    self.items.append(f'filter[order]={value}')
                case ('key' | 'digest'):
                    self.items.append(f'{arg}={value}')
                case _:
                    self.filters.add_filter(arg, value)
        return self

    def add_auth(self, api_key, digest):
        """Add authorisation fields the query

        Args:
            api_key (string): public API key (NOT the secret)
            digest (string): digest calculated using the filters and the secret key

        Returns:
            Query: self
        """
        return self.add_params(key=api_key, digest=digest)

    def add_str(self, item):
        """Add an arbitrary item to the query in the form `param=value`

        Args:
            item (Object): any object that responds to __str__ and returns a valid query string

        Returns:
            Query: self
        """
        self.items.append(str(item))
        return self

    def __str__(self):
        """Compile a URL query string from the items provided to the builder methods.

        Returns:
            string: the URL query string

        Notes:
            The string created is not URL encoded
        """
        result = []

        if self.items:
            result.append("&".join(self.items))

        if self.filters:
            result.append(str(self.filters))

        return '&'.join(result)


class Client:
    """Top level abstraction over the Altmetric Explorer API.
    """

    def __init__(self, api_endpoint, api_key, api_secret):
        """Initialises a new Client object

        Args:
            api_endpoint (string): the url of the explorer api (usually https://www.altmetric.com/explorer/api)
            api_key (string): your explorer api key
            api_secret (string): your explorer api secret key

        Raises:
            ValueError: if the api key or the api secret is None

        Notes:
            You can find your api key and secret at https://www.altmetric.com/explorer/settings
        """
        if api_key == None or api_secret == None:
            raise ValueError('api_key and api_secret cannot be None')

        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.api_secret = api_secret

    def get(self, path, **args):
        """Generic get method that constructs a call to an API path and returns the data returned. An authentication digest is calculated behind the scenes using the
        api keys instance variables and the filters provided and added to the request automatically.

        Args:
            path (string): the path to query
            filters (tuple, optional): tuple containing filters. Defaults to ().
            page_size (int, optional): size of each page to be returned. Defaults to 100.
            order (string, optional): the field on which the results should be sorted. Defaults to None.
            limit (int, optional): maximum number of items to return.  Set to None to return everything. Defaults to None.

        Returns:
            data: contents of the `data` keys from all the pages returned or up to
            the number of items specified by the `limit` parameter.

        TODO:
            This design sucks.  The idea of returning everything was all we needed for the Jupyter notebooks that this
            class grew out of but defaulting to returning everything is a really bad idea in the long term - especially
            when we already get the results as a (lazy) generator from the `all_pages` function.

            Adding the `limit` parameter is a bit of a workaround but it is artificial and adds extra responsibilities
            to this class.

            It would be much better to return response object that includes the `meta` object from the
            first page and a generator that yields `data` objects lazily so that the caller can decide how much to pull
            back.
        """
        limit = args.pop('limit', None)
        query = Query(**args)
        query.add_auth(self.api_key,
                       digest(self.api_secret, query.filters.message()))

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
        """
        The `meta` tag sometimes includes useful information like the number of
        rows returned by the query.

        TODO: This method was a quick and dirty way of exposing the `meta` data
        but it should be replaced by a proper response object as described in
        the doc string for `get` above.
        """
        filters = FilterList(filters)
        query = Query()
        query.add_auth(self.api_key, digest(
            self.api_secret, filters.message()))
        query.add_str(filters)

        url = self.api_endpoint + '/' + path + '?' + str(query)
        response = requests.get(url)
        return response.json().get('meta', {})

    def get_mention_sources(self, **args):
        '''
        Shorthand accessor for 'research_outputs/mention_sources'

        TODO: passing the parameters explicitly here is ugly and verbose.  DRY this up somehow.
        '''
        return self.get('research_outputs/mention_sources', **args)

    def get_mention_sources_meta_response(self, filters=()):
        '''
        Shorthand accessor for the meta data from 'research_outputs/mention_sources'

        TODO: Make `get` return a response object and add a `meta` method to it as described
        above so we can delete this method.
        '''

        return self.get_meta('research_outputs/mention_sources', filters).get('response', None)

    def get_mentions(self, **args):
        '''
        Shorthand accessor for 'research_outputs/mentions'

        TODO: passing the parameters explicitly here is ugly and verbose.  DRY this up somehow.
        '''
        return self.get('research_outputs/mentions', **args)

    def get_mentions_meta_response(self, filters=()):
        '''
        Shorthand accessor for the meta data from 'research_outputs/mentions'

        TODO: Make `get` return a response object and add a `meta` method to it as described
        above so we can delete this method.
        '''
        return self.get_meta('research_outputs/mentions', filters).get('response', None)
