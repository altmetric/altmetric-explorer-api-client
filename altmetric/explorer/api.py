import base64
import hashlib
import hmac
import itertools

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
    '''Holds a list of filters and provides accessors to the authentication message string as well
       as the query string itself.'''
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

class Response:
    """The response object that holds onto the meta data and data iterator
    """

    def __init__(self, all_pages):
        self.data_iterator, self.meta_iterator = itertools.tee(all_pages)
        self.first_page = next(self.meta_iterator)

    def data(self):
        for page in self.data_iterator:
            for row in page.get('data'):
                yield row

    def meta(self):
        return self.first_page["meta"]["response"]


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
        """Generic get method that constructs a call to an API path and returns a Response. An authentication digest is calculated behind the scenes using the
        api keys instance variables and the filters provided and added to the request automatically.

        Args:
            path (string): the path to query
            args (keyword list, accepts the following):
                page_size (int, optional): size of each page to be returned. Defaults to 100.
                order (string, optional): the field on which the results should be sorted. Defaults to None.
                limit (int, optional): maximum number of items to return.  Set to None to return everything. Defaults to None.
                All other keyword arguments are treated as filters e.g. timeframe, mention_sources_countries

        Returns:
            response: A Response object for the API call.
        """
        query = Query(**args)
        query.add_auth(self.api_key,
                       digest(self.api_secret, query.filters.message()))
        url = self.api_endpoint + '/' + path + '?' + str(query)

        return Response(all_pages(url))

    def get_mention_sources(self, **args):
        '''
        Shorthand accessor for 'research_outputs/mention_sources'
        '''
        return self.get('research_outputs/mention_sources', **args)

    def get_mentions(self, **args):
        '''
        Shorthand accessor for 'research_outputs/mentions'

        '''
        return self.get('research_outputs/mentions', **args)
